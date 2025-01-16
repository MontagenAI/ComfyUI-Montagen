import Filter from "../../renderers/webgl/filters/Filter";
import Matrix from "../../math/Matrix";
import Point from "../../math/Point";
import { readFileSync } from "fs";
import { join } from "path";

export default class DisplacementFilter extends Filter {
  constructor(sprite, scale) {
    const maskMatrix = new Matrix();

    sprite.renderable = false;

    super(
      // vertex shader
      readFileSync( join(__dirname, "../fragments/default-filter-matrix.vert"), "utf8"),
      // fragment shader
      readFileSync(join(__dirname, "./displacement.frag"), "utf8")
    );

    this.maskSprite = sprite;
    this.maskMatrix = maskMatrix;

    this.uniforms.mapSampler = sprite._texture;
    this.uniforms.filterMatrix = maskMatrix;
    this.uniforms.scale = { x: 1, y: 1 };

    if (scale === null || scale === undefined) {
      scale = 20;
    }

    this.setScale(scale, scale);
  }

  setScale(x, y) {
    this.scale = new Point(x, y);
  }

  apply(filterManager, input, output) {
    this.uniforms.filterMatrix = filterManager.calculateSpriteMatrix(
      this.maskMatrix,
      this.maskSprite
    );
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
