# N162 · JavaScript 函数组合、缓存与事件 —— 说人话详解

> 对应 notebook：`notebooks/19_specialized_tracks/162_javascript_functional_events.ipynb`

## 一、这章要解决什么问题？（问题描述）

这一章不讲新算法，讲的是四个"工具函数怎么设计"的问题，它们正好对应 LeetCode 的四道函数式编程题。你可以把本章看成四个小设计题：

1. **map**：给你一个数组和一个回调，你要返回新数组，每个元素是回调处理后的结果，而且回调要能同时拿到"值和下标"。例如输入 `[2,3]` 和 `(x,i)=>x+i`，输出 `[2,4]`，因为 `2+0=2`、`3+1=4`（第一个元素下标是 0，第二个是 1）。
2. **compose**：给你一组函数，你要把它们串成一个函数。规定从右往左执行，即 `compose([f,g])(x)=f(g(x))`。例如 `compose([x=>x+1, x=>x*2])(3)`：先执行最右边的 `x*2` 得 6，再执行 `x+1` 得 7，所以输出 7。
3. **memoize**：给你一个纯函数，你要返回一个"带缓存"的版本——同样的参数第二次调用不再重算。例如一个统计调用次数的函数，`cached(1)` 调两次，真正的计算只发生 1 次。
4. **EventEmitter**：你要实现"订阅—触发—取消订阅"。同一个事件名下可以挂多个监听器，`emit` 时按订阅顺序全部调用一遍。例如 `'x'` 事件挂了 `v=>v+1` 和 `v=>v*2` 两个监听器，`emit('x',[3])` 返回 `[4,6]`；退订第一个之后再 emit，返回 `[6]`。

这四个问题共同的主题是：**函数也是值，订阅关系也有生命周期**——我们需要精确地定义"什么算一次订阅""什么算一次缓存命中"。

## 二、关键概念（定义）

- **回调函数（callback）**：你传给别人、由别人在合适时机调用的函数。`map(arr, fn)` 里的 `fn` 就是回调，它由 `map` 在遍历时调用。
- **纯函数（pure function）**：输出只由输入决定、且不产生副作用的函数。memoize 的契约就是"只对纯函数有效"——如果函数还依赖外部可变状态，缓存就会返回过期答案。
- **map/filter/reduce**：函数式三件套。map 逐个变换，filter 按条件筛选，reduce 把列表折叠成一个值。本章只实现 map 这一个。
- **函数组合（compose）**：把 `[f,g]` 变成一个新函数 `x => f(g(x))`。方向约定为从右向左，和数学里的复合记号 `(f∘g)(x)=f(g(x))` 一致。空数组组合出来的函数就是恒等函数，输入什么返回什么。
- **memoization（记忆化）**：第一次算出结果后把"参数 → 结果"存起来，下次同样参数直接查表。核心问题是"拿什么当键"。
- **缓存键（cache key）**：识别"是不是同一组参数"的依据。如果用 `JSON.stringify(args)` 当键，`1`（数字）和 `'1'`（字符串）会被混成一个键，两个不同对象 `{x:1}` 也会撞键。本章改用 `Map` 嵌套（参数前缀树），键按对象身份区分，`Map` 允许任意类型的键（包括对象和 `undefined`）。
- **ready 标记**：缓存节点上的一个布尔值，用来区分"这个节点还没算过"和"算过了，结果是 undefined"。没有它，"结果恰为 undefined"和"没缓存"就无法区分。
- **订阅注册对象（item）**：每次 `subscribe` 都新建一个 `{callback}` 对象塞进列表。同一个回调函数注册两次，就是两个不同的 item，也就是两次独立订阅，退订一个不影响另一个。
- **快照（snapshot）语义**：`emit` 一开始就把当前订阅列表复制一份，本次触发只遍历这份副本；触发过程中新加或退订的监听器，从下一次 emit 才生效。这样能保证"每个注册对象在一次 emit 中恰好被调用一次"。
- **幂等退订**：`unsubscribe` 调两次不会报错也不会重复删除——第一次把它标记为 inactive，第二次直接 return。

## 三、解决思路（一步步推导）

我们按四个接口依次推导。

**Step 1：map 就是"新建数组 + 循环调用回调"。** 不要修改原数组（`out` 是新数组），并且把下标 `i` 一起传给回调，因为契约要求"值和索引"。本章只考虑稠密数组，不存在空洞元素。

**Step 2：compose 就是"从最后一个函数开始，把 x 反复喂进去"。** `for` 循环从 `functions.length-1` 倒着走到 0，每轮 `x = functions[i](x)`。数组为空时循环一次都不执行，直接返回原值 `x`，天然满足"空组合保持输入"。

**Step 3：memoize 用"参数前缀树"做键。** 与其把参数拼成字符串，不如让每个参数成为树的一层边：第一个参数查第一层 Map，第二个参数查第二层 Map……走到头就是缓存节点。我们手算一遍 notebook 测试里的调用序列（初始 `calls=0`）：

| 调用 | 走的路径 | 是否命中 | calls 变成 |
|---|---|---|---|
| `cached(1)` | root →1 | 未命中，算出 1 | 1 |
| `cached(1)` | root →1 | 命中 | 1 |
| `cached(1,undefined)` | root →1→undefined | 未命中，参数个数 2 | 2 |
| `cached('1')` | root →'1'（字符串键，和数字 1 不同） | 未命中 | 3 |
| `cached(obj)` | root →obj（按对象身份） | 未命中 | 4 |
| `cached(obj)` | root →obj | 命中 | 4 |
| `cached({x:1})` | root →新对象（身份不同） | 未命中 | 5 |

最终 `calls=5`——这正是 cell8 断言的数字。注意 `cached(1)` 和 `cached(1,undefined)` 结果不同（1 对 2），说明"参数个数"本身也是键的一部分，靠终止节点天然区分。而返回 undefined 的函数第二次调用时 `undefinedCalls` 仍是 1，靠的就是 ready 标记。

**Step 4：EventEmitter 用"注册对象数组"管理订阅。** 手算 cell6 的小实例：`a=subscribe('x', v=>v+1)`，`b=subscribe('x', v=>v*2)`，此时 `'x'` 的列表是 `[a项, b项]`。`emit('x',[3])`：拍快照 `[a项, b项]`，依次调用得 `[3+1, 3*2] = [4,6]`。然后 `a.unsubscribe()` 把 a 项从列表删掉（列表只剩 `[b项]`），再 `emit('x',[3])` 得 `[6]`。cell6 的表格记录的就是这两行：`two listeners → [4,6]`、`after unsubscribe → [6]`。

**Step 5：快照解决"触发中改列表"的边界。** 测试里第一个监听器在回调中退订了第二个监听器。第一次 emit 因为拍的是快照，第二个仍然被调用，返回 `[1,2]`；第二次 emit 列表里只剩第一个，返回 `[1]`。这就是"本次触发期间的增删从下一次生效"。

## 四、代码逐段讲解

cell3 的主体是一段 JavaScript 源码（存进 `JS_SOURCE` 字符串，由 Python 的 `run_js` 用 `node -e` 执行）。我们逐个函数看。

**map：**

```javascript
function map(arr, fn) {
  const out=[];
  for (let i=0;i<arr.length;i++) out.push(fn(arr[i],i));
  return out;
}
```

第 2 行新建空数组 `out`，保证不改动原数组。第 3 行遍历，`fn(arr[i],i)` 把值和下标一起传给回调——契约要求的正是这一点。最后返回 `out`。

**compose：**

```javascript
function compose(functions) {
  return function(x) {
    for (let i=functions.length-1;i>=0;i--) x=functions[i](x);
    return x;
  };
}
```

返回的是一个闭包。循环下标从 `functions.length-1` 递减到 0，即从数组最右（最后写的）函数先执行，实现 `f(g(x))` 的从右向左语义。空数组时循环不执行，`x` 原样返回，恒等函数不需要特判。

**memoize：**

```javascript
function memoize(fn) {
  // Contract: pure function of positional arguments; object keys use identity.
  const node=()=>({children:new Map(), ready:false, value:undefined});
  const root=node();
  return function(...args) {
    let current=root;
    for (const arg of args) {
      if (!current.children.has(arg)) current.children.set(arg,node());
      current=current.children.get(arg);
    }
    if (!current.ready) {
      current.value=fn(...args);
      current.ready=true;
    }
    return current.value;
  };
}
```

`node` 是节点工厂：每个节点有 `children`（下一层参数的 Map）、`ready`（算过没有）、`value`（结果）。返回的函数里，`for...of` 沿参数逐层下钻，缺边就现建一个节点；走完参数序列后落在终止节点上。`if (!current.ready)` 只在第一次执行真正的 `fn(...args)`，之后永远直接返回 `current.value`。注释明确了契约：纯函数、按位置参数、对象键按身份。这就是说 `cached(1)`、`cached('1')`、`cached(1,undefined)` 会落在三个不同节点。

**EventEmitter：**

```javascript
class EventEmitter {
  constructor() { this.events=new Map(); }
  subscribe(eventName,callback) {
    const item={callback};
    if (!this.events.has(eventName)) this.events.set(eventName,[]);
    this.events.get(eventName).push(item);
    let active=true;
    return {unsubscribe:()=>{
      if (!active) return;
      active=false;
      const items=this.events.get(eventName);
      const index=items.indexOf(item);
      if (index>=0) items.splice(index,1);
      if (items.length===0) this.events.delete(eventName);
    }};
  }
  emit(eventName,args=[]) {
    // Snapshot semantics: subscriptions changed during emission apply next time.
    const snapshot=[...(this.events.get(eventName)||[])];
    return snapshot.map(item=>item.callback(...args));
  }
}
```

`events` 是"事件名 → 订阅列表"的 Map。`subscribe` 每次都新建 `item={callback}`——这是关键设计：识别订阅靠 item 的对象身份，不靠回调函数本身，所以同一个函数注册两次就是两条订阅。`let active=true` 加闭包实现幂等退订：第二次调用 `unsubscribe` 时 `active` 已是 false，直接 return；删除用 `indexOf` 找到自己的 item 再 `splice`，只删这一条；列表空了就把整个事件名从 Map 里删掉，不留垃圾。`emit` 里 `[...(this.events.get(eventName)||[])]` 先拍快照（事件不存在时空数组兜底），再对快照逐个调用并收集返回值——注释再次强调快照语义。

## 五、为什么是对的？复杂度是多少？（说人话）

**正确性：** memoize 这边，一组参数唯一决定树上一条从根到终止节点的路径，所以"同参数必命中同一节点"；ready 标记保证"没算过"与"算出 undefined"是两种状态，不会把后者误判成前者。EventEmitter 这边，快照保证了 emit 期间列表不变，因此每个注册对象在一次触发中恰好被调用一次、顺序就是订阅顺序；退订只删自己的 item，不会误伤别的订阅。

**复杂度：** map 对 n 个元素是 O(n)；compose 对 k 个函数是 O(k)。memoize 一次访问要下钻 a 层（a 是参数个数），期望 O(a)；空间随"出现过的不同参数前缀"数量增长。emit 触发 m 个订阅是 O(m)；退订要在长度 m 的列表里 `indexOf`，也是 O(m)——本章选数组是为了保序，代价是退订线性。

## 六、测试用例在测什么

cell8 的断言逐条对应契约（均在 Node 里跑，`node:assert/strict`）：

- `map([2,3],(x,i)=>x+i)` 等于 `[2,4]`：正常值，验证"值+下标"都传对了（2+0=2、3+1=4）。
- `map([],x=>x)` 等于 `[]`：空数组边界，循环零次直接返回空数组。
- `compose([])(7)` 等于 7：空组合的边界，恒等函数。
- `compose([x=>x+1,x=>x*2])(3)` 等于 7：正常值，验证从右向左（先 *2 后 +1，得 7 而不是 4）。
- `cached(1)` 两次后 `calls===1`：缓存命中，第二次没重算。
- `cached(1,undefined)` 返回 2、`cached('1')` 返回 1：特殊值，证明"参数个数"和"数字 1 与字符串 '1'"都区分了。
- `cached(obj)`、`cached(obj)`、`cached({x:1})` 后 `calls===5`：对象身份键——同一个对象第二次命中，内容相同的新对象不命中。
- `missing()` 两次后 `undefinedCalls===1`：返回 undefined 的函数也能被正确缓存（ready 标记的功劳）。
- `e.emit('absent')` 等于 `[]`：没人订阅的事件不报错，返回空结果。
- 同一个 `cb` 注册两次后 `emit('x',[2])` 等于 `[3,3]`：同一函数两次注册是两条独立订阅，各调一次。
- `a.unsubscribe()` 连调两次后再 emit 得 `[3]`：幂等退订，重复退订不炸、不误删 b。
- `b.unsubscribe()` 后 emit 得 `[]`：全部退订后事件安静。
- 快照语义：第一个监听器在回调里退订第二个，第一次 emit 返回 `[1,2]`（快照里两个都在），第二次返回 `[1]`。

## 七、练习思路提示

**练习 1（JSON 文本键 vs 对象身份键）：** 建议你写两版 memoize，一版用 `JSON.stringify(args)` 当键存进普通对象，一版复用本章的前缀树。然后拿三类输入去打它们：`cached(1)` 对 `cached('1')`（JSON 后都是 `"1"`，会撞键）；`cached({x:1})` 两次（JSON 相同但身份不同，字符串版会错误命中）；`cached(1,undefined)` 对 `cached(1)`（一个参数的 `undefined` 直接被 stringify 丢掉）。手算表格可以照第三节的样式画。

**练习 2（实现 unsubscribe）：** notebook 其实已经给了参考实现，练习的意义是你自己推一遍边界。提示：要处理的边界有三个——重复退订（需要 active 标记）、退订一个从未存在的事件、退订后列表为空要不要清理事件名。再想一步：为什么删除目标必须是 `item` 这个注册对象，而不能按回调函数去找？（答案和"同一函数可注册多次"有关。）

## 八、对应 LeetCode 题目

- **2635. Apply Transform Over Each Element in Array**：练的是本章的 `map`，题面就是"给每个元素做变换、回调带下标"。
- **2629. Function Composition**：练的是 `compose`，验证从右向左执行和空数组恒等这两个约定。
- **2623. Memoize**：练的是 `memoize`，官方测试会专门区分 `1`/`'1'`、对象身份和 undefined 结果，和本章缓存键设计一一对应。
- **2694. Event Emitter**：练的是 `subscribe/emit/unsubscribe` 全套生命周期，包括同函数多次订阅和 emit 期间退订的快照语义。
