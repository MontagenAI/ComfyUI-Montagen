"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
Object.defineProperty(exports, "EventEmitter", {
  enumerable: true,
  get: function get() {
    return _eventemitter.default;
  }
});
exports.correctBlendMode = correctBlendMode;
exports.decomposeDataUri = decomposeDataUri;
Object.defineProperty(exports, "earcut", {
  enumerable: true,
  get: function get() {
    return _earcut.default;
  }
});
exports.getResolutionOfUrl = getResolutionOfUrl;
exports.getSvgSize = getSvgSize;
exports.getUrlFileExt = getUrlFileExt;
exports.hex2rgb = hex2rgb;
exports.hex2string = hex2string;
exports.inherit = inherit;
exports.mixins = void 0;
Object.defineProperty(exports, "pluginTarget", {
  enumerable: true,
  get: function get() {
    return _pluginTarget.default;
  }
});
exports.premultiplyBlendMode = void 0;
exports.premultiplyRgba = premultiplyRgba;
exports.premultiplyTint = premultiplyTint;
exports.premultiplyTintToRgba = premultiplyTintToRgba;
exports.removeItems = removeItems;
exports.rgb2hex = rgb2hex;
exports.rgb2hsl = rgb2hsl;
exports.sign = sign;
exports.str2rgb = str2rgb;
exports.uid = uid;
exports.uuidvx = uuidvx;

var _earcut = _interopRequireDefault(require("earcut"));

var mixins = _interopRequireWildcard(require("./mixin"));

exports.mixins = mixins;

var _eventemitter = _interopRequireDefault(require("eventemitter3"));

var _pluginTarget = _interopRequireDefault(require("./pluginTarget"));

var _const = require("../const");

var _mapPremultipliedBlendModes = _interopRequireDefault(require("./mapPremultipliedBlendModes"));

function _getRequireWildcardCache(nodeInterop) { if (typeof WeakMap !== "function") return null; var cacheBabelInterop = new WeakMap(); var cacheNodeInterop = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(nodeInterop) { return nodeInterop ? cacheNodeInterop : cacheBabelInterop; })(nodeInterop); }

function _interopRequireWildcard(obj, nodeInterop) { if (!nodeInterop && obj && obj.__esModule) { return obj; } if (obj === null || typeof obj !== "object" && typeof obj !== "function") { return { default: obj }; } var cache = _getRequireWildcardCache(nodeInterop); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (key !== "default" && Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj.default = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var nextUid = 0;

function removeItems(arr, startIdx, removeCount) {
  var length = arr.length;
  if (startIdx >= length || removeCount <= 0 || startIdx < 0) return;
  removeCount = startIdx + removeCount > length ? length - startIdx : removeCount;
  var len = length - removeCount;

  for (var i = startIdx; i < len; ++i) {
    arr[i] = arr[i + removeCount];
  }

  arr.length = len;
}

function uid() {
  return ++nextUid;
}

function uuidvx() {
  return "xxxxxxxx-xxxx-4xxx-yxxx".replace(/[xy]/g, c => {
    var r = Math.random() * 16 | 0;
    var v = c === "x" ? r : r & 0x3 | 0x8;
    return v.toString(16);
  });
}

function hex2rgb(hex, out) {
  out = out || [];
  out[0] = (hex >> 16 & 0xff) / 255;
  out[1] = (hex >> 8 & 0xff) / 255;
  out[2] = (hex & 0xff) / 255;
  return out;
}

function hex2string(hex) {
  hex = hex.toString(16);
  hex = "000000".substr(0, 6 - hex.length) + hex;
  return "#" + hex;
}

function rgb2hex(rgb) {
  return (rgb[0] * 255 << 16) + (rgb[1] * 255 << 8) + (rgb[2] * 255 | 0);
}

function str2rgb(h, base) {
  if (base === void 0) {
    base = 1;
  }

  var r, g, b;

  if (h.length === 4) {
    r = "0x" + h[1] + h[1];
    g = "0x" + h[2] + h[2];
    b = "0x" + h[3] + h[3];
  } else if (h.length === 7) {
    r = "0x" + h[1] + h[2];
    g = "0x" + h[3] + h[4];
    b = "0x" + h[5] + h[6];
  }

  return [Number(r) / base, Number(g) / base, Number(b) / base];
}

function rgb2hsl(r, g, b) {
  r /= 255;
  g /= 255;
  b /= 255;
  var max = Math.max(r, g, b),
      min = Math.min(r, g, b);
  var h,
      s,
      l = (max + min) / 2;

  if (max == min) {
    h = s = 0; // achromatic
  } else {
    var d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r:
        h = (g - b) / d + (g < b ? 6 : 0);
        break;

      case g:
        h = (b - r) / d + 2;
        break;

      case b:
        h = (r - g) / d + 4;
        break;
    }

    h /= 6;
  }

  h *= 360;
  s *= 100;
  l *= 100;
  return [h, s, l];
}

function getResolutionOfUrl(url, defaultValue) {
  return defaultValue !== undefined ? defaultValue : 1;
}

function decomposeDataUri(dataUri) {
  var dataUriMatch = _const.DATA_URI.exec(dataUri);

  if (dataUriMatch) {
    return {
      mediaType: dataUriMatch[1] ? dataUriMatch[1].toLowerCase() : undefined,
      subType: dataUriMatch[2] ? dataUriMatch[2].toLowerCase() : undefined,
      charset: dataUriMatch[3] ? dataUriMatch[3].toLowerCase() : undefined,
      encoding: dataUriMatch[4] ? dataUriMatch[4].toLowerCase() : undefined,
      data: dataUriMatch[5]
    };
  }

  return undefined;
}

function getUrlFileExt(url) {
  var extension = _const.URL_FILE_EXTENSION.exec(url);

  if (extension) return extension[1].toLowerCase();
  return undefined;
}

function getSvgSize(svgString) {
  var sizeMatch = _const.SVG_SIZE.exec(svgString);

  var size = {};

  if (sizeMatch) {
    size[sizeMatch[1]] = Math.round(parseFloat(sizeMatch[3]));
    size[sizeMatch[5]] = Math.round(parseFloat(sizeMatch[7]));
  }

  return size;
}

function sign(n) {
  if (n === 0) return 0;
  return n < 0 ? -1 : 1;
}

var premultiplyBlendMode = (0, _mapPremultipliedBlendModes.default)();
exports.premultiplyBlendMode = premultiplyBlendMode;

function correctBlendMode(blendMode, premultiplied) {
  return premultiplyBlendMode[premultiplied ? 1 : 0][blendMode];
}

function premultiplyTint(tint, alpha) {
  if (alpha === 1.0) {
    return (alpha * 255 << 24) + tint;
  }

  if (alpha === 0.0) {
    return 0;
  }

  var R = tint >> 16 & 0xff;
  var G = tint >> 8 & 0xff;
  var B = tint & 0xff;
  R = R * alpha + 0.5 | 0;
  G = G * alpha + 0.5 | 0;
  B = B * alpha + 0.5 | 0;
  return (alpha * 255 << 24) + (R << 16) + (G << 8) + B;
}

function premultiplyRgba(rgb, alpha, out, premultiply) {
  out = out || new Float32Array(4);

  if (premultiply || premultiply === undefined) {
    out[0] = rgb[0] * alpha;
    out[1] = rgb[1] * alpha;
    out[2] = rgb[2] * alpha;
  } else {
    out[0] = rgb[0];
    out[1] = rgb[1];
    out[2] = rgb[2];
  }

  out[3] = alpha;
  return out;
}

function premultiplyTintToRgba(tint, alpha, out, premultiply) {
  out = out || new Float32Array(4);
  out[0] = (tint >> 16 & 0xff) / 255.0;
  out[1] = (tint >> 8 & 0xff) / 255.0;
  out[2] = (tint & 0xff) / 255.0;

  if (premultiply || premultiply === undefined) {
    out[0] *= alpha;
    out[1] *= alpha;
    out[2] *= alpha;
  }

  out[3] = alpha;
  return out;
}

function inherit(ClassA, ClassB) {
  for (var k in ClassB.prototype) {
    ClassA.prototype[k] = ClassB.prototype[k];
  }
}
//# sourceMappingURL=index.js.map