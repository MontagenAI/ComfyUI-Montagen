"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _BaseRenderTexture = _interopRequireDefault(require("./BaseRenderTexture"));

var _Texture = _interopRequireDefault(require("./Texture"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class RenderTexture extends _Texture.default {
  constructor(baseRenderTexture, frame) {
    // support for legacy..
    var _legacyRenderer = null;

    if (!(baseRenderTexture instanceof _BaseRenderTexture.default)) {
      /* eslint-disable prefer-rest-params, no-console */
      var width = arguments[1];
      var height = arguments[2];
      var scaleMode = arguments[3];
      var resolution = arguments[4]; // we have an old render texture..

      console.warn("Please use RenderTexture.create(" + width + ", " + height + ") instead of the ctor directly.");
      _legacyRenderer = arguments[0];
      frame = null;
      baseRenderTexture = new _BaseRenderTexture.default(width, height, scaleMode, resolution);
    }

    super(baseRenderTexture, frame);
    this.legacyRenderer = _legacyRenderer;
    this.valid = true;

    this._updateUvs();
  }

  resize(width, height, doNotResizeBaseTexture) {
    width = Math.ceil(width);
    height = Math.ceil(height); // TODO - could be not required..

    this.valid = width > 0 && height > 0;
    this._frame.width = this.orig.width = width;
    this._frame.height = this.orig.height = height;

    if (!doNotResizeBaseTexture) {
      this.baseTexture.resize(width, height);
    }

    this._updateUvs();
  }

  static create(width, height, scaleMode, resolution) {
    return new RenderTexture(new _BaseRenderTexture.default(width, height, scaleMode, resolution));
  }

}

exports.default = RenderTexture;
//# sourceMappingURL=RenderTexture.js.map