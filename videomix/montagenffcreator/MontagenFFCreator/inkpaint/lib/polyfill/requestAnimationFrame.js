"use strict";

var ONE_FRAME_TIME = 16; // Date.now

if (!(Date.now && Date.prototype.getTime)) {
  Date.now = function now() {
    return new Date().getTime();
  };
} // performance.now


if (!(global.performance && global.performance.now)) {
  var startTime = Date.now();

  if (!global.performance) {
    global.performance = {};
  }

  global.performance.now = () => Date.now() - startTime;
} // requestAnimationFrame


var lastTime = Date.now();
var vendors = ["ms", "moz", "webkit", "o"];

for (var x = 0; x < vendors.length && !global.requestAnimationFrame; ++x) {
  var p = vendors[x];
  global.requestAnimationFrame = global[p + "RequestAnimationFrame"];
  global.cancelAnimationFrame = global[p + "CancelAnimationFrame"] || global[p + "CancelRequestAnimationFrame"];
}

if (!global.requestAnimationFrame) {
  global.requestAnimationFrame = callback => {
    if (typeof callback !== "function") {
      throw new TypeError(callback + "is not a function");
    }

    var currentTime = Date.now();
    var delay = ONE_FRAME_TIME + lastTime - currentTime;

    if (delay < 0) {
      delay = 0;
    }

    lastTime = currentTime;
    return setTimeout(() => {
      lastTime = Date.now();
      callback(performance.now());
    }, delay);
  };
}

if (!global.cancelAnimationFrame) {
  global.cancelAnimationFrame = id => clearTimeout(id);
}
//# sourceMappingURL=requestAnimationFrame.js.map