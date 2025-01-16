"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Filter = _interopRequireDefault(require("../../renderers/webgl/filters/Filter"));

var _path = require("path");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class TransitionFilter extends _Filter.default {
  constructor(transition) {
    var vert = "attribute vec2 aVertexPosition;\nattribute vec2 aTextureCoord;\n\nuniform mat3 projectionMatrix;\n\nvarying vec2 vTextureCoord;\nvarying vec2 _uv;\n\nvoid main(void) {\n  vec2 _p = (projectionMatrix * vec3(aVertexPosition, 1.0)).xy;\n  gl_Position = vec4(_p, 0.0, 1.0);\n  vTextureCoord = aTextureCoord;\n  _uv = vec2(0.5, 0.5) * (_p+vec2(1.0, 1.0));\n}";
    var frag = "precision highp float;\n\nvarying vec2 _uv;\n\nuniform float progress;\nuniform float ratio;\nuniform vec2 _offset;\n\nuniform sampler2D fromSampler;\nuniform sampler2D toSampler;\n\nvec4 getColor(sampler2D tex, vec2 uv) {\n  return texture2D(tex, vec2(uv.x + _offset.x, 1.0 - (uv.y + _offset.y)));\n}\n\nvec4 getFromColor(vec2 uv) {\n  return getColor(fromSampler, uv);\n}\n\nvec4 getToColor(vec2 uv) {\n  return getColor(toSampler, uv);\n}\n\n${transitionGlsl}\n\nvoid main(void) {\n  gl_FragColor = transition(_uv - _offset);\n  //gl_FragColor = getFromColor(_uv);\n}\n"; // todo: extractUniformsFromString写的比较烂，需要过滤掉注释

    var glsl = transition.glsl;
    var lines = [];

    for (var line of glsl.split("\n")) {
      line = line.trim();
      if (line.startsWith('//')) continue;

      if (line.startsWith('uniform ')) {
        var words = [];

        for (var word of line.replace(/\s+/g, ' ').split(" ")) {
          if (word.startsWith('//')) break;
          words.push(word);
        }

        lines.push(words.join(' '));
      } else {
        lines.push(line);
      }
    }

    glsl = lines.join("\n");
    frag = frag.replace('${transitionGlsl}', glsl);
    super(vert, frag);
    this.transition = transition;
  } // apply(filterManager, input, output) {
  //   console.log('apply', this.uniforms);
  //   super.apply(filterManager, input, output);
  // }


  get prev() {
    return this.fromSprite;
  }

  get next() {
    return this.toSprite;
  }

  set prev(sprite) {
    this.setSprite('from', sprite);
  }

  set next(sprite) {
    this.setSprite('to', sprite);
  }

  get ratio() {
    return this.uniforms.ratio;
  }

  set ratio(ratio) {
    this.uniforms.ratio = ratio;
  }

  get offset() {
    return this.uniforms._offset;
  }

  set offset(offset) {
    this.uniforms._offset = offset;
  }

  set params(params) {
    var unit = 2;
    var {
      transition,
      uniforms
    } = this;

    for (var key in transition.paramsTypes) {
      var value = key in params ? params[key] : transition.defaultParams[key];

      if (transition.paramsTypes[key] === "sampler2D") {
        if (!value) {
          console.warn("uniform[" + key + "]: A texture MUST be defined for uniform sampler2D of a texture");
        } else if (typeof value.bind !== "function") {
          throw new Error("uniform[" + key + "]: A gl-texture2d API-like object was expected");
        } else {
          uniforms[key] = value.bind(unit++);
        }
      } else {
        uniforms[key] = value;
      }
    }
  }

  setSprite(key, sprite) {
    this[key + "Sprite"] = sprite;
    sprite.renderable = false;
    this.uniforms[key + "Sampler"] = sprite.texture;
  }

  updateProgress(progress) {
    this.uniforms.progress = progress;
  }

}

exports.default = TransitionFilter;
//# sourceMappingURL=TransitionFilter.js.map