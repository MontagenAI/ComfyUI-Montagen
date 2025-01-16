"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Matrix = _interopRequireDefault(require("../math/Matrix"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var tempMat = new _Matrix.default();

class TextureMatrix {
  constructor(texture, clampMargin) {
    this._texture = texture;
    this.mapCoord = new _Matrix.default();
    this.uClampFrame = new Float32Array(4);
    this.uClampOffset = new Float32Array(2);
    this._lastTextureID = -1;
    this.clampOffset = 0;
    this.clampMargin = typeof clampMargin === "undefined" ? 0.5 : clampMargin;
  }

  get texture() {
    return this._texture;
  }

  set texture(value) {
    this._texture = value;
    this._lastTextureID = -1;
  }

  multiplyUvs(uvs, out) {
    if (out === undefined) {
      out = uvs;
    }

    var mat = this.mapCoord;

    for (var i = 0; i < uvs.length; i += 2) {
      var x = uvs[i];
      var y = uvs[i + 1];
      out[i] = x * mat.a + y * mat.c + mat.tx;
      out[i + 1] = x * mat.b + y * mat.d + mat.ty;
    }

    return out;
  }

  update(forceUpdate) {
    var tex = this._texture;

    if (!tex || !tex.valid) {
      return false;
    }

    if (!forceUpdate && this._lastTextureID === tex._updateID) {
      return false;
    }

    this._lastTextureID = tex._updateID;
    var uvs = tex._uvs;
    this.mapCoord.set(uvs.x1 - uvs.x0, uvs.y1 - uvs.y0, uvs.x3 - uvs.x0, uvs.y3 - uvs.y0, uvs.x0, uvs.y0);
    var orig = tex.orig;
    var trim = tex.trim;

    if (trim) {
      tempMat.set(orig.width / trim.width, 0, 0, orig.height / trim.height, -trim.x / trim.width, -trim.y / trim.height);
      this.mapCoord.append(tempMat);
    }

    var texBase = tex.baseTexture;
    var frame = this.uClampFrame;
    var margin = this.clampMargin / texBase.resolution;
    var offset = this.clampOffset;
    frame[0] = (tex._frame.x + margin + offset) / texBase.width;
    frame[1] = (tex._frame.y + margin + offset) / texBase.height;
    frame[2] = (tex._frame.x + tex._frame.width - margin + offset) / texBase.width;
    frame[3] = (tex._frame.y + tex._frame.height - margin + offset) / texBase.height;
    this.uClampOffset[0] = offset / texBase.realWidth;
    this.uClampOffset[1] = offset / texBase.realHeight;
    return true;
  }

}

exports.default = TextureMatrix;
//# sourceMappingURL=TextureMatrix.js.map