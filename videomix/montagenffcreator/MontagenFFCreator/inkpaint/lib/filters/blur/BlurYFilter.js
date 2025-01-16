"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var settings = _interopRequireWildcard(require("../../settings"));

var _Filter = _interopRequireDefault(require("../../renderers/webgl/filters/Filter"));

var _generateBlurVertSource = _interopRequireDefault(require("./generateBlurVertSource"));

var _generateBlurFragSource = _interopRequireDefault(require("./generateBlurFragSource"));

var _getMaxBlurKernelSize = _interopRequireDefault(require("./getMaxBlurKernelSize"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _getRequireWildcardCache(nodeInterop) { if (typeof WeakMap !== "function") return null; var cacheBabelInterop = new WeakMap(); var cacheNodeInterop = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(nodeInterop) { return nodeInterop ? cacheNodeInterop : cacheBabelInterop; })(nodeInterop); }

function _interopRequireWildcard(obj, nodeInterop) { if (!nodeInterop && obj && obj.__esModule) { return obj; } if (obj === null || typeof obj !== "object" && typeof obj !== "function") { return { default: obj }; } var cache = _getRequireWildcardCache(nodeInterop); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (key !== "default" && Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj.default = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

class BlurYFilter extends _Filter.default {
  constructor(strength, quality, resolution, kernelSize) {
    kernelSize = kernelSize || 5;
    var vertSrc = (0, _generateBlurVertSource.default)(kernelSize, false);
    var fragSrc = (0, _generateBlurFragSource.default)(kernelSize);
    super( // vertex shader
    vertSrc, // fragment shader
    fragSrc);
    this.resolution = resolution || settings.RESOLUTION;
    this._quality = 0;
    this.quality = quality || 4;
    this.strength = strength || 8;
    this.firstRun = true;
  }

  apply(filterManager, input, output, clear) {
    if (this.firstRun) {
      var gl = filterManager.renderer.gl;
      var kernelSize = (0, _getMaxBlurKernelSize.default)(gl);
      this.vertexSrc = (0, _generateBlurVertSource.default)(kernelSize, false);
      this.fragmentSrc = (0, _generateBlurFragSource.default)(kernelSize);
      this.firstRun = false;
    }

    this.uniforms.strength = 1 / output.size.height * (output.size.height / input.size.height);
    this.uniforms.strength *= this.strength;
    this.uniforms.strength /= this.passes;

    if (this.passes === 1) {
      filterManager.applyFilter(this, input, output, clear);
    } else {
      var renderTarget = filterManager.getRenderTarget(true);
      var flip = input;
      var flop = renderTarget;

      for (var i = 0; i < this.passes - 1; i++) {
        filterManager.applyFilter(this, flip, flop, true);
        var temp = flop;
        flop = flip;
        flip = temp;
      }

      filterManager.applyFilter(this, flip, output, clear);
      filterManager.returnRenderTarget(renderTarget);
    }
  }
  /**
   * Sets the strength of both the blur.
   *
   * @member {number}
   * @default 2
   */


  get blur() {
    return this.strength;
  }

  set blur(value) {
    this.padding = Math.abs(value) * 2;
    this.strength = value;
  }
  /**
   * Sets the quality of the blur by modifying the number of passes. More passes means higher
   * quaility bluring but the lower the performance.
   *
   * @member {number}
   * @default 4
   */


  get quality() {
    return this._quality;
  }

  set quality(value) {
    this._quality = value;
    this.passes = value;
  }

}

exports.default = BlurYFilter;
//# sourceMappingURL=BlurYFilter.js.map