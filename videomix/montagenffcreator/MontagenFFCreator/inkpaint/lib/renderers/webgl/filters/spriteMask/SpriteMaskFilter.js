"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Filter = _interopRequireDefault(require("../Filter"));

var _math = require("../../../../math");

var _path = require("path");

var _TextureMatrix = _interopRequireDefault(require("../../../../textures/TextureMatrix"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class SpriteMaskFilter extends _Filter.default {
  /**
   * @param {InkPaint.Sprite} sprite - the target sprite
   */
  constructor(sprite) {
    var maskMatrix = new _math.Matrix();
    super("attribute vec2 aVertexPosition;\nattribute vec2 aTextureCoord;\n\nuniform mat3 projectionMatrix;\nuniform mat3 otherMatrix;\n\nvarying vec2 vMaskCoord;\nvarying vec2 vTextureCoord;\n\nvoid main(void)\n{\n    gl_Position = vec4((projectionMatrix * vec3(aVertexPosition, 1.0)).xy, 0.0, 1.0);\n\n    vTextureCoord = aTextureCoord;\n    vMaskCoord = ( otherMatrix * vec3( aTextureCoord, 1.0)  ).xy;\n}\n", "varying vec2 vMaskCoord;\nvarying vec2 vTextureCoord;\n\nuniform sampler2D uSampler;\nuniform sampler2D mask;\nuniform float alpha;\nuniform vec4 maskClamp;\n\nuniform bool useBinaryMask;\nuniform bool useReverseMask;\n\nvoid main(void)\n{\n    float clip = step(3.5,\n        step(maskClamp.x, vMaskCoord.x) +\n        step(maskClamp.y, vMaskCoord.y) +\n        step(vMaskCoord.x, maskClamp.z) +\n        step(vMaskCoord.y, maskClamp.w));\n\n    vec4 original = texture2D(uSampler, vTextureCoord);\n    vec4 mask = texture2D(mask, vMaskCoord);\n    float a = clamp(dot(mask.rgb, vec3(1.0, 1.0, 1.0)) * alpha * clip, 0.0, 1.0);\n    if (useBinaryMask) a = step(0.01, alpha);\n    if (useReverseMask) a = 1.0 - a;\n    original *= a;\n    gl_FragColor = original;\n}\n");
    sprite.renderable = false;
    this.maskSprite = sprite;
    this.maskMatrix = maskMatrix;
  }
  /**
   * Applies the filter
   *
   * @param {InkPaint.FilterManager} filterManager - The renderer to retrieve the filter from
   * @param {InkPaint.RenderTarget} input - The input render target.
   * @param {InkPaint.RenderTarget} output - The target to output to.
   * @param {boolean} clear - Should the output be cleared before rendering to it
   */


  apply(filterManager, input, output, clear) {
    var maskSprite = this.maskSprite;
    var tex = this.maskSprite.texture;
    if (!tex.valid) return;

    if (!tex.transform) {
      // margin = 0.0, let it bleed a bit, shader code becomes easier
      // assuming that atlas textures were made with 1-pixel padding
      tex.transform = new _TextureMatrix.default(tex, 0.0);
    }

    tex.transform.update();
    this.uniforms.mask = tex;
    this.uniforms.useBinaryMask = !!maskSprite.binaryMask;
    this.uniforms.useReverseMask = !!maskSprite.reverseMask;
    this.uniforms.otherMatrix = filterManager.calculateSpriteMatrix(this.maskMatrix, maskSprite).prepend(tex.transform.mapCoord);
    this.uniforms.alpha = maskSprite.worldAlpha;
    this.uniforms.maskClamp = tex.transform.uClampFrame;
    filterManager.applyFilter(this, input, output, clear);
  }

}

exports.default = SpriteMaskFilter;
//# sourceMappingURL=SpriteMaskFilter.js.map