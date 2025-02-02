"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = extractUniformsFromSrc;

var _pixiGlCore = _interopRequireDefault(require("pixi-gl-core"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var defaultValue = _pixiGlCore.default.shader.defaultValue;

function extractUniformsFromSrc(vertexSrc, fragmentSrc, mask) {
  var vertUniforms = extractUniformsFromString(vertexSrc, mask);
  var fragUniforms = extractUniformsFromString(fragmentSrc, mask);
  return Object.assign(vertUniforms, fragUniforms);
}

function extractUniformsFromString(string) {
  var maskRegex = new RegExp('^(projectionMatrix|uSampler|filterArea|filterClamp)$');
  var uniforms = {};
  var nameSplit; // clean the lines a little - remove extra spaces / tabs etc
  // then split along ';'

  var lines = string.replace(/\s+/g, ' ').split(/\s*[;}]\s*/); // loop through..

  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();

    if (line.indexOf('uniform') > -1) {
      var splitLine = line.split(' ');
      var type = splitLine[1];
      var name = splitLine[2];
      var size = 1;

      if (name.indexOf('[') > -1) {
        // array!
        nameSplit = name.split(/\[|]/);
        name = nameSplit[0];
        size *= Number(nameSplit[1]);
      }

      if (!name.match(maskRegex)) {
        uniforms[name] = {
          value: defaultValue(type, size),
          name,
          type
        };
      }
    }
  }

  return uniforms;
}
//# sourceMappingURL=extractUniformsFromSrc.js.map