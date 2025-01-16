"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Matrix = _interopRequireDefault(require("./Matrix"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var ux = [1, 1, 0, -1, -1, -1, 0, 1, 1, 1, 0, -1, -1, -1, 0, 1];
var uy = [0, 1, 1, 1, 0, -1, -1, -1, 0, 1, 1, 1, 0, -1, -1, -1];
var vx = [0, -1, -1, -1, 0, 1, 1, 1, 0, 1, 1, 1, 0, -1, -1, -1];
var vy = [1, 1, 0, -1, -1, -1, 0, 1, -1, -1, 0, 1, 1, 1, 0, -1];
var tempMatrices = [];
var mul = [];

function signum(x) {
  if (x < 0) {
    return -1;
  }

  if (x > 0) {
    return 1;
  }

  return 0;
}

function init() {
  for (var i = 0; i < 16; i++) {
    var row = [];
    mul.push(row);

    for (var j = 0; j < 16; j++) {
      var _ux = signum(ux[i] * ux[j] + vx[i] * uy[j]);

      var _uy = signum(uy[i] * ux[j] + vy[i] * uy[j]);

      var _vx = signum(ux[i] * vx[j] + vx[i] * vy[j]);

      var _vy = signum(uy[i] * vx[j] + vy[i] * vy[j]);

      for (var k = 0; k < 16; k++) {
        if (ux[k] === _ux && uy[k] === _uy && vx[k] === _vx && vy[k] === _vy) {
          row.push(k);
          break;
        }
      }
    }
  }

  for (var _i = 0; _i < 16; _i++) {
    var mat = new _Matrix.default();
    mat.set(ux[_i], uy[_i], vx[_i], vy[_i], 0, 0);
    tempMatrices.push(mat);
  }
}

init();
var GroupD8 = {
  E: 0,
  SE: 1,
  S: 2,
  SW: 3,
  W: 4,
  NW: 5,
  N: 6,
  NE: 7,
  MIRROR_VERTICAL: 8,
  MIRROR_HORIZONTAL: 12,
  uX: ind => ux[ind],
  uY: ind => uy[ind],
  vX: ind => vx[ind],
  vY: ind => vy[ind],
  inv: rotation => {
    if (rotation & 8) {
      return rotation & 15;
    }

    return -rotation & 7;
  },
  add: (rotationSecond, rotationFirst) => mul[rotationSecond][rotationFirst],
  sub: (rotationSecond, rotationFirst) => mul[rotationSecond][GroupD8.inv(rotationFirst)],
  rotate180: rotation => rotation ^ 4,
  isVertical: rotation => (rotation & 3) === 2,
  byDirection: (dx, dy) => {
    if (Math.abs(dx) * 2 <= Math.abs(dy)) {
      if (dy >= 0) {
        return GroupD8.S;
      }

      return GroupD8.N;
    } else if (Math.abs(dy) * 2 <= Math.abs(dx)) {
      if (dx > 0) {
        return GroupD8.E;
      }

      return GroupD8.W;
    } else if (dy > 0) {
      if (dx > 0) {
        return GroupD8.SE;
      }

      return GroupD8.SW;
    } else if (dx > 0) {
      return GroupD8.NE;
    }

    return GroupD8.NW;
  },
  matrixAppendRotationInv: function matrixAppendRotationInv(matrix, rotation, tx, ty) {
    if (tx === void 0) {
      tx = 0;
    }

    if (ty === void 0) {
      ty = 0;
    }

    // Packer used "rotation", we use "inv(rotation)"
    var mat = tempMatrices[GroupD8.inv(rotation)];
    mat.tx = tx;
    mat.ty = ty;
    matrix.append(mat);
  }
};
var _default = GroupD8;
exports.default = _default;
//# sourceMappingURL=GroupD8.js.map