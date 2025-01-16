"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Image = _interopRequireDefault(require("../../polyfill/Image"));

var _utils = require("../../utils");

var _canUseNewCanvasBlendModes = _interopRequireDefault(require("../../renderers/canvas/utils/canUseNewCanvasBlendModes"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var CanvasTinter = {
  getTintedTexture: (sprite, color) => {
    var texture = sprite._texture;
    color = CanvasTinter.roundColor(color);
    var stringColor = "#" + ("00000" + (color | 0).toString(16)).substr(-6);
    texture.tintCache = texture.tintCache || {};
    var cachedTexture = texture.tintCache[stringColor];
    var canvas;

    if (cachedTexture) {
      if (cachedTexture.tintId === texture._updateID) {
        return texture.tintCache[stringColor];
      }

      canvas = texture.tintCache[stringColor];
    } else {
      canvas = CanvasTinter.canvas;
    }

    CanvasTinter.tintMethod(texture, color, canvas);
    canvas.tintId = texture._updateID;

    if (CanvasTinter.convertTintToImage) {
      var tintImage = new _Image.default();
      tintImage.src = canvas.toDataURL();
      texture.tintCache[stringColor] = tintImage;
    } else {
      texture.tintCache[stringColor] = canvas;
      CanvasTinter.canvas = null;
    }

    return canvas;
  },
  tintWithMultiply: (texture, color, canvas) => {
    var context = canvas.getContext("2d");

    var crop = texture._frame.clone();

    var resolution = texture.baseTexture.resolution;
    crop.x *= resolution;
    crop.y *= resolution;
    crop.width *= resolution;
    crop.height *= resolution;
    canvas.width = Math.ceil(crop.width);
    canvas.height = Math.ceil(crop.height);
    context.save();
    context.fillStyle = "#" + ("00000" + (color | 0).toString(16)).substr(-6);
    context.fillRect(0, 0, crop.width, crop.height);
    context.globalCompositeOperation = "multiply";
    context.drawImage(texture.baseTexture.source, crop.x, crop.y, crop.width, crop.height, 0, 0, crop.width, crop.height);
    context.globalCompositeOperation = "destination-atop";
    context.drawImage(texture.baseTexture.source, crop.x, crop.y, crop.width, crop.height, 0, 0, crop.width, crop.height);
    context.restore();
  },

  tintWithOverlay(texture, color, canvas) {
    var context = canvas.getContext("2d");

    var crop = texture._frame.clone();

    var resolution = texture.baseTexture.resolution;
    crop.x *= resolution;
    crop.y *= resolution;
    crop.width *= resolution;
    crop.height *= resolution;
    canvas.width = Math.ceil(crop.width);
    canvas.height = Math.ceil(crop.height);
    context.save();
    context.globalCompositeOperation = "copy";
    context.fillStyle = "#" + ("00000" + (color | 0).toString(16)).substr(-6);
    context.fillRect(0, 0, crop.width, crop.height);
    context.globalCompositeOperation = "destination-atop";
    context.drawImage(texture.baseTexture.source, crop.x, crop.y, crop.width, crop.height, 0, 0, crop.width, crop.height); // context.globalCompositeOperation = 'copy';

    context.restore();
  },

  tintWithPerPixel: (texture, color, canvas) => {
    var context = canvas.getContext("2d");

    var crop = texture._frame.clone();

    var resolution = texture.baseTexture.resolution;
    crop.x *= resolution;
    crop.y *= resolution;
    crop.width *= resolution;
    crop.height *= resolution;
    canvas.width = Math.ceil(crop.width);
    canvas.height = Math.ceil(crop.height);
    context.save();
    context.globalCompositeOperation = "copy";
    context.drawImage(texture.baseTexture.source, crop.x, crop.y, crop.width, crop.height, 0, 0, crop.width, crop.height);
    context.restore();
    var rgbValues = (0, _utils.hex2rgb)(color);
    var r = rgbValues[0];
    var g = rgbValues[1];
    var b = rgbValues[2];
    var pixelData = context.getImageData(0, 0, crop.width, crop.height);
    var pixels = pixelData.data;

    for (var i = 0; i < pixels.length; i += 4) {
      pixels[i + 0] *= r;
      pixels[i + 1] *= g;
      pixels[i + 2] *= b;
    }

    context.putImageData(pixelData, 0, 0);
  },
  roundColor: color => {
    var step = CanvasTinter.cacheStepsPerColorChannel;
    var rgbValues = (0, _utils.hex2rgb)(color);
    rgbValues[0] = Math.min(255, rgbValues[0] / step * step);
    rgbValues[1] = Math.min(255, rgbValues[1] / step * step);
    rgbValues[2] = Math.min(255, rgbValues[2] / step * step);
    return (0, _utils.rgb2hex)(rgbValues);
  },
  cacheStepsPerColorChannel: 8,
  convertTintToImage: false,
  canUseMultiply: (0, _canUseNewCanvasBlendModes.default)(),
  tintMethod: 0
};
CanvasTinter.tintMethod = CanvasTinter.canUseMultiply ? CanvasTinter.tintWithMultiply : CanvasTinter.tintWithPerPixel;
var _default = CanvasTinter;
exports.default = _default;
//# sourceMappingURL=CanvasTinter.js.map