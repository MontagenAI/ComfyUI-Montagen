"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _settings = _interopRequireDefault(require("../../settings"));

var _Filter = _interopRequireDefault(require("../../renderers/webgl/filters/Filter"));

var _BlurXFilter = _interopRequireDefault(require("./BlurXFilter"));

var _BlurYFilter = _interopRequireDefault(require("./BlurYFilter"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class BlurFilter extends _Filter.default {
  constructor(strength, quality, resolution, kernelSize) {
    super();
    this.blurXFilter = new _BlurXFilter.default(strength, quality, resolution, kernelSize);
    this.blurYFilter = new _BlurYFilter.default(strength, quality, resolution, kernelSize);
    this.padding = 0;
    this.resolution = resolution || _settings.default.RESOLUTION;
    this.quality = quality || 4;
    this.blur = strength || 8;
  }

  apply(filterManager, input, output) {
    var renderTarget = filterManager.getRenderTarget(true);
    this.blurXFilter.apply(filterManager, input, renderTarget, true);
    this.blurYFilter.apply(filterManager, renderTarget, output, false);
    filterManager.returnRenderTarget(renderTarget);
  }
  /**
   * Sets the strength of both the blurX and blurY properties simultaneously
   *
   * @member {number}
   * @default 2
   */


  get blur() {
    return this.blurXFilter.blur;
  }

  set blur(value) {
    this.blurXFilter.blur = this.blurYFilter.blur = value;
    this.padding = Math.max(Math.abs(this.blurXFilter.strength), Math.abs(this.blurYFilter.strength)) * 2;
  }
  /**
   * Sets the number of passes for blur. More passes means higher quaility bluring.
   *
   * @member {number}
   * @default 1
   */


  get quality() {
    return this.blurXFilter.quality;
  }

  set quality(value) {
    this.blurXFilter.quality = this.blurYFilter.quality = value;
  }
  /**
   * Sets the strength of the blurX property
   *
   * @member {number}
   * @default 2
   */


  get blurX() {
    return this.blurXFilter.blur;
  }

  set blurX(value) {
    this.blurXFilter.blur = value;
    this.padding = Math.max(Math.abs(this.blurXFilter.strength), Math.abs(this.blurYFilter.strength)) * 2;
  }
  /**
   * Sets the strength of the blurY property
   *
   * @member {number}
   * @default 2
   */


  get blurY() {
    return this.blurYFilter.blur;
  }

  set blurY(value) {
    this.blurYFilter.blur = value;
    this.padding = Math.max(Math.abs(this.blurXFilter.strength), Math.abs(this.blurYFilter.strength)) * 2;
  }

  get blendMode() {
    return this.blurYFilter._blendMode;
  }

  set blendMode(value) {
    this.blurYFilter._blendMode = value;
  }

}

exports.default = BlurFilter;
//# sourceMappingURL=BlurFilter.js.map