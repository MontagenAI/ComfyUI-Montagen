"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.autoRenderer = autoRenderer;

var _CanvasRenderer = _interopRequireDefault(require("./renderers/canvas/CanvasRenderer"));

var _WebGLRenderer = _interopRequireDefault(require("./renderers/webgl/WebGLRenderer"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function autoRenderer(options) {
  if (options === void 0) {
    options = {};
  }

  var useGL = options.useGL;
  if (useGL) return new _WebGLRenderer.default(options);
  return new _CanvasRenderer.default(options);
}
//# sourceMappingURL=autoRenderer.js.map