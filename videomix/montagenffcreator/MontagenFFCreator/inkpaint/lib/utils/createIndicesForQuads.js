"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = createIndicesForQuads;

function createIndicesForQuads(size) {
  var totalIndices = size * 6;
  var indices = new Uint16Array(totalIndices);

  for (var i = 0, j = 0; i < totalIndices; i += 6, j += 4) {
    indices[i + 0] = j + 0;
    indices[i + 1] = j + 1;
    indices[i + 2] = j + 2;
    indices[i + 3] = j + 0;
    indices[i + 4] = j + 2;
    indices[i + 5] = j + 3;
  }

  return indices;
}
//# sourceMappingURL=createIndicesForQuads.js.map