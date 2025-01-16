"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _const = require("../../const");

var _settings = _interopRequireDefault(require("../../settings"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class TextureGarbageCollector {
  constructor(renderer) {
    this.renderer = renderer;
    this.count = 0;
    this.checkCount = 0;
    this.maxIdle = _settings.default.GC_MAX_IDLE;
    this.checkCountMax = _settings.default.GC_MAX_CHECK_COUNT;
    this.mode = _settings.default.GC_MODE;
  }

  update() {
    this.count++;

    if (this.mode === _const.GC_MODES.MANUAL) {
      return;
    }

    this.checkCount++;

    if (this.checkCount > this.checkCountMax) {
      this.checkCount = 0;
      this.run();
    }
  }

  run() {
    var tm = this.renderer.textureManager;
    var managedTextures = tm._managedTextures;
    var wasRemoved = false;

    for (var i = 0; i < managedTextures.length; i++) {
      var texture = managedTextures[i]; // only supports non generated textures at the moment!

      if (!texture._glRenderTargets && this.count - texture.touched > this.maxIdle) {
        tm.destroyTexture(texture, true);
        managedTextures[i] = null;
        wasRemoved = true;
      }
    }

    if (wasRemoved) {
      var j = 0;

      for (var _i = 0; _i < managedTextures.length; _i++) {
        if (managedTextures[_i] !== null) {
          managedTextures[j++] = managedTextures[_i];
        }
      }

      managedTextures.length = j;
    }
  }

  unload(displayObject) {
    var tm = this.renderer.textureManager; // only destroy non generated textures

    if (displayObject._texture && displayObject._texture._glRenderTargets) {
      tm.destroyTexture(displayObject._texture, true);
    }

    for (var i = displayObject.children.length - 1; i >= 0; i--) {
      this.unload(displayObject.children[i]);
    }
  }

}

exports.default = TextureGarbageCollector;
//# sourceMappingURL=TextureGarbageCollector.js.map