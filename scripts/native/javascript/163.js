'use strict';
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
