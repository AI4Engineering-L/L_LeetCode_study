'use strict';
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
