"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

class WebGLManager {
  constructor(renderer) {
    this.renderer = renderer;
    this.renderer.on("context", this.onContextChange, this);
  }

  onContextChange() {// do some codes init!
  }

  destroy() {
    this.renderer.off("context", this.onContextChange, this);
    this.renderer = null;
  }

}

exports.default = WebGLManager;
//# sourceMappingURL=WebGLManager.js.map