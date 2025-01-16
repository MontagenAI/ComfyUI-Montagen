"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _BaseTexture = _interopRequireDefault(require("./BaseTexture"));

var _settings = _interopRequireDefault(require("../settings"));

var _TextureUvs = _interopRequireDefault(require("./TextureUvs"));

var _eventemitter = _interopRequireDefault(require("eventemitter3"));

var _math = require("../math");

var _utils = require("../utils");

var _cache = require("../utils/cache");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class Texture extends _eventemitter.default {
  constructor(baseTexture, frame, orig, trim, rotate, anchor) {
    super();

    if (frame) {
      this.hasDefaultFrame = true;
    } else {
      this.hasDefaultFrame = false;
      frame = new _math.Rectangle(0, 0, 1, 1);
    }

    this._uvs = null;
    this._cache = [];
    this.valid = false;
    this.destroyed = false;
    this.requiresUpdate = false;
    this.cutout = false;
    this.cutoutColors = null;
    this.trim = trim;
    this.orig = orig || frame;
    this._frame = frame;
    this._rotate = Number(rotate || 0);
    this._updateID = 0;
    this.transform = null;
    this.textureCacheIds = [];

    if (rotate === true) {
      this._rotate = 2;
    } else if (this._rotate % 2 !== 0) {
      throw new Error("attempt to use diamond-shaped UVs.");
    }

    this.id = (0, _utils.uuidvx)();
    this.initBaseTexture(baseTexture, frame);
    this.defaultAnchor = anchor ? new _math.Point(anchor.x, anchor.y) : new _math.Point(0, 0);
  }

  initBaseTexture(baseTexture, frame) {
    if (baseTexture instanceof Texture) baseTexture = baseTexture.baseTexture;
    this.baseTexture = baseTexture;
    this.addToCache(baseTexture.imageUrl);

    if (baseTexture.hasLoaded) {
      if (!this.hasDefaultFrame) {
        // from 1,1 -> w,h
        var {
          width,
          height
        } = baseTexture;
        this.frame = new _math.Rectangle(0, 0, width, height);
        baseTexture.on("update", this.onBaseTextureUpdated, this);
      } else {
        this.frame = frame;
      }

      baseTexture.adaptedNodeCanvas();
    } else {
      baseTexture.once("loaded", this.onBaseTextureLoaded, this);
    }

    baseTexture.on("error", this.onBaseTextureError, this);
  }

  update() {
    this.baseTexture.update();
  }

  addToCache(imageUrl) {
    if (!imageUrl) return;
    if (this._cache.indexOf(imageUrl) < 0) this._cache.push(imageUrl);
  }

  updateSource(imageUrl, useCache) {
    if (useCache === void 0) {
      useCache = false;
    }

    if (this.baseTexture.imageUrl === imageUrl) return;

    if (useCache) {
      this.addToCache(imageUrl);
      this.baseTexture = _BaseTexture.default.fromImage(imageUrl);
      this.baseTexture.adaptedNodeCanvas();
    } else {
      this.baseTexture.updateSource(imageUrl);
    }
  }

  getImageUrl() {
    return this.baseTexture.imageUrl;
  }

  onBaseTextureLoaded(baseTexture) {
    this._updateID++;

    if (!this.hasDefaultFrame) {
      // from 1,1 -> w,h
      var {
        width,
        height
      } = baseTexture;
      this.frame = new _math.Rectangle(0, 0, width, height);
    } else {
      this.frame = this._frame;
    }

    baseTexture.adaptedNodeCanvas();
    this.baseTexture.on("update", this.onBaseTextureUpdated, this);
    this.emit("update", this);
  }

  onBaseTextureError(e) {
    this.emit("error", e);
  }

  onBaseTextureUpdated(baseTexture) {
    this._updateID++;

    if (!this.hasDefaultFrame) {
      this._frame.width = baseTexture.width;
      this._frame.height = baseTexture.height;
    }

    baseTexture.adaptedNodeCanvas();
    this.emit("update", this);
  }

  destroy(destroyBase) {
    if (this.destroyed) return;

    if (this.baseTexture) {
      if (destroyBase) {
        var {
          imageUrl
        } = this.baseTexture;

        if (_cache.TextureCache[imageUrl]) {
          (0, _cache.removeFromTextureCache)(imageUrl);
        }

        for (var i = 0; i < this._cache.length; i++) {
          var urlKey = this._cache[i];
          (0, _cache.destroyBaseTextureCache)(urlKey);
        }

        this.baseTexture.destroy();
      }

      this.baseTexture.off("update", this.onBaseTextureUpdated, this);
      this.baseTexture.off("loaded", this.onBaseTextureLoaded, this);
      this.baseTexture.off("error", this.onBaseTextureError, this);
      this.baseTexture = null;
    }

    this._cache.length = 0;
    this._cache = null;
    this._frame = null;
    this._uvs = null;
    this.trim = null;
    this.orig = null;
    this.valid = false;
    this.cutout = false;
    this.cutoutColors = null;
    this.destroyed = true;
    (0, _cache.removeFromTextureCache)(this);
    this.textureCacheIds = null;
  }

  clone() {
    return new Texture(this.baseTexture, this.frame, this.orig, this.trim, this.rotate, this.defaultAnchor);
  }

  _updateUvs() {
    if (!this._uvs) this._uvs = new _TextureUvs.default();

    this._uvs.set(this._frame, this.baseTexture, this.rotate);

    this._updateID++;
  }

  get frame() {
    return this._frame;
  }

  set frame(frame) {
    this._frame = frame;
    this.hasDefaultFrame = true;
    var {
      x,
      y,
      width,
      height
    } = frame;
    var xNotFit = x + width > this.baseTexture.width;
    var yNotFit = y + height > this.baseTexture.height;

    if (xNotFit || yNotFit) {
      var relationship = xNotFit && yNotFit ? "and" : "or";
      var errorX = "X: " + x + " + " + width + " = " + (x + width) + " > " + this.baseTexture.width;
      var errorY = "Y: " + y + " + " + height + " = " + (y + height) + " > " + this.baseTexture.height;
      throw new Error("Texture Error: frame does not fit inside the base Texture dimensions: " + (errorX + " " + relationship + " " + errorY));
    }

    this.valid = width && height && this.baseTexture.hasLoaded;

    if (!this.trim && !this.rotate) {
      this.orig = frame;
    }

    if (this.valid) this._updateUvs();
  }

  get rotate() {
    return this._rotate;
  }

  set rotate(rotate) {
    this._rotate = rotate;
    if (this.valid) this._updateUvs();
  }

  get width() {
    return this.orig.width;
  }

  get height() {
    return this.orig.height;
  }

  static newEmpty() {
    return new Texture(new _BaseTexture.default());
  }

  static fromImage(imageUrl, crossorigin, scaleMode, sourceScale) {
    var texture = _cache.TextureCache[imageUrl];
    if (texture) return texture;

    if (crossorigin instanceof _math.Rectangle) {
      texture = new Texture(_BaseTexture.default.fromImage(imageUrl), crossorigin, scaleMode, sourceScale);
    } else {
      texture = new Texture(_BaseTexture.default.fromImage(imageUrl, crossorigin, scaleMode, sourceScale));
    }

    (0, _cache.addToTextureCache)(texture, imageUrl);
    return texture;
  }

  static fromFrame(frameId) {
    var texture = _cache.TextureCache[frameId];

    if (!texture) {
      throw new Error("The frameId \"" + frameId + "\" does not exist in cache");
    }

    return texture;
  }

  static fromCanvas(canvas, scaleMode, origin) {
    if (origin === void 0) {
      origin = "canvas";
    }

    return new Texture(_BaseTexture.default.fromCanvas(canvas, scaleMode, origin));
  }

  static from(source) {
    if (typeof source === "string") {
      var texture = _cache.TextureCache[source];
      if (texture) return texture;
      return Texture.fromImage(source);
    } else if (source instanceof Texture) {
      return source;
    } else if (source instanceof HTMLImageElement) {
      return new Texture(_BaseTexture.default.from(source));
    } else if (source instanceof HTMLCanvasElement) {
      return Texture.fromCanvas(source, _settings.default.SCALE_MODE, "HTMLCanvasElement");
    } else if (source instanceof _BaseTexture.default) {
      return new Texture(source);
    }

    return source;
  }

  static fromLoader(source, imageUrl, name) {
    var baseTexture = new _BaseTexture.default(source, undefined, (0, _utils.getResolutionOfUrl)(imageUrl));
    var texture = new Texture(baseTexture);
    baseTexture.imageUrl = imageUrl;
    if (!name) name = imageUrl;
    (0, _cache.addToBaseTextureCache)(texture.baseTexture, name);
    (0, _cache.addToTextureCache)(texture, name);

    if (name !== imageUrl) {
      (0, _cache.addToBaseTextureCache)(texture.baseTexture, imageUrl);
      (0, _cache.addToTextureCache)(texture, imageUrl);
    }

    return texture;
  }

}

exports.default = Texture;

function removeAllHandlers(tex) {
  tex.destroy = () => {};

  tex.on = () => {};

  tex.once = () => {};

  tex.emit = () => {};
}

Texture.EMPTY = new Texture(new _BaseTexture.default());
removeAllHandlers(Texture.EMPTY);
removeAllHandlers(Texture.EMPTY.baseTexture);
//# sourceMappingURL=Texture.js.map