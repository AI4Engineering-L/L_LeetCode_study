# N163 · JavaScript 异步、定时器与并发限制 —— 说人话详解

> 对应 notebook：`notebooks/19_specialized_tracks/163_javascript_promises_timers.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章解决四个 JavaScript 异步编程的常见需求，它们都对应 LeetCode 的异步题：

1. **promiseAll**：同时启动 m 个异步函数，等它们全部完成后，按"输入顺序"返回结果数组。难点在于完成顺序和输入顺序往往不同——输入 `[3ms 任务, 1ms 任务, 2ms 任务]`，完成顺序是 1ms、2ms、3ms，但返回必须是 `[结果0, 结果1, 结果2]`，谁先完成不影响谁排在哪。
2. **timeLimit**：给任何异步函数加一个限时 t 毫秒的包装，超时就拒绝（reject `'Time Limit Exceeded'`）。例如一个 15ms 才完成的函数 `slow`，用 `timeLimit(slow, 1)()` 调用，1ms 时你就收到拒绝；但注意底层任务并没有被杀死，15ms 时它照样跑完——"超时"只影响调用者什么时候拿到拒绝，不等于"取消"。
3. **debounce**：疯狂连续调用时只执行最后一次。输入：1ms 内连调三次 `realDeb(1); realDeb(2); realDeb(3)`，输出：只有一次执行，参数是 3（测试断言 `values===[3]`）。
4. **promisePool**：m 个任务最多允许 n 个同时跑。输入 12 个任务、n=3，输出是全部 12 个结果（按输入顺序），且测试记录到任意时刻活跃任务数从没超过 3。

四个问题合起来的主题是：**异步结果怎么按"身份"归位、时间怎么可控、并发怎么限量、错误怎么传播**。

## 二、关键概念（定义）

- **Promise**：一个"未来才会有结果"的对象。成功叫 resolve，失败叫 reject；`.then(onOk, onErr)` 分别挂两条路径的处理。
- **async/await**：让异步代码看起来像同步的语法糖。`await p` 会暂停当前函数、让出控制权，p 落定后继续；`async` 函数总是返回 Promise。
- **微任务（microtask）**：Promise 回调排队的队列，比定时器先执行。本章用 `Promise.resolve().then(fn)` 保证 `fn` 以异步方式启动（而不是在注册当场同步执行）。
- **竞速（race）与结果归位**：多个 Promise 同时跑，谁先完成不确定；解决办法是启动时分配下标 i，完成时写 `out[i]`——位置由输入决定，与完成时间无关。
- **计时器句柄与清理**：`setTimeout` 返回句柄，`clearTimeout(句柄)` 取消。成功和失败两条路径都必须 `clearTimeout`，否则留下"已无用却仍存活"的定时器（测试用 `activeTimers.size===0` 检查这一点）。
- **超时 ≠ 取消**：拒绝只是"告诉调用者别等了"，底层函数该跑还是跑。想真取消需要任务自己支持中断，这超出本章接口。
- **debounce（防抖）**：每次调用都取消上一个还没到期的定时器、重设一个新的，所以只有"最后一次"参数和 this（`receiver`）会被真正使用。持续等待的定时器至多一个。
- **可注入时钟（clock）**：把 `setTimeout/clearTimeout` 作为参数传入而不是直接用全局的，这样测试可以提供一个假时钟，手动"拨表"推进时间，避免依赖真实毫秒的脆弱断言。
- **并发池（pool）与 worker**：固定 n 个 worker 循环"领任务—做任务"，每个 worker 同一时刻只占一个任务，所以同时活跃的任务至多 n 个。
- **错误传播策略**：池子遇到第一个错误就"停止领新任务"，但已经开始的任务要等它收尾，最后把首个错误抛出——既不吞错，也不丢已启动任务的副作用。

## 三、解决思路（一步步推导）

**Step 1：promiseAll 的核心是"下标即位置"。** 启动时建 `out=new Array(m)` 和计数器 `remaining=m`；每个任务完成时 `out[i]=value` 并把 `remaining` 减 1，减到 0 才 resolve。空数组要特判直接 resolve（否则计数器永远到不了 0）。

**Step 2：timeLimit 是"两个 Promise 谁先说话听谁"。** 一个定时器 Promise 在 t 毫秒后 reject；原函数照常执行，成功或失败都要先 `clearTimeout` 再 resolve/reject。注意成功、失败两条路径都要清理计时器。

**Step 3：debounce 是"每来一次新调用就重置闹钟"。** 用假时钟手算 cell8 的用例（延迟 10）：

| 时刻 | 动作 | 定时器状态 | seen |
|---|---|---|---|
| t=0 | `deb.call({prefix:'a'},1)` | 闹钟定在 t=10 | [] |
| 推进 9 → t=9 | 无事发生 | 还差 1 | [] |
| t=9 | `deb.call({prefix:'b'},2)` | 取消旧闹钟，新闹钟定在 t=19 | [] |
| 推进 9 → t=18 | 无事发生 | 还差 1 | [] |
| 推进 1 → t=19 | 闹钟响，用保存的 this=`{prefix:'b'}` 和参数 2 执行 | 清空 | ['b2'] |
| t=19 | `deb(3)` 后立即 `deb.cancel()` | 定时器被取消 | ['b2'] |
| 推进 20 | 无事发生 | 空 | ['b2']（断言 clock.size()===0） |

**Step 4：promisePool 用"领号机"分配任务。** 共享变量 `next` 是下一个待领下标。worker 的循环体是：检查未失败且 `next<len` → `const index=next++` → `await` 任务 → 存 `out[index]`。关键在"取下标和递增 next 之间没有 await"，所以两个 worker 绝不会领到同一个任务。手算 cell6 的小实例（任务时长 `[3ms,1ms,2ms]`，n=2）的时间线：

```
t=0   workerA 领任务0（active=1）  workerB 领任务1（active=2）  next=2
t=1   任务1完成（active=1），workerB 立刻领任务2（active=2）
t=3   任务0 完成、任务2 完成（都定在 t=3，先后看调度），active 归 0
结果  out=[0,1,2] —— 按输入顺序，和完成顺序（1→2→0）无关
```

cell6 的表格记录的正是这条轨迹（start/finish 事件与 active 计数），最后 `result` 一行是 `[0,1,2]`。

**Step 5：错误传播手算。** 输入 `[立即抛错, 延时2ms返回1, 返回2]`、n=2：两个 worker 分别领任务 0 和 1（`starts=2`）；任务 0 抛错，记下 `firstError` 并置 `failed=true`；任务 1 照常做完收尾；worker 循环看到 `failed` 不再领任务 2（所以 `starts` 停在 2）；两个 worker 都结束后，池子抛出 `boom`。测试断言 `starts===2` 验证的正是"停止领新任务，但不丢已启动的"。

## 四、代码逐段讲解

cell3 主体是 `JS_SOURCE` 里的 JavaScript（Python 的 `run_js` 负责交给 node 执行）。逐个函数讲。

**promiseAll：**

```javascript
function promiseAll(functions) {
  return new Promise((resolve,reject)=>{
    const out=new Array(functions.length);
    if (functions.length===0) { resolve(out);return; }
    let remaining=functions.length;
    functions.forEach((fn,i)=>{
      Promise.resolve().then(fn).then(value=>{
        out[i]=value;
        if (--remaining===0) resolve(out);
      },reject);
    });
  });
}
```

`out` 按输入长度开槽位。空数组立即 resolve 空数组并 return。`Promise.resolve().then(fn)` 保证 `fn` 在微任务里启动（统一异步语义）；成功回调把结果写回自己的下标槽位 `out[i]=value`，并把 `remaining` 减 1，减到 0 说明最后一个也到了，此时 `out` 已填满，整体 resolve。第二个参数直接传 `reject`：任何一个失败，整体立刻以同一个错误拒绝。

**timeLimit：**

```javascript
function timeLimit(fn,t,clock=globalThis) {
  return function(...args) {
    const receiver=this;
    return new Promise((resolve,reject)=>{
      const timer=clock.setTimeout(()=>reject('Time Limit Exceeded'),t);
      Promise.resolve().then(()=>fn.apply(receiver,args)).then(
        value=>{clock.clearTimeout(timer);resolve(value);},
        error=>{clock.clearTimeout(timer);reject(error);});
    });
  };
}
```

`clock=globalThis` 让默认用真实全局定时器、测试时可注入假时钟。`receiver=this` 先存下来，再用 `fn.apply(receiver,args)` 调用，保住 this 绑定。定时器先挂上，t 毫秒后 reject 字符串 `'Time Limit Exceeded'`（LeetCode 的约定文案）。原函数的成功、失败两个分支都先 `clock.clearTimeout(timer)` 再往下走——这就是"两条路径都清理计时器"。

**debounce：**

```javascript
function debounce(fn,t,clock=globalThis) {
  let timer=null;
  function debounced(...args) {
    if (timer!==null) clock.clearTimeout(timer);
    const receiver=this;
    timer=clock.setTimeout(()=>{timer=null;fn.apply(receiver,args);},t);
  }
  debounced.cancel=()=>{
    if (timer!==null) clock.clearTimeout(timer);
    timer=null;
  };
  return debounced;
}
```

闭包变量 `timer` 至多持有一个待执行定时器：每次调用先取消上一个（`if (timer!==null)`），再把 this 和最新参数封进新的定时器回调——所以最终执行的是"最后一次"的 this 和参数。回调开头 `timer=null` 把句柄清空，避免留下指向已触发定时器的旧句柄。`debounced.cancel` 是附加上去的取消方法，把还挂着的定时器撤掉。

**promisePool：**

```javascript
async function promisePool(functions,n) {
  if (!Number.isInteger(n)||n<1) throw new RangeError('Positive concurrency required');
  const out=new Array(functions.length);
  let next=0,failed=false,firstError;
  async function worker() {
    while (!failed && next<functions.length) {
      const index=next++;
      try { out[index]=await functions[index](); }
      catch (error) { if (!failed) firstError=error; failed=true; }
    }
  }
  await promiseAll(Array.from({length:Math.min(n,functions.length)},()=>worker));
  if (failed) throw firstError;
  return out;
}
```

第一行防御：n 必须是正整数（测试里 `promisePool([],0)` 因此抛 RangeError）。`next` 是领号机，`failed/firstError` 记录首个错误。worker 的 while 条件先看 `failed`：出错后不再领新任务。`const index=next++` 这一行没有 await，取号是原子的。`try/catch` 把错误吞进 `failed/firstError`，让 worker 能正常退出循环而不是异常炸掉。`Math.min(n,functions.length)` 避免任务比 worker 还少时开多余的 worker（它们第一轮循环就退出了）。最后复用本章的 promiseAll 等所有 worker 收尾，再决定是否抛 `firstError`，成功则返回按输入顺序的 `out`。

## 五、为什么是对的？复杂度是多少？（说人话）

**正确性：** 结果归位靠下标，与完成时间无关，所以怎么交错 `out` 都按输入顺序填满；`remaining` 归零当且仅当每个槽位都填过。池子这边，"取下标与递增 next 之间无 await"保证不重号；一个 worker 做完当前任务才领下一个，所以同时活跃任务至多 n。debounce 每次调用前先取消旧定时器，因此待执行定时器至多一个，语义就是"只执行最后一次"。timeLimit 的正确性要分两层说：调用者层——t 毫秒内没结果就收到拒绝；资源层——底层任务并未取消，它会继续跑完，只是结果没人再消费。cell4 特意强调这两层必须分开讨论，不能混为一谈。

**复杂度：** 忽略任务本身耗时，promiseAll 的调度开销 O(m)，结果数组 O(m)；池子额外只有 O(min(n,m)) 个活跃 worker。debounce 每次调用的额外状态 O(1)（一个句柄加一个闭包）。另外 cell4 明确说：定时器相关测试不用"真实墙钟 + 毫秒阈值"来证明性能，因为那种断言既慢又不稳定；本章用假时钟做确定性验证、用句柄计数检查泄漏。

## 六、测试用例在测什么

cell8 分两段：先用 `fakeClock` 测 debounce，再包裹真实 `setTimeout` 跑其余接口（`activeTimers` 集合记录所有挂着的真实定时器，结束必须清零）。

- 假时钟部分的 5 条断言：对应第三节那张手算表——两次 `advance(9)` 后都还没执行（验证"重置闹钟"）、`advance(1)` 后执行的是 `'b2'`（验证最后一次的 this 和参数）、`clock.size()===0`（定时器不泄漏）、`cancel()` 后推进 20 也不执行（正常值+边界一起测）。
- `promiseAll([])` 得 `[]`：空输入边界。
- `promiseAll([延时5ms返回1, 立即返回2])` 得 `[1,2]`：正常值，验证按输入顺序归位（先完成的排后面）。
- `promiseAll([()=>{throw boom;}])` 以同一个 `boom` 拒绝：异常就是原样传播，不包装。
- `timeLimit(async x=>x+1,100)(2)` 得 3：限时内成功，this/参数透传正常。
- `timeLimit(抛 boom 的函数,100)()` 以 `boom` 拒绝：业务错误优先于超时逻辑，不串味。
- `timeLimit(slow,1)()` 以 `'Time Limit Exceeded'` 拒绝、且 `underlyingFinished` 最终落定：这条就是"超时≠取消"的直接证据——调用者 1ms 拿到拒绝，底层 15ms 照样跑完。
- 12 个任务、n=3 的池：结果等于 `[0,1,4,...,121]`（i 的平方）、`maximum<=3`（并发从没超限）、`active===0`（全部收尾）。接着 `await Promise.resolve()` 让包装器的完成处理器有机会清掉它那个已触发的定时器（注释里解释了这个微妙的次序）。
- 错误传播：任务 0 抛错、n=2 的池以 `boom` 拒绝且 `starts===2`：第三个任务没被启动，已启动的收了尾。
- `promisePool([],2)` 得 `[]`（空任务边界）、`promisePool([],0)` 抛 RangeError（非法参数边界）。
- 真实定时器的 debounce（t=1）：连调 1、2、3，最终 `values===[3]`：只执行最后一次。
- `activeTimers.size===0`：全程无定时器泄漏（finally 里恢复全局函数并清掉残余句柄）。

## 七、练习思路提示

**练习 1（解释超时拒绝不等于取消原任务）：** 提示：从"两条独立的因果链"入手——调用者链在 t 毫秒收到 reject，资源链继续执行到自然结束。设计一个能观察到这一点的实验：让底层任务在完成前打一个标记（就像测试里的 `underlyingFinished`），然后分别断言"1ms 时已被拒绝"和"稍后标记仍被置位"。再把问题推广一步：如果底层任务支持中断（比如接受 AbortSignal），包装器该怎么改？

**练习 2（用可控时钟测 debounce 边界）：** 提示：照 cell8 的 `fakeClock` 写一个迷你版本，核心只有三个方法——`setTimeout` 登记任务（记录触发时间）、`clearTimeout` 删除、`advance(delta)` 把到点的任务按"触发时间升序、同时间按登记序"逐个执行。然后专门测边界：推进 t-1 不执行、再推进 1 执行；连打两次重置后从最后一次起算 t。避免写 `await delay(50); assert(...)` 这种依赖真实墙钟的断言，因为它在慢机器上会抖。

## 八、对应 LeetCode 题目

- **2721. Execute Asynchronous Functions in Parallel**：练的是 `promiseAll` 的下标归位——完成顺序和输出顺序解耦。
- **2637. Promise Time Limit**：练的是 `timeLimit` 的超时拒绝、两条路径清理计时器，以及"超时不取消"的边界认知。
- **2627. Debounce**：练的是 `debounce` 的"重置闹钟 + 只执行最后一次参数"，官方还要求正确处理 this。
- **2636. Promise Pool（extension）**：练的是 `promisePool` 的领号机模式与首个错误传播策略（教学版额外返回按输入排序的结果数组，官方只要求完成信号）。
