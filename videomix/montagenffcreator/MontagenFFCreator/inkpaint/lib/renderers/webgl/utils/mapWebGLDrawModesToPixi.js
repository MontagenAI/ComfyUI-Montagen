"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = mapWebGLDrawModesToPixi;

var _const = require("../../../const");

function mapWebGLDrawModesToPixi(gl, object) {
  if (object === void 0) {
    object = {};
  }

  object[_const.DRAW_MODES.POINTS] = gl.POINTS;
  object[_const.DRAW_MODES.LINES] = gl.LINES;
  object[_const.DRAW_MODES.LINE_LOOP] = gl.LINE_LOOP;
  object[_const.DRAW_MODES.LINE_STRIP] = gl.LINE_STRIP;
  object[_const.DRAW_MODES.TRIANGLES] = gl.TRIANGLES;
  object[_const.DRAW_MODES.TRIANGLE_STRIP] = gl.TRIANGLE_STRIP;
  object[_const.DRAW_MODES.TRIANGLE_FAN] = gl.TRIANGLE_FAN;
  return object;
}
//# sourceMappingURL=mapWebGLDrawModesToPixi.js.map