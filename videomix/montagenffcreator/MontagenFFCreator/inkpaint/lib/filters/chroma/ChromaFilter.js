"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Filter = _interopRequireDefault(require("../../renderers/webgl/filters/Filter"));

var _path = require("path");

var _utils = require("../../utils");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class ChromaFilter extends _Filter.default {
  constructor(rgbColor, similarity, smoothness, saturation, shadowness) {
    if (similarity === void 0) {
      similarity = 0.3;
    }

    if (smoothness === void 0) {
      smoothness = 0.1;
    }

    if (saturation === void 0) {
      saturation = 0.1;
    }

    if (shadowness === void 0) {
      shadowness = 0.5;
    }

    super( // vertex shader
    "attribute vec2 aVertexPosition;\nattribute vec2 aTextureCoord;\n\nuniform mat3 projectionMatrix;\n\nvarying vec2 vTextureCoord;\n\nvoid main(void)\n{\n    gl_Position = vec4((projectionMatrix * vec3(aVertexPosition, 1.0)).xy, 0.0, 1.0);\n    vTextureCoord = aTextureCoord;\n}", // fragment shader
    "varying vec2 vTextureCoord;\n\nuniform sampler2D uSampler;\nuniform vec3 uColor;\nuniform float uSimilarity;\nuniform float uSmoothness;\nuniform float uSaturation;\nuniform float uShadowness;\n\nvec2 RGBtoUV(vec3 rgb) {\n  return vec2(\n    rgb.r * -0.169 + rgb.g * -0.331 + rgb.b *  0.5    + 0.5,\n    rgb.r *  0.5   + rgb.g * -0.419 + rgb.b * -0.081  + 0.5\n  );\n}\n\nvec4 ProcessChromaKey(vec2 uv) {\n  vec4 rgba = texture2D(uSampler, uv);\n  float chromaDist = distance(RGBtoUV(rgba.rgb), RGBtoUV(uColor));\n\n  float diff = chromaDist - uSimilarity;\n  float alpha = pow(clamp(diff / uSmoothness, 0., 1.), 1.5);\n  rgba *= alpha;\n\n  float sat = pow(clamp(diff / uSaturation, 0., 1.), 1.5);\n  float luma = clamp(rgba.r * 0.2126 + rgba.g * 0.7152 + rgba.b * 0.0722, 0., 1.) * uShadowness;\n  rgba.rgb = mix(vec3(luma, luma, luma), rgba.rgb, sat);\n\n  return rgba;\n}\n\nvoid main(void) {\n  gl_FragColor = ProcessChromaKey(vTextureCoord);\n}\n");
    this.color = rgbColor;
    this.similarity = Math.max(similarity, 0.001);
    this.smoothness = Math.max(smoothness, 0.001);
    this.saturation = Math.max(saturation, 0.001);
    this.shadowness = Math.max(shadowness, 0.001);
    this.glShaderKey = "chroma";
  }

  get color() {
    return this.uniforms.uColor;
  }

  set color(value) {
    this.uniforms.uColor = value;
  }

  get similarity() {
    return this.uniforms.uSimilarity;
  }

  set similarity(value) {
    this.uniforms.uSimilarity = value;
  }

  get smoothness() {
    return this.uniforms.uSmoothness;
  }

  set smoothness(value) {
    this.uniforms.uSmoothness = value;
  }

  get saturation() {
    return this.uniforms.uSaturation;
  }

  set saturation(value) {
    this.uniforms.uSaturation = value;
  }

  get shadowness() {
    return this.uniforms.uShadowness;
  }

  set shadowness(value) {
    this.uniforms.uShadowness = value;
  }

}

exports.default = ChromaFilter;
//# sourceMappingURL=ChromaFilter.js.map