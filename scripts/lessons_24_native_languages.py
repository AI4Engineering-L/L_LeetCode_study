"""Execute real Shell and JavaScript, never translated Python substitutes."""
from course_builder import add

SHELL_SOURCES = {
'word_frequency.sh': '''#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
awk '{ for (i=1;i<=NF;i++) count[$i]++ } END { for (word in count) print word, count[word] }' | sort -k2,2nr -k1,1
''',
'valid_phone_numbers.sh': '''#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
awk '/^([0-9][0-9][0-9]-|\\([0-9][0-9][0-9]\\) )[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]$/ { print }'
''',
 'transpose_file.sh': '''#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
awk 'NR==1 { width=NF }
     NF!=width { bad=1; exit 2 }
     { for (i=1;i<=NF;i++) cell[NR,i]=$i }
     END { if (bad) exit 2;
           for (i=1;i<=width;i++) {
             for (j=1;j<=NR;j++) printf "%s%s", cell[j,i], (j==NR ? "\\n" : " ")
           }
     }'
''',
 'tenth_line.sh': '''#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
sed -n '10p'
'''
}
SHELL_CODE = '''import os
import subprocess
import tempfile
from pathlib import Path

SHELL_SOURCES = ''' + repr(SHELL_SOURCES) + '''

def run_shell(name, text):
    """Execute the actual script on stdin in a temporary directory."""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / name
        path.write_text(SHELL_SOURCES[name], encoding='utf-8')
        result = subprocess.run(['bash', str(path)], input=text, text=True,
            capture_output=True, check=True, timeout=10,
            env={**os.environ, 'LC_ALL':'C'})
        return result.stdout
'''
add(160,
'''Shell 管道传递的是文本流，而不是 DataFrame。先固定输入语法：词由空白分隔且区分大小写；词频并列按 C locale 字典序；电话必须整行匹配；转置要求矩形空白分隔表。

四个脚本直接调用真实 `awk`、`sort`、`sed`。词频先用关联数组计数，再按次数逆序和词升序排序；电话加首尾锚点拒绝多余空格；转置先记录 `(行, 列)`；第十行无需读入 Python。

脚本从标准输入读取，便于管道组合。在文件式判题接口中用 `< file.txt` 重定向即可。矩形前提失败返回非零退出码，不能把错误数据当作空结果。''',
SHELL_CODE,
r'''from IPython.display import Code
for name in SHELL_SOURCES:
    display(Code(SHELL_SOURCES[name], language='bash'))
text = 'the day is sunny the the\nthe sunny is is\n'
show_table(['stage','text','lines'], [
 ['input',repr(text),len(text.splitlines())],
 ['frequency',repr(run_shell('word_frequency.sh',text)),len(run_shell('word_frequency.sh',text).splitlines())],
 ['transpose',repr(run_shell('transpose_file.sh','name age\nalice 21\nbob 23')),2]])
''',
r'''assert run_shell('word_frequency.sh','') == ''
assert run_shell('word_frequency.sh','b a b a c') == 'a 2\nb 2\nc 1\n'
phones = '987-123-4567\n(123) 456-7890\n123 456 7890\n987-123-4567 \n(12) 345-6789\n000-000-0000'
assert run_shell('valid_phone_numbers.sh',phones) == '987-123-4567\n(123) 456-7890\n000-000-0000\n'
assert run_shell('valid_phone_numbers.sh','bad') == ''
assert run_shell('transpose_file.sh','name age\nalice 21\nbob 23') == 'name alice bob\nage 21 23\n'
assert run_shell('transpose_file.sh','') == ''
assert run_shell('transpose_file.sh','only') == 'only\n'
try:
    run_shell('transpose_file.sh','a b\nc')
except subprocess.CalledProcessError as error:
    assert error.returncode == 2
else:
    raise AssertionError('Ragged table was accepted')
assert run_shell('tenth_line.sh','1\n2') == ''
lines = '\n'.join(map(str,range(1,12)))
assert run_shell('tenth_line.sh',lines).strip() == '10'
assert run_shell('tenth_line.sh','').strip() == ''
''',
'''计数不变量是已读前缀中每个词的出现次数。转置的第 i 个输出行，按原行序列出全部 `cell[j,i]`，因此与原矩阵第 i 列一一对应。正则锚点保证是完整合法电话，而不是字符串中存在合法片段。''',
'''词频 O(L+u log u)，L 为文本长度、u 为不同词数。电话与第十行线性扫描；转置存储全部 r×c 个字段，时间、空间均 O(rc)。''')

JS_RUNNER = '''
import json
import subprocess

def run_js(extra):
    result = subprocess.run(['node', '-e', JS_SOURCE + '\\n' + extra],
                            text=True, capture_output=True, check=True, timeout=20)
    return result.stdout
'''
def js_code(source):
    return "JS_SOURCE = r'''" + source + "'''\n" + JS_RUNNER

JS161 = ''''use strict';
function createHelloWorld() {
  return function (...args) { return 'Hello World'; };
}
function createCounter(n) {
  let current = n;
  return function () { return current++; };
}
function createCounterWithReset(init) {
  let current = init;
  return {
    increment() { return ++current; },
    decrement() { return --current; },
    reset() { current = init; return current; }
  };
}
'''
add(161,
'''闭包捕获的是词法环境中的绑定，不是调用时复制的常数。创建计数器只执行一次初始化，随后每次调用更新同一个私有 `current`。重新创建计数器则产生独立环境。

普通计数器返回旧值后递增；带复位对象的 `increment` 返回新值，`reset` 恢复构造时的初值。这个差别是返回值契约，不能用看似相近的 `++` 写法混过去。

以下代码单元格保存原生 JS 源码并用 Node.js 执行；Python 只负责组织 Notebook 和显示结果。''',
js_code(JS161),
'''from IPython.display import Code
display(Code(JS_SOURCE,language='javascript'))
trace = json.loads(run_js("const a=createCounter(5), b=createCounter(-1); console.log(JSON.stringify([['a',a()],['a',a()],['b',b()],['a',a()]]));"))
show_table(['closure','returned value'],trace)
print(run_js('console.log(process.version);').strip())
''',
'''print(run_js("""const assert=require('node:assert/strict');
const hello=createHelloWorld();
assert.equal(hello(),'Hello World'); assert.equal(hello(1,null,{}),'Hello World');
const a=createCounter(3),b=createCounter(3);
assert.deepEqual([a(),a(),b(),a(),b()],[3,4,3,5,4]);
const c=createCounterWithReset(5);
assert.deepEqual([c.increment(),c.reset(),c.decrement(),c.reset()],[6,5,4,5]);
console.log('Node assertions passed');"""))
''',
'''每次工厂调用创建独立 `current`，对象方法共享同一词法环境。对调用次数归纳可知普通计数器第 k 次返回 n+k−1；复位将状态转回初态。''',
'''单次构造、调用均 O(1)；每个计数器保存 O(1) 状态。不涉及 JavaScript 数值超出安全整数范围后的精确大整数计数。''')

JS162 = ''''use strict';
function map(arr, fn) {
  const out=[];
  for (let i=0;i<arr.length;i++) out.push(fn(arr[i],i));
  return out;
}
function compose(functions) {
  return function(x) {
    for (let i=functions.length-1;i>=0;i--) x=functions[i](x);
    return x;
  };
}
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
'''
add(162,
'''函数组合从右向左执行，因此 `compose([f,g])(x)=f(g(x))`；空组合保持输入。自定义 map 明确向回调传入“值和索引”，本章数组为稠密数组。

缓存键本身也是契约。把参数 `JSON.stringify` 后当键，会混淆某些值，并失去对象身份。本章用 `Map` 参数前缀树；参数个数由终止节点决定，返回 `undefined` 也有单独命中标记。函数必须是只依赖参数的纯函数；可变对象内容变化而身份不变时，不应期待缓存重新计算。

事件订阅用独立注册对象标识，同一个函数注册两次是两次订阅。emit 对当前订阅列表拍快照，本次触发期间的增删从下一次生效。''',
js_code(JS162),
'''from IPython.display import Code
display(Code(JS_SOURCE,language='javascript'))
trace = json.loads(run_js("const e=new EventEmitter(); const a=e.subscribe('x',v=>v+1); const b=e.subscribe('x',v=>v*2); const rows=[['two listeners',e.emit('x',[3])]]; a.unsubscribe(); rows.push(['after unsubscribe',e.emit('x',[3])]); console.log(JSON.stringify(rows));"))
show_table(['event state','results'],trace)
''',
'''print(run_js("""const assert=require('node:assert/strict');
assert.deepEqual(map([2,3],(x,i)=>x+i),[2,4]);
assert.deepEqual(map([],x=>x),[]); assert.equal(compose([])(7),7);
assert.equal(compose([x=>x+1,x=>x*2])(3),7);
let calls=0; const cached=memoize((...args)=>{calls++;return args.length;});
assert.equal(cached(1),1);assert.equal(cached(1),1);assert.equal(calls,1);
assert.equal(cached(1,undefined),2); assert.equal(cached('1'),1);
const obj={x:1};cached(obj);cached(obj);cached({x:1});assert.equal(calls,5);
let undefinedCalls=0;const missing=memoize(()=>{undefinedCalls++;return undefined;});
missing();missing();assert.equal(undefinedCalls,1);
const e=new EventEmitter();assert.deepEqual(e.emit('absent'),[]);
const cb=x=>x+1, a=e.subscribe('x',cb),b=e.subscribe('x',cb);
assert.deepEqual(e.emit('x',[2]),[3,3]);a.unsubscribe();a.unsubscribe();
assert.deepEqual(e.emit('x',[2]),[3]);b.unsubscribe();assert.deepEqual(e.emit('x'),[]);
const f=new EventEmitter();let second;
f.subscribe('t',()=>{second.unsubscribe();return 1;});
second=f.subscribe('t',()=>2);
assert.deepEqual(f.emit('t'),[1,2]);assert.deepEqual(f.emit('t'),[1]);
console.log('Node assertions passed');"""))
''',
'''参数序列沿唯一前缀树路径到达缓存节点；终止标记区分尚未计算和计算结果为 undefined。事件快照保留订阅顺序，每个注册对象在一次 emit 中调用一次，取消操作只删除对应注册。''',
'''map 和含 k 个函数的组合分别 O(n)、O(k)。a 个参数的缓存访问期望 O(a)，空间随不同参数前缀数增长。emit 对当前 m 个订阅 O(m)；数组式取消订阅 O(m)。''')

JS163 = ''''use strict';
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
'''
add(163,
'''并发结果的顺序与完成时间无关：启动时分配索引，完成时填入对应位置。Promise 的一次拒绝不会自动取消已经开始的其他任务。

超时包装只改变调用者何时得到拒绝；底层函数仍可能运行。成功、失败两条路径都清理计时器。debounce 每次取消上一个待执行回调，最后一次参数与 this 才被使用。本章允许注入时钟以确定性测试边界，并保留真实 Node 定时器测试。

并发池只有 n 个 worker，每个 worker 同时等待一个任务。遇到首个错误停止领新任务，等已经开始的任务收尾后传播首个错误。本教学接口返回按输入排序的结果；要求仅完成信号的平台接口可忽略该返回数组。''',
js_code(JS163),
'''from IPython.display import Code
display(Code(JS_SOURCE,language='javascript'))
trace = json.loads(run_js("""(async()=>{
const trace=[];let active=0;
const jobs=[3,1,2].map((ms,i)=>async()=>{trace.push(['start',i,++active]);await new Promise(r=>setTimeout(r,ms));trace.push(['finish',i,--active]);return i;});
const result=await promisePool(jobs,2);trace.push(['result',JSON.stringify(result),active]);
console.log(JSON.stringify(trace));
})().catch(e=>{console.error(e);process.exitCode=1;});"""))
show_table(['event','task/result','active'],trace)
''',
'''print(run_js("""const assert=require('node:assert/strict');
function fakeClock() {
  let now=0,next=0;const tasks=new Map();
  return {
    setTimeout(fn,delay){const id=next++;tasks.set(id,{time:now+delay,fn});return id;},
    clearTimeout(id){tasks.delete(id);},
    advance(delta){const target=now+delta;while(true){
      const ready=[...tasks].filter(([id,x])=>x.time<=target).sort((a,b)=>a[1].time-b[1].time||a[0]-b[0]);
      if(!ready.length)break;const [id,x]=ready[0];tasks.delete(id);now=x.time;x.fn();
    }now=target;},
    size(){return tasks.size;}
  };
}
(async()=>{
  const clock=fakeClock(),seen=[];
  const deb=debounce(function(x){seen.push(this.prefix+x);},10,clock);
  deb.call({prefix:'a'},1);clock.advance(9);assert.deepEqual(seen,[]);
  deb.call({prefix:'b'},2);clock.advance(9);assert.deepEqual(seen,[]);
  clock.advance(1);assert.deepEqual(seen,['b2']);assert.equal(clock.size(),0);
  deb(3);deb.cancel();clock.advance(20);assert.deepEqual(seen,['b2']);

  const originalSet=globalThis.setTimeout,originalClear=globalThis.clearTimeout;
  const activeTimers=new Set();
  globalThis.setTimeout=(fn,delay,...args)=>{
    let timer=originalSet(()=>{activeTimers.delete(timer);fn(...args);},delay);
    activeTimers.add(timer);return timer;
  };
  globalThis.clearTimeout=timer=>{activeTimers.delete(timer);originalClear(timer);};
  const delay=ms=>new Promise(r=>setTimeout(r,ms));
  try {
    assert.deepEqual(await promiseAll([]),[]);
    assert.deepEqual(await promiseAll([async()=>{await delay(5);return 1;},async()=>2]),[1,2]);
    const boom=new Error('boom');
    await assert.rejects(promiseAll([()=>{throw boom;}]),e=>e===boom);
    assert.equal(await timeLimit(async x=>x+1,100)(2),3);
    await assert.rejects(timeLimit(async()=>{throw boom;},100)(),e=>e===boom);
    let finish;
    const underlyingFinished=new Promise(r=>{finish=r;});
    const slow=async()=>{await delay(15);finish();return 9;};
    await assert.rejects(timeLimit(slow,1)(),e=>e==='Time Limit Exceeded');
    await underlyingFinished;
    // Allow the wrapper's completion handler to clear its already-fired timer.
    await Promise.resolve();
    let active=0,maximum=0;
    const jobs=Array.from({length:12},(_,i)=>async()=>{
      active++;maximum=Math.max(maximum,active);
      try {await delay(i%3);return i*i;} finally {active--;}
    });
    assert.deepEqual(await promisePool(jobs,3),Array.from({length:12},(_,i)=>i*i));
    assert(maximum<=3);assert.equal(active,0);
    let starts=0;
    await assert.rejects(promisePool([
      async()=>{starts++;throw boom;},
      async()=>{starts++;await delay(2);return 1;},
      async()=>{starts++;return 2;}
    ],2),e=>e===boom);
    assert.equal(starts,2);
    assert.deepEqual(await promisePool([],2),[]);
    await assert.rejects(promisePool([],0),RangeError);
    let resolveDebounced;
    const done=new Promise(r=>{resolveDebounced=r;});
    const values=[];const realDeb=debounce(x=>{values.push(x);resolveDebounced();},1);
    realDeb(1);realDeb(2);realDeb(3);await done;
    assert.deepEqual(values,[3]);
    assert.equal(activeTimers.size,0);
  } finally {
    for(const timer of activeTimers)originalClear(timer);
    globalThis.setTimeout=originalSet;globalThis.clearTimeout=originalClear;
  }
  console.log('Node async assertions passed');
})().catch(error=>{console.error(error);process.exitCode=1;});"""))
''',
'''worker 取得索引与递增 next 之间没有 await，因此不会领到重复任务；一个 worker 完成当前任务后才领下一个，同时活跃任务数至多 n。debounce 的待执行定时器至多一个。超时拒绝不是资源取消，必须分别讨论底层任务的收尾。''',
'''忽略任务本身成本，promiseAll 和池调度 O(m)，结果存储 O(m)，池的活跃 worker O(min(n,m))。debounce 每次调用的附加状态 O(1)。定时器测试不以脆弱的墙钟毫秒阈值证明性能。''')
