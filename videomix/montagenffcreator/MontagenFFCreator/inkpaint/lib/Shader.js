"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _pixiGlCore = require("pixi-gl-core");

var _settings = _interopRequireDefault(require("./settings"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function checkPrecision(src, def) {
  if (src instanceof Array) {
    if (src[0].substring(0, 9) !== "precision") {
      var copy = src.slice(0);
      copy.unshift("precision " + def + " float;");
      return copy;
    }
  } else if (src.trim().substring(0, 9) !== "precision") {
    return "precision " + def + " float;\n" + src;
  }

  return src;
}

class Shader extends _pixiGlCore.GLShader {
  constructor(gl, vertexSrc, fragmentSrc, attributeLocations, precision) {
    super(gl, checkPrecision(vertexSrc, precision || _settings.default.PRECISION_VERTEX), checkPrecision(fragmentSrc, precision || _settings.default.PRECISION_FRAGMENT), undefined, attributeLocations);
  }

}

exports.default = Shader;
//# sourceMappingURL=Shader.js.map