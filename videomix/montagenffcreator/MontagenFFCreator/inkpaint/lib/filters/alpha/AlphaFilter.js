"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _settings = _interopRequireDefault(require("../../settings"));

var _Filter = _interopRequireDefault(require("../../renderers/webgl/filters/Filter"));

var _path = require("path");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class AlphaFilter extends _Filter.default {
  constructor(alpha) {
    if (alpha === void 0) {
      alpha = 1.0;
    }

    super( // vertex shader
    "attribute vec2 aVertexPosition;\nattribute vec2 aTextureCoord;\n\nuniform mat3 projectionMatrix;\n\nvarying vec2 vTextureCoord;\n\nvoid main(void)\n{\n    gl_Position = vec4((projectionMatrix * vec3(aVertexPosition, 1.0)).xy, 0.0, 1.0);\n    vTextureCoord = aTextureCoord;\n}", // fragment shader
    "varying vec2 vTextureCoord;\n\nuniform sampler2D uSampler;\nuniform float uAlpha;\n\nvoid main(void)\n{\n   gl_FragColor = texture2D(uSampler, vTextureCoord) * uAlpha;\n}\n");
    this.alpha = alpha;
    this.glShaderKey = "alpha";
  }
  /**
   * Coefficient for alpha multiplication
   *
   * @member {number}
   * @default 1
   */


  get alpha() {
    return this.uniforms.uAlpha;
  }

  set alpha(value) {
    this.uniforms.uAlpha = value;
  }

}

exports.default = AlphaFilter;
//# sourceMappingURL=AlphaFilter.js.map