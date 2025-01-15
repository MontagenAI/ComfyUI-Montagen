import Filter from "../../renderers/webgl/filters/Filter";
import { readFileSync } from "fs";
import { join } from "path";
import { rgb2hsl, str2rgb } from "../../utils";
export default class ChromaFilter extends Filter {
  constructor(rgbColor, similarity=0.3, smoothness=0.1, saturation=0.1, shadowness=0.5) {
    super(
      // vertex shader
      readFileSync(join(__dirname, "../fragments/default.vert"), "utf8"),
      // fragment shader
      readFileSync(join(__dirname, "./chroma.frag"), "utf8")
    );

    this.color = rgbColor;
    this.similarity = Math.max(similarity, 0.001);
    this.smoothness = Math.max(smoothness, 0.001);
    this.saturation = Math.max(saturation, 0.001);
    this.shadowness = Math.max(shadowness, 0.001);
    this.glShaderKey = "chroma";
  }

  get color() {
    return this.uniforms.uColor;
  }

  set color(value) {
    this.uniforms.uColor = value;
  }

  get similarity() {
    return this.uniforms.uSimilarity;
  }

  set similarity(value) {
    this.uniforms.uSimilarity = value;
  }

  get smoothness() {
    return this.uniforms.uSmoothness;
  }

  set smoothness(value) {
    this.uniforms.uSmoothness = value;
  }

  get saturation() {
    return this.uniforms.uSaturation;
  }

  set saturation(value) {
    this.uniforms.uSaturation = value;
  }

  get shadowness() {
    return this.uniforms.uShadowness;
  }

  set shadowness(value) {
    this.uniforms.uShadowness = value;
  }
  
}
