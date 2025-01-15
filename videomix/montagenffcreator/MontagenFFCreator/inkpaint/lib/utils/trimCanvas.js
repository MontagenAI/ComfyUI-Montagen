"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = trimCanvas;

function trimCanvas(canvas) {
  var width = canvas.width;
  var height = canvas.height;
  var context = canvas.getContext("2d");
  var imageData = context.getImageData(0, 0, width, height);
  var pixels = imageData.data;
  var len = pixels.length;
  var bound = {
    top: null,
    left: null,
    right: null,
    bottom: null
  };
  var data = null;
  var i;
  var x;
  var y;

  for (i = 0; i < len; i += 4) {
    if (pixels[i + 3] !== 0) {
      x = i / 4 % width;
      y = ~~(i / 4 / width);

      if (bound.top === null) {
        bound.top = y;
      }

      if (bound.left === null) {
        bound.left = x;
      } else if (x < bound.left) {
        bound.left = x;
      }

      if (bound.right === null) {
        bound.right = x + 1;
      } else if (bound.right < x) {
        bound.right = x + 1;
      }

      if (bound.bottom === null) {
        bound.bottom = y;
      } else if (bound.bottom < y) {
        bound.bottom = y;
      }
    }
  }

  if (bound.top !== null) {
    width = bound.right - bound.left;
    height = bound.bottom - bound.top + 1;
    data = context.getImageData(bound.left, bound.top, width, height);
  }

  return {
    height,
    width,
    data
  };
}
//# sourceMappingURL=trimCanvas.js.map