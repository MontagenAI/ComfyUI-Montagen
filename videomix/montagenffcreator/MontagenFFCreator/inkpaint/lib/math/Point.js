"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

class Point {
  constructor(x, y) {
    if (x === void 0) {
      x = 0;
    }

    if (y === void 0) {
      y = 0;
    }

    this.x = x;
    this.y = y;
  }

  clone() {
    return new Point(this.x, this.y);
  }

  copy(p) {
    this.set(p.x, p.y);
  }

  equals(p) {
    return p.x === this.x && p.y === this.y;
  }

  set(x, y) {
    this.x = x || 0;
    this.y = y || (y !== 0 ? this.x : 0);
  }

  dot(p) {
    this.x = this.x * p.x;
    this.x = this.y * p.y;
  }

}

exports.default = Point;
//# sourceMappingURL=Point.js.map