"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = checkMaxIfStatmentsInShader;
var fragTemplate = ["precision mediump float;", "void main(void){", "float test = 0.1;", "%forloop%", "gl_FragColor = vec4(0.0);", "}"].join("\n");

function checkMaxIfStatmentsInShader(maxIfs, gl) {
  var shader = gl.createShader(gl.FRAGMENT_SHADER);

  while (true) {
    var fragmentSrc = fragTemplate.replace(/%forloop%/gi, generateIfTestSrc(maxIfs));
    gl.shaderSource(shader, fragmentSrc);
    gl.compileShader(shader);

    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      maxIfs = maxIfs / 2 | 0;
    } else {
      break;
    }
  }

  return maxIfs;
}

function generateIfTestSrc(maxIfs) {
  var src = "";

  for (var i = 0; i < maxIfs; ++i) {
    if (i > 0) {
      src += "\nelse ";
    }

    if (i < maxIfs - 1) {
      src += "if(test == " + i + ".0){}";
    }
  }

  return src;
}
//# sourceMappingURL=checkMaxIfStatmentsInShader.js.map