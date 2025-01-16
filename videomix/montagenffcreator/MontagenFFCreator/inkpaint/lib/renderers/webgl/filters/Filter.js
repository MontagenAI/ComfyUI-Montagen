"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _extractUniformsFromSrc = _interopRequireDefault(require("./extractUniformsFromSrc"));

var _utils = require("../../../utils");

var _const = require("../../../const");

var _settings = _interopRequireDefault(require("../../../settings"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var SOURCE_KEY_MAP = {};

class Filter {
  constructor(vertexSrc, fragmentSrc, uniformData) {
    this.vertexSrc = vertexSrc || Filter.defaultVertexSrc;
    this.fragmentSrc = fragmentSrc || Filter.defaultFragmentSrc;
    this._blendMode = _const.BLEND_MODES.NORMAL;
    this.uniformData = uniformData || (0, _extractUniformsFromSrc.default)(this.vertexSrc, this.fragmentSrc, "projectionMatrix|uSampler");
    this.uniforms = {};

    for (var i in this.uniformData) {
      this.uniforms[i] = this.uniformData[i].value;

      if (this.uniformData[i].type) {
        this.uniformData[i].type = this.uniformData[i].type.toLowerCase();
      }
    }

    this.glShaders = {};

    if (!SOURCE_KEY_MAP[this.vertexSrc + this.fragmentSrc]) {
      SOURCE_KEY_MAP[this.vertexSrc + this.fragmentSrc] = (0, _utils.uid)();
    }

    this.glShaderKey = SOURCE_KEY_MAP[this.vertexSrc + this.fragmentSrc];
    this.padding = 4;
    this.resolution = _settings.default.FILTER_RESOLUTION;
    this.enabled = true;
    this.autoFit = true;
  }

  apply(filterManager, input, output, clear, currentState) {
    filterManager.applyFilter(this, input, output, clear);
  }

  get blendMode() {
    return this._blendMode;
  }

  set blendMode(value) {
    this._blendMode = value;
  }

  static get defaultVertexSrc() {
    return ["attribute vec2 aVertexPosition;", "attribute vec2 aTextureCoord;", "uniform mat3 projectionMatrix;", "uniform mat3 filterMatrix;", "varying vec2 vTextureCoord;", "varying vec2 vFilterCoord;", "void main(void){", "   gl_Position = vec4((projectionMatrix * vec3(aVertexPosition, 1.0)).xy, 0.0, 1.0);", "   vFilterCoord = ( filterMatrix * vec3( aTextureCoord, 1.0)  ).xy;", "   vTextureCoord = aTextureCoord ;", "}"].join("\n");
  }

  static get defaultFragmentSrc() {
    return ["varying vec2 vTextureCoord;", "varying vec2 vFilterCoord;", "uniform sampler2D uSampler;", "uniform sampler2D filterSampler;", "void main(void){", "   vec4 masky = texture2D(filterSampler, vFilterCoord);", "   vec4 sample = texture2D(uSampler, vTextureCoord);", "   vec4 color;", "   if(mod(vFilterCoord.x, 1.0) > 0.5)", "   {", "     color = vec4(1.0, 0.0, 0.0, 1.0);", "   }", "   else", "   {", "     color = vec4(0.0, 1.0, 0.0, 1.0);", "   }", // '   gl_FragColor = vec4(mod(vFilterCoord.x, 1.5), vFilterCoord.y,0.0,1.0);',
    "   gl_FragColor = mix(sample, masky, 0.5);", "   gl_FragColor *= sample.a;", "}"].join("\n");
  }

}

exports.default = Filter;
//# sourceMappingURL=Filter.js.map