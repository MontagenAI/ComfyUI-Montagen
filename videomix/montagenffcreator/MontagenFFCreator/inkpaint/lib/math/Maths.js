"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var Maths = {
  sign(x) {
    x = Number(x);

    if (x === 0 || isNaN(x)) {
      return x;
    }

    return x > 0 ? 1 : -1;
  }

};
var _default = Maths;
exports.default = _default;
//# sourceMappingURL=Maths.js.map