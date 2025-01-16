"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _math = require("../math");

var _TransformBase = _interopRequireDefault(require("./TransformBase"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class Transform extends _TransformBase.default {
  constructor() {
    super();
    this.position = new _math.Point(0, 0);
    this.scale = new _math.Point(1, 1);
    this.flip = new _math.Point(1, 1);
    this.skew = new _math.ObservablePoint(this.updateSkew, this, 0, 0);
    this.pivot = new _math.Point(0, 0);
    this._rotation = 0;
    this._cx = 1; // cos rotation + skewY;

    this._sx = 0; // sin rotation + skewY;

    this._cy = 0; // cos rotation + Math.PI/2 - skewX;

    this._sy = 1; // sin rotation + Math.PI/2 - skewX;
  }

  updateSkew() {
    this._cx = Math.cos(this._rotation + this.skew._y);
    this._sx = Math.sin(this._rotation + this.skew._y);
    this._cy = -Math.sin(this._rotation - this.skew._x); // cos, added PI/2

    this._sy = Math.cos(this._rotation - this.skew._x); // sin, added PI/2
  }

  updateLocalTransform() {
    var lt = this.localTransform;
    lt.a = this._cx * this.scale.x * this.flip.x;
    lt.b = this._sx * this.scale.x * this.flip.x;
    lt.c = this._cy * this.scale.y * this.flip.y;
    lt.d = this._sy * this.scale.y * this.flip.y;
    lt.tx = this.position.x - (this.pivot.x * lt.a + this.pivot.y * lt.c);
    lt.ty = this.position.y - (this.pivot.x * lt.b + this.pivot.y * lt.d);
  }

  updateTransform(parentTransform) {
    var lt = this.localTransform;
    lt.a = this._cx * this.scale.x * this.flip.x;
    lt.b = this._sx * this.scale.x * this.flip.x;
    lt.c = this._cy * this.scale.y * this.flip.y;
    lt.d = this._sy * this.scale.y * this.flip.y;
    lt.tx = this.position.x - (this.pivot.x * lt.a + this.pivot.y * lt.c);
    lt.ty = this.position.y - (this.pivot.x * lt.b + this.pivot.y * lt.d); // concat the parent matrix with the objects transform.

    var pt = parentTransform.worldTransform;
    var wt = this.worldTransform;
    wt.a = lt.a * pt.a + lt.b * pt.c;
    wt.b = lt.a * pt.b + lt.b * pt.d;
    wt.c = lt.c * pt.a + lt.d * pt.c;
    wt.d = lt.c * pt.b + lt.d * pt.d;
    wt.tx = lt.tx * pt.a + lt.ty * pt.c + pt.tx;
    wt.ty = lt.tx * pt.b + lt.ty * pt.d + pt.ty;
    this._worldID++;
  }

  setFromMatrix(matrix) {
    matrix.decompose(this);
  }

  get rotation() {
    return this._rotation;
  }

  set rotation(value) {
    this._rotation = value;
    this.updateSkew();
  }

}

exports.default = Transform;
//# sourceMappingURL=Transform.js.map