"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.calculateNormalizedScreenSpaceMatrix = calculateNormalizedScreenSpaceMatrix;
exports.calculateScreenSpaceMatrix = calculateScreenSpaceMatrix;
exports.calculateSpriteMatrix = calculateSpriteMatrix;

var _math = require("../../../math");

function calculateScreenSpaceMatrix(outputMatrix, filterArea, textureSize) {
  var mappedMatrix = outputMatrix.identity();
  mappedMatrix.translate(filterArea.x / textureSize.width, filterArea.y / textureSize.height);
  mappedMatrix.scale(textureSize.width, textureSize.height);
  return mappedMatrix;
}

function calculateNormalizedScreenSpaceMatrix(outputMatrix, filterArea, textureSize) {
  var mappedMatrix = outputMatrix.identity();
  mappedMatrix.translate(filterArea.x / textureSize.width, filterArea.y / textureSize.height);
  var translateScaleX = textureSize.width / filterArea.width;
  var translateScaleY = textureSize.height / filterArea.height;
  mappedMatrix.scale(translateScaleX, translateScaleY);
  return mappedMatrix;
}

function calculateSpriteMatrix(outputMatrix, filterArea, textureSize, sprite) {
  var orig = sprite._texture.orig;
  var mappedMatrix = outputMatrix.set(textureSize.width, 0, 0, textureSize.height, filterArea.x, filterArea.y);
  var worldTransform = sprite.worldTransform.copy(_math.Matrix.TEMP_MATRIX);
  worldTransform.invert();
  mappedMatrix.prepend(worldTransform);
  mappedMatrix.scale(1.0 / orig.width, 1.0 / orig.height);
  mappedMatrix.translate(sprite.anchor.x, sprite.anchor.y);
  return mappedMatrix;
}
//# sourceMappingURL=filterTransforms.js.map