"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Filter = _interopRequireDefault(require("../../renderers/webgl/filters/Filter"));

var _path = require("path");

var _Matrix = _interopRequireDefault(require("../../math/Matrix"));

var _TextureMatrix = _interopRequireDefault(require("../../textures/TextureMatrix"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class SimpleFilter extends _Filter.default {
  constructor(opt) {
    var {
      key,
      vert,
      frag,
      render,
      vars
    } = opt || {};
    if (!render) render = "vec4 render(sampler2D tex, vec2 uv, vec4 bg, vec4 mask, float alpha) { return bg; }";
    if (!vert) vert = "attribute vec2 aVertexPosition;\nattribute vec2 aTextureCoord;\n\nuniform mat3 projectionMatrix;\nuniform mat3 filterMatrix;\n\nvarying vec2 vTextureCoord;\nvarying vec2 vFilterCoord;\n\nvoid main(void)\n{\n   gl_Position = vec4((projectionMatrix * vec3(aVertexPosition, 1.0)).xy, 0.0, 1.0);\n   vFilterCoord = ( filterMatrix * vec3( aTextureCoord, 1.0)  ).xy;\n   vTextureCoord = aTextureCoord;\n}";

    if (!frag) {
      var uniforms = [];

      if (vars) {
        for (var [_key, val] of Object.entries(vars)) {
          if (!_key) continue;
          var type = Array.isArray(val) ? "vec" + val.length : 'float';
          uniforms.push("uniform " + type + " " + _key + ";");
        }
      }

      frag = "varying vec2 vTextureCoord;\nvarying vec2 vFilterCoord; // for mask\n\nuniform sampler2D uSampler;\nuniform sampler2D uMask;\n\nuniform vec2 uMaskAnchor;\nuniform vec2 uMaskSize;\nuniform float uMaskRotation;\n\nuniform vec4 maskClamp;\nuniform vec4 filterArea;\nuniform vec4 filterClamp;\nuniform vec2 uFrameSize;\n\nuniform bool useMask;\nuniform bool useBinaryMask;\nuniform bool useReverseMask;\n\nuniform float uStart;\nuniform float uDuration;\n\n${uniforms}\n\n${render}\n\nvoid main(void) {\n  vec4 bg = texture2D(uSampler, vTextureCoord);\n  vec4 mask = vec4(1.0);\n  float alpha = 1.0;\n  if (useMask) {\n    float clip = step(3.5,\n      step(maskClamp.x, vFilterCoord.x) +\n      step(maskClamp.y, vFilterCoord.y) +\n      step(vFilterCoord.x, maskClamp.z) +\n      step(vFilterCoord.y, maskClamp.w));\n    mask = texture2D(uMask, vFilterCoord);\n    alpha = clamp(dot(mask.rgb, vec3(1.0, 1.0, 1.0)) * clip, 0.0, 1.0);\n    if (useBinaryMask) alpha = step(0.01, alpha);\n    if (useReverseMask) alpha = 1.0 - alpha;\n  }\n  vec4 color = render(uSampler, vTextureCoord, bg, mask, alpha);\n  color = mix(bg, color, alpha);\n  gl_FragColor = color;\n}\n";
      frag = frag.replace('${uniforms}', uniforms.join("\n")).replace('${render}', render);
    }

    super(vert, frag);
    if (key) this.glShaderKey = key;
    this.vars = vars;
    this._maskMatrix = new _Matrix.default();
  }

  apply(filterManager, input, output, clear) {
    if (this.uniforms.uFrameSize) {
      this.uniforms.uFrameSize[0] = input.sourceFrame.width;
      this.uniforms.uFrameSize[1] = input.sourceFrame.height;
    }

    if (this.uniforms.filterMatrix !== undefined && this._mask) {
      this.uniforms.filterMatrix = filterManager.calculateSpriteMatrix(this._maskMatrix, this._mask);
    }

    if (this._mask) {
      this.uniforms.uMaskAnchor = [this._mask.x, this._mask.y];
      this.uniforms.uMaskSize = [this._mask.width, this._mask.height];
      this.uniforms.uMaskRotation = this._mask.rotation;
      this.uniforms.useBinaryMask = !!this._mask.binaryMask;
      this.uniforms.useReverseMask = !!this._mask.reverseMask;
    }

    super.apply(filterManager, input, output, clear);
  }

  set vars(vars) {
    this._vars = vars;
    if (!vars) return;

    for (var [key, val] of Object.entries(vars)) {
      if (!key) continue;
      this.uniforms[key] = val;
    }
  }

  get vars() {
    return this._vars;
  }

  get mask() {
    return this._mask;
  }

  set mask(mask) {
    this._mask = mask;

    if (this.uniforms.uMask !== undefined) {
      if (mask) {
        var tex = mask.texture;

        if (!tex.transform) {
          // margin = 0.0, let it bleed a bit, shader code becomes easier
          // assuming that atlas textures were made with 1-pixel padding
          tex.transform = new _TextureMatrix.default(tex, 0.0);
        }

        tex.transform.update();
        this.uniforms.uMask = tex;
        this.uniforms.useMask = true;
        this.uniforms.maskClamp = tex.transform.uClampFrame;
      } else {
        this.uniforms.useMask = false;
      }
    }
  }

  setTime(start, duration) {
    this.uniforms.uStart = start;
    this.uniforms.uDuration = duration;
  }

}

exports.default = SimpleFilter;
//# sourceMappingURL=SimpleFilter.js.map