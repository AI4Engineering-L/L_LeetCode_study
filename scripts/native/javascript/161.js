'use strict';
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
