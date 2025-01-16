"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

class ObservablePoint {
  constructor(cb, scope, x, y) {
    if (x === void 0) {
      x = 0;
    }

    if (y === void 0) {
      y = 0;
    }

    this._x = x;
    this._y = y;
    this.cb = cb;
    this.scope = scope;
  }

  clone(cb, scope) {
    if (cb === void 0) {
      cb = null;
    }

    if (scope === void 0) {
      scope = null;
    }

    var _cb = cb || this.cb;

    var _scope = scope || this.scope;

    return new ObservablePoint(_cb, _scope, this._x, this._y);
  }

  set(x, y) {
    var _x = x || 0;

    var _y = y || (y !== 0 ? _x : 0);

    if (this._x !== _x || this._y !== _y) {
      this._x = _x;
      this._y = _y;
      this.cb.call(this.scope);
    }
  }

  copy(point) {
    if (this._x !== point.x || this._y !== point.y) {
      this._x = point.x;
      this._y = point.y;
      this.cb.call(this.scope);
    }
  }

  equals(p) {
    return p.x === this._x && p.y === this._y;
  }

  get x() {
    return this._x;
  }

  set x(value) {
    if (this._x !== value) {
      this._x = value;
      this.cb.call(this.scope);
    }
  }

  get y() {
    return this._y;
  }

  set y(value) {
    if (this._y !== value) {
      this._y = value;
      this.cb.call(this.scope);
    }
  }

  dot(p) {
    this.x = this.x * p.x;
    this.x = this.y * p.y;
  }

}

exports.default = ObservablePoint;
//# sourceMappingURL=ObservablePoint.js.map