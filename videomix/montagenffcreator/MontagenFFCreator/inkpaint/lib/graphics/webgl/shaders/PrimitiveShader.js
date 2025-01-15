"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Shader = _interopRequireDefault(require("../../../Shader"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class PrimitiveShader extends _Shader.default {
  constructor(gl) {
    super(gl, // vertex shader
    ["attribute vec2 aVertexPosition;", "attribute vec4 aColor;", "uniform mat3 translationMatrix;", "uniform mat3 projectionMatrix;", "uniform float alpha;", "uniform vec3 tint;", "varying vec4 vColor;", "void main(void){", "   gl_Position = vec4((projectionMatrix * translationMatrix * vec3(aVertexPosition, 1.0)).xy, 0.0, 1.0);", "   vColor = aColor * vec4(tint * alpha, alpha);", "}"].join("\n"), // fragment shader
    ["varying vec4 vColor;", "void main(void){", "   gl_FragColor = vColor;", "}"].join("\n"));
  }

}

exports.default = PrimitiveShader;
//# sourceMappingURL=PrimitiveShader.js.map