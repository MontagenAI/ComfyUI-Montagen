"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _CanvasRenderer = _interopRequireDefault(require("../../renderers/canvas/CanvasRenderer"));

var _const = require("../../const");

var _math = require("../../math");

var _Image = _interopRequireDefault(require("../../polyfill/Image"));

var _CanvasTinter = _interopRequireDefault(require("./CanvasTinter"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var canvasRenderWorldTransform = new _math.Matrix();

class CanvasSpriteRenderer {
  constructor(renderer) {
    this.renderer = renderer;
  }

  render(sprite) {
    var texture = sprite._texture;
    var renderer = this.renderer;
    var width = texture._frame.width;
    var height = texture._frame.height;
    var wt = sprite.transform.worldTransform;
    var dx = 0;
    var dy = 0;

    if (texture.orig.width <= 0 || texture.orig.height <= 0 || !texture.baseTexture.source) {
      return;
    }

    renderer.setBlendMode(sprite.blendMode); //  Ignore null sources

    if (texture.valid) {
      renderer.context.globalAlpha = sprite.worldAlpha;
      var smoothingEnabled = texture.baseTexture.scaleMode === _const.SCALE_MODES.LINEAR;

      if (renderer.smoothProperty && renderer.context[renderer.smoothProperty] !== smoothingEnabled) {
        renderer.context[renderer.smoothProperty] = smoothingEnabled;
      } // if (texture.trim) {
      //   dx =
      //     texture.trim.width / 2 +
      //     texture.trim.x -
      //     sprite.anchor.x * texture.orig.width;
      //   dy =
      //     texture.trim.height / 2 +
      //     texture.trim.y -
      //     sprite.anchor.y * texture.orig.height;
      // } else {
      //   dx = (0.5 - sprite.anchor.x) * texture.orig.width;
      //   dy = (0.5 - sprite.anchor.y) * texture.orig.height;
      // }


      dx = (0.5 - sprite.anchor.x) * texture.orig.width;
      dy = (0.5 - sprite.anchor.y) * texture.orig.height;

      if (texture.rotate) {
        wt.copy(canvasRenderWorldTransform);
        wt = canvasRenderWorldTransform;

        _math.GroupD8.matrixAppendRotationInv(wt, texture.rotate, dx, dy); // the anchor has already been applied above, so lets set it to zero


        dx = 0;
        dy = 0;
      }

      dx -= width / 2;
      dy -= height / 2; // Allow for pixel rounding

      if (renderer.roundPixels) {
        renderer.context.setTransform(wt.a, wt.b, wt.c, wt.d, wt.tx * renderer.resolution | 0, wt.ty * renderer.resolution | 0);
        dx = dx | 0;
        dy = dy | 0;
      } else {
        renderer.context.setTransform(wt.a, wt.b, wt.c, wt.d, wt.tx * renderer.resolution, wt.ty * renderer.resolution);
      }

      var resolution = texture.baseTexture.resolution;
      this.adaptedNodeCanvas(texture.baseTexture);
      var sx, sy, dw, dh;
      sx = texture._frame.x;
      sy = texture._frame.y;

      if (texture.trim) {
        dw = texture.trim.width;
        dh = texture.trim.height;
      } else {
        dw = width;
        dh = height;
      }

      renderer.context.drawImage(texture.baseTexture.source, sx * resolution, sy * resolution, width * resolution, height * resolution, dx * renderer.resolution, dy * renderer.resolution, dw * renderer.resolution, dh * renderer.resolution); // 0 0 100 100 -50 -50 100 100
    }
  }

  adaptedNodeCanvas(baseTexture) {
    if (!baseTexture.source) return;
    if (baseTexture.source.isPSCanvas) return;

    if (this.isImageData(baseTexture.source)) {
      var {
        source,
        width,
        height
      } = baseTexture;
      baseTexture.source = _Image.default.convertToCanvas(source, width, height);
    }
  }

  isImageData(data) {
    if (!data) return false;
    if (data.width && data.height && data.data && data.data.length) return true;
    return false;
  }

  destroy() {
    this.renderer = null;
  }

}

exports.default = CanvasSpriteRenderer;

_CanvasRenderer.default.registerPlugin("sprite", CanvasSpriteRenderer);
//# sourceMappingURL=CanvasSpriteRenderer.js.map