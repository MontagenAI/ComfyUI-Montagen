"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _core = require("../core");

var _utils = require("../utils");

var _cache = require("../utils/cache");

class Spritesheet {
  static get BATCH_SIZE() {
    return 1000;
  }

  constructor(baseTexture, data, resolutionFilename) {
    if (resolutionFilename === void 0) {
      resolutionFilename = null;
    }

    this.baseTexture = baseTexture;
    this.textures = {};
    this.animations = {};
    this.data = data;
    this.resolution = this._updateResolution(resolutionFilename || this.baseTexture.imageUrl);
    this._frames = this.data.frames;
    this._frameKeys = Object.keys(this._frames);
    this._batchIndex = 0;
    this._callback = null;
  }

  _updateResolution(resolutionFilename) {
    var scale = this.data.meta.scale; // Use a defaultValue of `null` to check if a url-based resolution is set

    var resolution = (0, _utils.getResolutionOfUrl)(resolutionFilename, null); // No resolution found via URL

    if (resolution === null) {
      // Use the scale value or default to 1
      resolution = scale !== undefined ? parseFloat(scale) : 1;
    } // For non-1 resolutions, update baseTexture


    if (resolution !== 1) {
      this.baseTexture.resolution = resolution;
      this.baseTexture.update();
    }

    return resolution;
  }

  parse(callback) {
    this._batchIndex = 0;
    this._callback = callback;

    if (this._frameKeys.length <= Spritesheet.BATCH_SIZE) {
      this._processFrames(0);

      this._processAnimations();

      this._parseComplete();
    } else {
      this._nextBatch();
    }
  }

  _processFrames(initialFrameIndex) {
    var frameIndex = initialFrameIndex;
    var maxFrames = Spritesheet.BATCH_SIZE;
    var sourceScale = this.baseTexture.sourceScale;

    while (frameIndex - initialFrameIndex < maxFrames && frameIndex < this._frameKeys.length) {
      var i = this._frameKeys[frameIndex];
      var data = this._frames[i];
      var rect = data.frame;

      if (rect) {
        var frame = null;
        var trim = null;
        var sourceSize = data.trimmed !== false && data.sourceSize ? data.sourceSize : data.frame;
        var orig = new _core.Rectangle(0, 0, Math.floor(sourceSize.w * sourceScale) / this.resolution, Math.floor(sourceSize.h * sourceScale) / this.resolution);

        if (data.rotated) {
          frame = new _core.Rectangle(Math.floor(rect.x * sourceScale) / this.resolution, Math.floor(rect.y * sourceScale) / this.resolution, Math.floor(rect.h * sourceScale) / this.resolution, Math.floor(rect.w * sourceScale) / this.resolution);
        } else {
          frame = new _core.Rectangle(Math.floor(rect.x * sourceScale) / this.resolution, Math.floor(rect.y * sourceScale) / this.resolution, Math.floor(rect.w * sourceScale) / this.resolution, Math.floor(rect.h * sourceScale) / this.resolution);
        } //  Check to see if the sprite is trimmed


        if (data.trimmed !== false && data.spriteSourceSize) {
          trim = new _core.Rectangle(Math.floor(data.spriteSourceSize.x * sourceScale) / this.resolution, Math.floor(data.spriteSourceSize.y * sourceScale) / this.resolution, Math.floor(rect.w * sourceScale) / this.resolution, Math.floor(rect.h * sourceScale) / this.resolution);
        }

        this.textures[i] = new _core.Texture(this.baseTexture, frame, orig, trim, data.rotated ? 2 : 0, data.anchor);
        (0, _cache.addToTextureCache)(this.textures[i], i);
      }

      frameIndex++;
    }
  }

  _processAnimations() {
    var animations = this.data.animations || {};

    for (var animName in animations) {
      this.animations[animName] = [];

      for (var frameName of animations[animName]) {
        this.animations[animName].push(this.textures[frameName]);
      }
    }
  }

  _parseComplete() {
    var callback = this._callback;
    this._callback = null;
    this._batchIndex = 0;
    callback.call(this, this.textures);
  }

  _nextBatch() {
    this._processFrames(this._batchIndex * Spritesheet.BATCH_SIZE);

    this._batchIndex++;
    setTimeout(() => {
      if (this._batchIndex * Spritesheet.BATCH_SIZE < this._frameKeys.length) {
        this._nextBatch();
      } else {
        this._processAnimations();

        this._parseComplete();
      }
    }, 0);
  }

  destroy(destroyBase) {
    if (destroyBase === void 0) {
      destroyBase = false;
    }

    for (var i in this.textures) {
      this.textures[i].destroy();
    }

    this._frames = null;
    this._frameKeys = null;
    this.data = null;
    this.textures = null;

    if (destroyBase) {
      this.baseTexture.destroy();
    }

    this.baseTexture = null;
  }

}

exports.default = Spritesheet;
//# sourceMappingURL=Spritesheet.js.map