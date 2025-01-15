"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _poly = _interopRequireDefault(require("./poly"));

var _canvasGl = require("../canvas-gl");

var _eventemitter = _interopRequireDefault(require("eventemitter3"));

var _browserOrNode = require("browser-or-node");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var myCanvas;

class PsImage extends (0, _poly.default)(_canvasGl.Image) {
  constructor() {
    super(...arguments);
    this.isPsImage = true;
  }

  addEventListener(name, cb) {
    if (!this._eventemitter) {
      this._eventemitter = new _eventemitter.default();
    }

    this._eventemitter.once(name, cb);
  }

  static convertToImageData(image, flip) {
    if (flip === void 0) {
      flip = false;
    }

    var {
      width,
      height
    } = image;
    if (!myCanvas) myCanvas = (0, _canvasGl.createCanvas)(width, height);
    myCanvas.width = width;
    myCanvas.height = height;
    var ctx = myCanvas.getContext("2d");

    if (flip) {
      ctx.scale(1, -1);
      ctx.translate(0, -height);
    }

    ctx.clearRect(width, height);
    ctx.drawImage(image, 0, 0);
    return ctx.getImageData(0, 0, width, height);
  }

  static convertToCanvas(imgData, width, height) {
    var can = (0, _canvasGl.createCanvas)(width, height);
    var ctx = can.getContext("2d");
    ctx.putImageData(imgData, 0, 0);
    return can;
  }

}

var _default = _browserOrNode.isBrowser ? window.Image : PsImage;

exports.default = _default;
//# sourceMappingURL=Image.js.map