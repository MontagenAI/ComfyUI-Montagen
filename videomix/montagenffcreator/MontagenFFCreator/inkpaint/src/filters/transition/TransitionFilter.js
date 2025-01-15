import Filter from "../../renderers/webgl/filters/Filter";
import { readFileSync } from "fs";
import { join } from "path";

export default class TransitionFilter extends Filter {
  constructor(transition) {
    let vert = readFileSync(join(__dirname, "./trans.vert"), "utf8");
    let frag = readFileSync(join(__dirname, "./trans.frag"), "utf8");

    // todo: extractUniformsFromString写的比较烂，需要过滤掉注释
    let glsl = transition.glsl;
    const lines = [];
    for (let line of glsl.split("\n")) {
      line = line.trim();
      if (line.startsWith('//')) continue;
      if (line.startsWith('uniform ')) {
        const words = [];
        for (const word of line.replace(/\s+/g, ' ').split(" ")) {
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
  }

  // apply(filterManager, input, output) {
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
    let unit = 2;
    const { transition, uniforms } = this;
    for (let key in transition.paramsTypes) {
      const value = key in params
        ? params[key]
        : transition.defaultParams[key];
      if (transition.paramsTypes[key] === "sampler2D") {
        if (!value) {
          console.warn(
            "uniform[" +
              key +
              "]: A texture MUST be defined for uniform sampler2D of a texture"
          );
        } else if (typeof value.bind !== "function") {
          throw new Error(
            "uniform[" +
              key +
              "]: A gl-texture2d API-like object was expected"
          );
        } else {
          uniforms[key] = value.bind(unit++);
        }
      } else {
        uniforms[key] = value;
      }
    }
  }

  setSprite(key, sprite) {
    this[`${key}Sprite`] = sprite;
    sprite.renderable = false;
    this.uniforms[`${key}Sampler`] = sprite.texture;
  }

  updateProgress(progress) {
    this.uniforms.progress = progress;
  }
}
