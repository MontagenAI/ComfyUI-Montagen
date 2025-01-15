"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _canvasGl = require("../canvas-gl");

var _poly = _interopRequireDefault(require("./poly"));

var _glfix = _interopRequireDefault(require("./glfix"));

var _utils = require("../utils");

var _eventemitter = _interopRequireDefault(require("eventemitter3"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class PSCanvas extends (0, _poly.default)(_canvasGl.Canvas) {
  constructor(width, height, type) {
    super(width, height, type);
    this._event = new _eventemitter.default();
    this._glResizeExt = null;
    this._gl = null;
    this._renderType = "2d";
    this.useTypedArray = false;
    this.rgbReverse = false;
    this.isPSCanvas = true;
    this.id = (0, _utils.uuidvx)();
  } // Get canvas context


  getContext(type, options) {
    this._renderType = type;

    if (type === "webgl") {
      if (this._gl) return this._gl;
      var {
        width,
        height
      } = this;
      var ctx = (0, _canvasGl.gl)(width, height, options);

      _glfix.default.fixGetUniformLocation(ctx);

      _glfix.default.fixTexImage2D(ctx);

      this._gl = ctx;
      this._glResizeExt = ctx.getExtension("STACKGL_resize_drawingbuffer");
      this._ctx = super.getContext("2d", options);
      return this._gl;
    } else {
      this._ctx = super.getContext("2d", options);
    }

    return super.getContext(type, options);
  } // Canvas Reset width and height


  get height() {
    return super.height;
  }

  set height(value) {
    if (this._glResizeExt) this._glResizeExt.resize(this.width, value);
    super.height = value;
  }

  get width() {
    return super.width;
  }

  set width(value) {
    if (this._glResizeExt) this._glResizeExt.resize(value, this.height);
    super.width = value;
  }

  get clientWidth() {
    return super.width;
  }

  get clientHeight() {
    return super.height;
  } // add and remove event listener


  addEventListener(type, listener) {
    return this._event.addListener(type, listener);
  }

  removeEventListener(type, listener) {
    if (listener) return this._event.removeListener(type, listener);
    return this._event.removeAllListeners(type);
  }

  _glBuffer() {
    var {
      width,
      height,
      _ctx,
      _gl
    } = this;
    var pixels = new Uint8Array(width * height * 4);

    _gl.readPixels(0, 0, width, height, _gl.RGBA, _gl.UNSIGNED_BYTE, pixels);

    return Buffer.from(pixels);
  }

  _putImageData() {
    var data;
    var {
      width,
      height,
      _ctx,
      _gl,
      useTypedArray
    } = this;
    var pixels = new Uint8Array(width * height * 4);

    _gl.readPixels(0, 0, width, height, _gl.RGBA, _gl.UNSIGNED_BYTE, pixels);

    if (useTypedArray) {
      data = (0, _canvasGl.createImageData)(new Uint8ClampedArray(pixels), width, height);
    } else {
      data = _ctx.getImageData(0, 0, width, height);

      this._fillImageData(data, pixels, width, height);
    }

    _ctx.putImageData(data, 0, 0);
  }

  _reverseColor() {
    var m = [2, 1, 0, 3];
    var {
      width,
      height,
      _ctx
    } = this;

    var pixels = _ctx.getImageData(0, 0, width, height);

    var data = new Uint8Array(width * height * 4);

    for (var i = 0; i < height; i++) {
      for (var j = 0; j < width; j++) {
        var col = j;
        var row = i;

        for (var k = 0; k < 4; k++) {
          var idx = 4 * (row * width + col) + m[k];
          var idx2 = 4 * (row * width + col) + k;
          data[idx] = pixels.data[idx2];
        }
      }
    }

    var imageData = (0, _canvasGl.createImageData)(new Uint8ClampedArray(data), width, height);

    _ctx.putImageData(imageData, 0, 0);
  }

  _fillImageData(data, pixels, width, height) {
    var m = this.rgbReverse ? [2, 1, 0, 3] : [0, 1, 2, 3];

    for (var i = 0; i < height; i++) {
      for (var j = 0; j < width; j++) {
        var col = j;
        var row = height - i - 1;

        for (var k = 0; k < 4; k++) {
          var idx = 4 * (row * width + col) + m[k];
          var idx2 = 4 * (i * width + col) + k;
          data.data[idx] = pixels[idx2];
        }
      }
    }

    return data;
  } // Store buffer png jpg and other data


  toBuffer() {
    if (this._gl) return this._glBuffer();else if (this.rgbReverse) this._reverseColor();
    return super.toBuffer(...arguments);
  }

  toDataURL() {
    if (this._gl) this._putImageData();else if (this.rgbReverse) this._reverseColor();
    return super.toDataURL(...arguments);
  }

  createPNGStream() {
    if (this._gl) this._putImageData();else if (this.rgbReverse) this._reverseColor();
    return super.createPNGStream(...arguments);
  }

  createJPEGStream() {
    if (this._gl) this._putImageData();else if (this.rgbReverse) this._reverseColor();
    return super.createJPEGStream(...arguments);
  }

  createPDFStream() {
    if (this._gl) this._putImageData();else if (this.rgbReverse) this._reverseColor();
    return super.createPDFStream(...arguments);
  }

  destroy() {
    //super.destroy();
    this._event.removeAllListeners();

    this._event = null;
    this._glResizeExt = null;
    this._gl = null;
    this._ctx = null;
  }

}

exports.default = PSCanvas;
//# sourceMappingURL=Canvas.js.map