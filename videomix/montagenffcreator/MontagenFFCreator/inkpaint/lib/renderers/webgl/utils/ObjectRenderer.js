"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _WebGLManager = _interopRequireDefault(require("../managers/WebGLManager"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class ObjectRenderer extends _WebGLManager.default {
  start() {// set the shader..
  }

  stop() {
    this.flush();
  }

  flush() {// flush!
  }

  render(object) {// render the object
  }

}

exports.default = ObjectRenderer;
//# sourceMappingURL=ObjectRenderer.js.map