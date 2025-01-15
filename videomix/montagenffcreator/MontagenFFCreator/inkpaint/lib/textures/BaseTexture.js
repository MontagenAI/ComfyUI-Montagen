"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Image = _interopRequireDefault(require("../polyfill/Image"));

var _settings = _interopRequireDefault(require("../settings"));

var _bitTwiddle = _interopRequireDefault(require("bit-twiddle"));

var _eventemitter = _interopRequireDefault(require("eventemitter3"));

var _utils = require("../utils");

var _cache = require("../utils/cache");

var _canvas = require("canvas");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class BaseTexture extends _eventemitter.default {
  constructor(source, scaleMode, resolution) {
    super();
    this.uid = (0, _utils.uid)();
    this.touched = 0;
    this.width = 100;
    this.height = 100;
    this.realWidth = 100;
    this.realHeight = 100;
    this.resolution = resolution || _settings.default.RESOLUTION;
    this.scaleMode = scaleMode !== undefined ? scaleMode : _settings.default.SCALE_MODE;
    this.hasLoaded = false;
    this.isLoading = false;
    this.image = null;
    this.source = null;
    this.imageType = null;
    this.sourceScale = 1.0;
    this.premultipliedAlpha = true;
    this.imageUrl = null;
    this.isPowerOfTwo = false;
    this.cutout = false;
    this.cutoutColors = null;
    this.mipmap = _settings.default.MIPMAP_TEXTURES;
    this.wrapMode = _settings.default.WRAP_MODE;
    this._glTextures = {};
    this._enabled = 0;
    this._virtalBoundId = -1;
    this.destroyed = false;
    this.textureCacheIds = [];
    this.loadSource(source);
  }

  updateSource(imageUrl) {
    if (!this.image) this.image = new _Image.default();
    this.resetImage(this.image);
    this.loadSource(this.image);
    this.image.src = imageUrl;
    this.imageUrl = imageUrl;
    this.resolution = (0, _utils.getResolutionOfUrl)(imageUrl);
  }

  loadSource(source) {
    if (!source) return;
    var wasLoading = this.isLoading;
    this.hasLoaded = false;
    this.isLoading = false;
    if (wasLoading && this.source) this.removeHandler(this.source);
    var firstLoaded = !this.source;
    this.source = source; // source resources loaded

    var {
      src,
      width,
      height,
      complete,
      getContext,
      network
    } = source;
    var hasSize = width && height;

    if ((src && complete || network && complete || getContext) && hasSize) {
      this._updateImageType();

      this._sourceLoaded();

      if (firstLoaded) this.emit("loaded", this);
    } // the resource is not loaded
    else if (!getContext) {
      this.isLoading = true;

      source.onload = () => {
        this._updateImageType();

        this.removeHandler(source);
        if (!this.isLoading) return;
        this.isLoading = false;

        this._sourceLoaded();

        this.emit("loaded", this);
      };

      source.onerror = () => {
        this.removeHandler(source);
        if (!this.isLoading) return;
        this.isLoading = false;
        this.emit("error", this);
      };

      if (complete && src) {
        this.removeHandler(source);
        this.isLoading = false;

        if (width && height) {
          this._sourceLoaded();

          if (wasLoading) this.emit("loaded", this);
        } else if (wasLoading) {
          this.emit("error", this);
        }
      }
    }
  }

  removeHandler(source) {
    source.onload = null;
    source.onerror = null;
  }

  resetImage(image) {
    image.src = "";
    image.width = 0;
    image.height = 0;
  }

  adaptedNodeCanvas() {
    var {
      source,
      cutout,
      cutoutColors
    } = this;

    if (source && source instanceof _Image.default && source.isPsImage) {
      this.source = _Image.default.convertToImageData(source);
    }
  }

  update() {
    if (this.imageType !== "svg") {
      this.realWidth = this.source.naturalWidth || this.source.videoWidth || this.source.width;
      this.realHeight = this.source.naturalHeight || this.source.videoHeight || this.source.height; // update width and height

      this._updateDimensions();
    }

    this.emit("update", this);
  }

  _updateDimensions() {
    this.width = this.realWidth / this.resolution;
    this.height = this.realHeight / this.resolution;
    this.isPowerOfTwo = _bitTwiddle.default.isPow2(this.realWidth) && _bitTwiddle.default.isPow2(this.realHeight);
  }

  _updateImageType() {
    if (!this.imageUrl) return;
    var dataUri = (0, _utils.decomposeDataUri)(this.imageUrl);
    var imageType;

    if (dataUri && dataUri.mediaType === "image") {
      var firstSubType = dataUri.subType.split("+")[0];
      imageType = (0, _utils.getUrlFileExt)("." + firstSubType);
    } else {
      imageType = (0, _utils.getUrlFileExt)(this.imageUrl);
    }

    this.imageType = imageType || "png";
  }

  _sourceLoaded() {
    this.hasLoaded = true;
    this.update();
  }

  destroy() {
    if (this.imageUrl) {
      delete _cache.TextureCache[this.imageUrl];
      this.imageUrl = null;
      this.source.src = "";
      this.removeHandler(this.source);
    }

    if (this.image) {
      this.image.src = "";
      this.image = null;
    }

    this.source = null;
    this.dispose();
    (0, _cache.removeFromBaseTextureCache)(this);
    this.textureCacheIds = null;
    this.destroyed = true;
    this.cutout = false;
    this.cutoutColors = null;
  }

  dispose() {
    this.emit("dispose", this);
  }

  static fromImage(imageUrl, crossorigin, scaleMode, sourceScale) {
    var baseTexture = _cache.BaseTextureCache[imageUrl];

    if (!baseTexture) {
      var image = new _Image.default();
      baseTexture = new BaseTexture(image, scaleMode);
      baseTexture.imageUrl = imageUrl;
      if (sourceScale) baseTexture.sourceScale = sourceScale;
      baseTexture.resolution = (0, _utils.getResolutionOfUrl)(imageUrl);
      image.src = imageUrl;
      (0, _cache.addToBaseTextureCache)(baseTexture, imageUrl);
    }

    return baseTexture;
  }

  static fromCanvas(canvas, scaleMode, origin) {
    if (origin === void 0) {
      origin = "canvas";
    }

    if (!canvas.__paintId) canvas.__paintId = origin + "_" + (0, _utils.uid)();
    var baseTexture = _cache.BaseTextureCache[canvas.__paintId];

    if (!baseTexture) {
      baseTexture = new BaseTexture(canvas, scaleMode);
      (0, _cache.addToBaseTextureCache)(baseTexture, canvas.__paintId);
    }

    return baseTexture;
  }

  static from(source, scaleMode, sourceScale) {
    if (typeof source === "string") {
      return BaseTexture.fromImage(source, undefined, scaleMode, sourceScale);
    } else if (source instanceof HTMLImageElement) {
      var imageUrl = source.src;
      var baseTexture = _cache.BaseTextureCache[imageUrl];

      if (!baseTexture) {
        baseTexture = new BaseTexture(source, scaleMode);
        baseTexture.imageUrl = imageUrl;

        if (sourceScale) {
          baseTexture.sourceScale = sourceScale;
        }

        baseTexture.resolution = (0, _utils.getResolutionOfUrl)(imageUrl);
        (0, _cache.addToBaseTextureCache)(baseTexture, imageUrl);
      }

      return baseTexture;
    } else if (source instanceof HTMLCanvasElement) {
      return BaseTexture.fromCanvas(source, scaleMode);
    }

    return source;
  }

}

exports.default = BaseTexture;
//# sourceMappingURL=BaseTexture.js.map