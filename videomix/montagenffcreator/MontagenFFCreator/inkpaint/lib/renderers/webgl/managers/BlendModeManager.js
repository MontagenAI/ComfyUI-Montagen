"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _WebGLManager = _interopRequireDefault(require("./WebGLManager"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class BlendModeManager extends _WebGLManager.default {
  constructor(renderer) {
    super(renderer);
    this.currentBlendMode = 99999;
  }

  setBlendMode(blendMode) {
    if (this.currentBlendMode === blendMode) {
      return false;
    }

    this.currentBlendMode = blendMode;
    var mode = this.renderer.blendModes[this.currentBlendMode];
    this.renderer.gl.blendFunc(mode[0], mode[1]);
    return true;
  }

}

exports.default = BlendModeManager;
//# sourceMappingURL=BlendModeManager.js.map