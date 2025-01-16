"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _settings = _interopRequireDefault(require("../../settings"));

var _Filter = _interopRequireDefault(require("../../renderers/webgl/filters/Filter"));

var _generateBlurVertSource = _interopRequireDefault(require("./generateBlurVertSource"));

var _generateBlurFragSource = _interopRequireDefault(require("./generateBlurFragSource"));

var _getMaxBlurKernelSize = _interopRequireDefault(require("./getMaxBlurKernelSize"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class BlurXFilter extends _Filter.default {
  constructor(strength, quality, resolution, kernelSize) {
    kernelSize = kernelSize || 5;
    var vertSrc = (0, _generateBlurVertSource.default)(kernelSize, true);
    var fragSrc = (0, _generateBlurFragSource.default)(kernelSize);
    super( // vertex shader
    vertSrc, // fragment shader
    fragSrc);
    this.resolution = resolution || _settings.default.RESOLUTION;
    this._quality = 0;
    this.quality = quality || 4;
    this.strength = strength || 8;
    this.firstRun = true;
  }

  apply(filterManager, input, output, clear) {
    if (this.firstRun) {
      var gl = filterManager.renderer.gl;
      var kernelSize = (0, _getMaxBlurKernelSize.default)(gl);
      this.vertexSrc = (0, _generateBlurVertSource.default)(kernelSize, true);
      this.fragmentSrc = (0, _generateBlurFragSource.default)(kernelSize);
      this.firstRun = false;
    }

    this.uniforms.strength = 1 / output.size.width * (output.size.width / input.size.width); // screen space!

    this.uniforms.strength *= this.strength;
    this.uniforms.strength /= this.passes; // / this.passes//Math.pow(1, this.passes);

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

  get blur() {
    return this.strength;
  }

  set blur(value) {
    this.padding = Math.abs(value) * 2;
    this.strength = value;
  }

  get quality() {
    return this._quality;
  }

  set quality(value) {
    this._quality = value;
    this.passes = value;
  }

}

exports.default = BlurXFilter;
//# sourceMappingURL=BlurXFilter.js.map