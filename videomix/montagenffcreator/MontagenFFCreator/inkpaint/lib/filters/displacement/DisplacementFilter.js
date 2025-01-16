"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Filter = _interopRequireDefault(require("../../renderers/webgl/filters/Filter"));

var _Matrix = _interopRequireDefault(require("../../math/Matrix"));

var _Point = _interopRequireDefault(require("../../math/Point"));

var _path = require("path");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class DisplacementFilter extends _Filter.default {
  constructor(sprite, scale) {
    var maskMatrix = new _Matrix.default();
    sprite.renderable = false;
    super( // vertex shader
    "attribute vec2 aVertexPosition;\nattribute vec2 aTextureCoord;\n\nuniform mat3 projectionMatrix;\nuniform mat3 filterMatrix;\n\nvarying vec2 vTextureCoord;\nvarying vec2 vFilterCoord;\n\nvoid main(void)\n{\n   gl_Position = vec4((projectionMatrix * vec3(aVertexPosition, 1.0)).xy, 0.0, 1.0);\n   vFilterCoord = ( filterMatrix * vec3( aTextureCoord, 1.0)  ).xy;\n   vTextureCoord = aTextureCoord;\n}", // fragment shader
    "varying vec2 vFilterCoord;\nvarying vec2 vTextureCoord;\n\nuniform vec2 scale;\n\nuniform sampler2D uSampler;\nuniform sampler2D mapSampler;\n\nuniform vec4 filterArea;\nuniform vec4 filterClamp;\n\nvoid main(void)\n{\n  vec4 map =  texture2D(mapSampler, vFilterCoord);\n\n  map -= 0.5;\n  map.xy *= scale / filterArea.xy;\n\n  gl_FragColor = texture2D(uSampler, clamp(vec2(vTextureCoord.x + map.x, vTextureCoord.y + map.y), filterClamp.xy, filterClamp.zw));\n}\n");
    this.maskSprite = sprite;
    this.maskMatrix = maskMatrix;
    this.uniforms.mapSampler = sprite._texture;
    this.uniforms.filterMatrix = maskMatrix;
    this.uniforms.scale = {
      x: 1,
      y: 1
    };

    if (scale === null || scale === undefined) {
      scale = 20;
    }

    this.setScale(scale, scale);
  }

  setScale(x, y) {
    this.scale = new _Point.default(x, y);
  }

  apply(filterManager, input, output) {
    this.uniforms.filterMatrix = filterManager.calculateSpriteMatrix(this.maskMatrix, this.maskSprite);
    this.uniforms.scale.x = this.scale.x;
    this.uniforms.scale.y = this.scale.y;
    super.apply(filterManager, input, output);
  }

  get map() {
    return this.uniforms.mapSampler;
  }

  set map(value) {
    this.uniforms.mapSampler = value;
  }

}

exports.default = DisplacementFilter;
//# sourceMappingURL=DisplacementFilter.js.map