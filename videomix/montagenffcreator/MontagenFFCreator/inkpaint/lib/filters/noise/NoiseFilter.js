"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _settings = _interopRequireDefault(require("../../settings"));

var _Filter = _interopRequireDefault(require("../../renderers/webgl/filters/Filter"));

var _path = require("path");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class NoiseFilter extends _Filter.default {
  constructor(noise, seed) {
    if (noise === void 0) {
      noise = 0.5;
    }

    if (seed === void 0) {
      seed = Math.random();
    }

    super( // vertex shader
    "attribute vec2 aVertexPosition;\nattribute vec2 aTextureCoord;\n\nuniform mat3 projectionMatrix;\n\nvarying vec2 vTextureCoord;\n\nvoid main(void)\n{\n    gl_Position = vec4((projectionMatrix * vec3(aVertexPosition, 1.0)).xy, 0.0, 1.0);\n    vTextureCoord = aTextureCoord;\n}", // fragment shader
    "precision highp float;\n\nvarying vec2 vTextureCoord;\nvarying vec4 vColor;\n\nuniform float uNoise;\nuniform float uSeed;\nuniform sampler2D uSampler;\n\nfloat rand(vec2 co)\n{\n    return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);\n}\n\nvoid main()\n{\n    vec4 color = texture2D(uSampler, vTextureCoord);\n    float randomValue = rand(gl_FragCoord.xy * uSeed);\n    float diff = (randomValue - 0.5) * uNoise;\n\n    // Un-premultiply alpha before applying the color matrix. See issue #3539.\n    if (color.a > 0.0) {\n        color.rgb /= color.a;\n    }\n\n    color.r += diff;\n    color.g += diff;\n    color.b += diff;\n\n    // Premultiply alpha again.\n    color.rgb *= color.a;\n\n    gl_FragColor = color;\n}\n");
    this.noise = noise;
    this.seed = seed;
  }

  get noise() {
    return this.uniforms.uNoise;
  }

  set noise(value) {
    this.uniforms.uNoise = value;
  }

  get seed() {
    return this.uniforms.uSeed;
  }

  set seed(value) {
    this.uniforms.uSeed = value;
  }

}

exports.default = NoiseFilter;
//# sourceMappingURL=NoiseFilter.js.map