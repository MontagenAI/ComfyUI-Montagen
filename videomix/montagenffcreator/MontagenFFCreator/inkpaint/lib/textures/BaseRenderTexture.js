"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _BaseTexture = _interopRequireDefault(require("./BaseTexture"));

var _settings = _interopRequireDefault(require("../settings"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class BaseRenderTexture extends _BaseTexture.default {
  constructor(width, height, scaleMode, resolution) {
    if (width === void 0) {
      width = 100;
    }

    if (height === void 0) {
      height = 100;
    }

    super(null, scaleMode);
    this.resolution = resolution || _settings.default.RESOLUTION;
    this.width = Math.ceil(width);
    this.height = Math.ceil(height);
    this.realWidth = this.width * this.resolution;
    this.realHeight = this.height * this.resolution;
    this.scaleMode = scaleMode !== undefined ? scaleMode : _settings.default.SCALE_MODE;
    this.hasLoaded = true;
    this._glRenderTargets = {};
    this._canvasRenderTarget = null;
    this.valid = false;
  }

  resize(width, height) {
    width = Math.ceil(width);
    height = Math.ceil(height);

    if (width === this.width && height === this.height) {
      return;
    }

    this.valid = width > 0 && height > 0;
    this.width = width;
    this.height = height;
    this.realWidth = this.width * this.resolution;
    this.realHeight = this.height * this.resolution;

    if (!this.valid) {
      return;
    }

    this.emit("update", this);
  }

  destroy() {
    super.destroy(true);
    this.renderer = null;
  }

}

exports.default = BaseRenderTexture;
//# sourceMappingURL=BaseRenderTexture.js.map