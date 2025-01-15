"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _math = require("../math");

class TransformBase {
  constructor() {
    this.worldTransform = new _math.Matrix();
    this.localTransform = new _math.Matrix();
    this._worldID = 0;
    this._parentID = 0;
  }

  updateLocalTransform() {// empty
  }

  updateTransform(parentTransform) {
    var pt = parentTransform.worldTransform;
    var wt = this.worldTransform;
    var lt = this.localTransform; // concat the parent matrix with the objects transform.

    wt.a = lt.a * pt.a + lt.b * pt.c;
    wt.b = lt.a * pt.b + lt.b * pt.d;
    wt.c = lt.c * pt.a + lt.d * pt.c;
    wt.d = lt.c * pt.b + lt.d * pt.d;
    wt.tx = lt.tx * pt.a + lt.ty * pt.c + pt.tx;
    wt.ty = lt.tx * pt.b + lt.ty * pt.d + pt.ty;
    this._worldID++;
  }

}

exports.default = TransformBase;
TransformBase.prototype.updateWorldTransform = TransformBase.prototype.updateTransform;
TransformBase.IDENTITY = new TransformBase();
//# sourceMappingURL=TransformBase.js.map