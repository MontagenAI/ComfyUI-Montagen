"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Point = _interopRequireDefault(require("./Point"));

var _const = require("../const");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class Matrix {
  constructor(a, b, c, d, tx, ty) {
    if (a === void 0) {
      a = 1;
    }

    if (b === void 0) {
      b = 0;
    }

    if (c === void 0) {
      c = 0;
    }

    if (d === void 0) {
      d = 1;
    }

    if (tx === void 0) {
      tx = 0;
    }

    if (ty === void 0) {
      ty = 0;
    }

    this.a = a;
    this.b = b;
    /**
     * @member {number}
     * @default 0
     */

    this.c = c;
    /**
     * @member {number}
     * @default 1
     */

    this.d = d;
    /**
     * @member {number}
     * @default 0
     */

    this.tx = tx;
    /**
     * @member {number}
     * @default 0
     */

    this.ty = ty;
    this.array = null;
  }
  /**
   * Creates a Matrix object based on the given array. The Element to Matrix mapping order is as follows:
   *
   * a = array[0]
   * b = array[1]
   * c = array[3]
   * d = array[4]
   * tx = array[2]
   * ty = array[5]
   *
   * @param {number[]} array - The array that the matrix will be populated from.
   */


  fromArray(array) {
    this.a = array[0];
    this.b = array[1];
    this.c = array[3];
    this.d = array[4];
    this.tx = array[2];
    this.ty = array[5];
  }
  /**
   * sets the matrix properties
   *
   * @param {number} a - Matrix component
   * @param {number} b - Matrix component
   * @param {number} c - Matrix component
   * @param {number} d - Matrix component
   * @param {number} tx - Matrix component
   * @param {number} ty - Matrix component
   *
   * @return {InkPaint.Matrix} This matrix. Good for chaining method calls.
   */


  set(a, b, c, d, tx, ty) {
    this.a = a;
    this.b = b;
    this.c = c;
    this.d = d;
    this.tx = tx;
    this.ty = ty;
    return this;
  }
  /**
   * Creates an array from the current Matrix object.
   *
   * @param {boolean} transpose - Whether we need to transpose the matrix or not
   * @param {Float32Array} [out=new Float32Array(9)] - If provided the array will be assigned to out
   * @return {number[]} the newly created array which contains the matrix
   */


  toArray(transpose, out) {
    if (!this.array) {
      this.array = new Float32Array(9);
    }

    var array = out || this.array;

    if (transpose) {
      array[0] = this.a;
      array[1] = this.b;
      array[2] = 0;
      array[3] = this.c;
      array[4] = this.d;
      array[5] = 0;
      array[6] = this.tx;
      array[7] = this.ty;
      array[8] = 1;
    } else {
      array[0] = this.a;
      array[1] = this.c;
      array[2] = this.tx;
      array[3] = this.b;
      array[4] = this.d;
      array[5] = this.ty;
      array[6] = 0;
      array[7] = 0;
      array[8] = 1;
    }

    return array;
  }
  /**
   * Get a new position with the current transformation applied.
   * Can be used to go from a child's coordinate space to the world coordinate space. (e.g. rendering)
   *
   * @param {InkPaint.Point} pos - The origin
   * @param {InkPaint.Point} [newPos] - The point that the new position is assigned to (allowed to be same as input)
   * @return {InkPaint.Point} The new point, transformed through this matrix
   */


  apply(pos, newPos) {
    newPos = newPos || new _Point.default();
    var x = pos.x;
    var y = pos.y;
    newPos.x = this.a * x + this.c * y + this.tx;
    newPos.y = this.b * x + this.d * y + this.ty;
    return newPos;
  }
  /**
   * Get a new position with the inverse of the current transformation applied.
   * Can be used to go from the world coordinate space to a child's coordinate space. (e.g. input)
   *
   * @param {InkPaint.Point} pos - The origin
   * @param {InkPaint.Point} [newPos] - The point that the new position is assigned to (allowed to be same as input)
   * @return {InkPaint.Point} The new point, inverse-transformed through this matrix
   */


  applyInverse(pos, newPos) {
    newPos = newPos || new _Point.default();
    var id = 1 / (this.a * this.d + this.c * -this.b);
    var x = pos.x;
    var y = pos.y;
    newPos.x = this.d * id * x + -this.c * id * y + (this.ty * this.c - this.tx * this.d) * id;
    newPos.y = this.a * id * y + -this.b * id * x + (-this.ty * this.a + this.tx * this.b) * id;
    return newPos;
  }
  /**
   * Translates the matrix on the x and y.
   *
   * @param {number} x How much to translate x by
   * @param {number} y How much to translate y by
   * @return {InkPaint.Matrix} This matrix. Good for chaining method calls.
   */


  translate(x, y) {
    this.tx += x;
    this.ty += y;
    return this;
  }
  /**
   * Applies a scale transformation to the matrix.
   *
   * @param {number} x The amount to scale horizontally
   * @param {number} y The amount to scale vertically
   * @return {InkPaint.Matrix} This matrix. Good for chaining method calls.
   */


  scale(x, y) {
    this.a *= x;
    this.d *= y;
    this.c *= x;
    this.b *= y;
    this.tx *= x;
    this.ty *= y;
    return this;
  }
  /**
   * Applies a rotation transformation to the matrix.
   *
   * @param {number} angle - The angle in radians.
   * @return {InkPaint.Matrix} This matrix. Good for chaining method calls.
   */


  rotate(angle) {
    var cos = Math.cos(angle);
    var sin = Math.sin(angle);
    var a1 = this.a;
    var c1 = this.c;
    var tx1 = this.tx;
    this.a = a1 * cos - this.b * sin;
    this.b = a1 * sin + this.b * cos;
    this.c = c1 * cos - this.d * sin;
    this.d = c1 * sin + this.d * cos;
    this.tx = tx1 * cos - this.ty * sin;
    this.ty = tx1 * sin + this.ty * cos;
    return this;
  }
  /**
   * Appends the given Matrix to this Matrix.
   *
   * @param {InkPaint.Matrix} matrix - The matrix to append.
   * @return {InkPaint.Matrix} This matrix. Good for chaining method calls.
   */


  append(matrix) {
    var a1 = this.a;
    var b1 = this.b;
    var c1 = this.c;
    var d1 = this.d;
    this.a = matrix.a * a1 + matrix.b * c1;
    this.b = matrix.a * b1 + matrix.b * d1;
    this.c = matrix.c * a1 + matrix.d * c1;
    this.d = matrix.c * b1 + matrix.d * d1;
    this.tx = matrix.tx * a1 + matrix.ty * c1 + this.tx;
    this.ty = matrix.tx * b1 + matrix.ty * d1 + this.ty;
    return this;
  }
  /**
   * Sets the matrix based on all the available properties
   *
   * @param {number} x - Position on the x axis
   * @param {number} y - Position on the y axis
   * @param {number} pivotX - Pivot on the x axis
   * @param {number} pivotY - Pivot on the y axis
   * @param {number} scaleX - Scale on the x axis
   * @param {number} scaleY - Scale on the y axis
   * @param {number} rotation - Rotation in radians
   * @param {number} skewX - Skew on the x axis
   * @param {number} skewY - Skew on the y axis
   * @return {InkPaint.Matrix} This matrix. Good for chaining method calls.
   */


  setTransform(x, y, pivotX, pivotY, scaleX, scaleY, rotation, skewX, skewY) {
    this.a = Math.cos(rotation + skewY) * scaleX;
    this.b = Math.sin(rotation + skewY) * scaleX;
    this.c = -Math.sin(rotation - skewX) * scaleY;
    this.d = Math.cos(rotation - skewX) * scaleY;
    this.tx = x - (pivotX * this.a + pivotY * this.c);
    this.ty = y - (pivotX * this.b + pivotY * this.d);
    return this;
  }
  /**
   * Prepends the given Matrix to this Matrix.
   *
   * @param {InkPaint.Matrix} matrix - The matrix to prepend
   * @return {InkPaint.Matrix} This matrix. Good for chaining method calls.
   */


  prepend(matrix) {
    var tx1 = this.tx;

    if (matrix.a !== 1 || matrix.b !== 0 || matrix.c !== 0 || matrix.d !== 1) {
      var a1 = this.a;
      var c1 = this.c;
      this.a = a1 * matrix.a + this.b * matrix.c;
      this.b = a1 * matrix.b + this.b * matrix.d;
      this.c = c1 * matrix.a + this.d * matrix.c;
      this.d = c1 * matrix.b + this.d * matrix.d;
    }

    this.tx = tx1 * matrix.a + this.ty * matrix.c + matrix.tx;
    this.ty = tx1 * matrix.b + this.ty * matrix.d + matrix.ty;
    return this;
  }
  /**
   * Decomposes the matrix (x, y, scaleX, scaleY, and rotation) and sets the properties on to a transform.
   *
   * @param {InkPaint.Transform|InkPaint.TransformStatic} transform - The transform to apply the properties to.
   * @return {InkPaint.Transform|InkPaint.TransformStatic} The transform with the newly applied properties
   */


  decompose(transform) {
    // sort out rotation / skew..
    var a = this.a;
    var b = this.b;
    var c = this.c;
    var d = this.d;
    var skewX = -Math.atan2(-c, d);
    var skewY = Math.atan2(b, a);
    var delta = Math.abs(skewX + skewY);

    if (delta < 0.00001 || Math.abs(_const.PI_2 - delta) < 0.00001) {
      transform.rotation = skewY;
      transform.skew.x = transform.skew.y = 0;
    } else {
      transform.rotation = 0;
      transform.skew.x = skewX;
      transform.skew.y = skewY;
    } // next set scale


    transform.scale.x = Math.sqrt(a * a + b * b);
    transform.scale.y = Math.sqrt(c * c + d * d); // next set position

    transform.position.x = this.tx;
    transform.position.y = this.ty;
    return transform;
  }
  /**
   * Inverts this matrix
   *
   * @return {InkPaint.Matrix} This matrix. Good for chaining method calls.
   */


  invert() {
    var a1 = this.a;
    var b1 = this.b;
    var c1 = this.c;
    var d1 = this.d;
    var tx1 = this.tx;
    var n = a1 * d1 - b1 * c1;
    this.a = d1 / n;
    this.b = -b1 / n;
    this.c = -c1 / n;
    this.d = a1 / n;
    this.tx = (c1 * this.ty - d1 * tx1) / n;
    this.ty = -(a1 * this.ty - b1 * tx1) / n;
    return this;
  }
  /**
   * Resets this Matix to an identity (default) matrix.
   *
   * @return {InkPaint.Matrix} This matrix. Good for chaining method calls.
   */


  identity() {
    this.a = 1;
    this.b = 0;
    this.c = 0;
    this.d = 1;
    this.tx = 0;
    this.ty = 0;
    return this;
  }
  /**
   * Creates a new Matrix object with the same values as this one.
   *
   * @return {InkPaint.Matrix} A copy of this matrix. Good for chaining method calls.
   */


  clone() {
    var matrix = new Matrix();
    matrix.a = this.a;
    matrix.b = this.b;
    matrix.c = this.c;
    matrix.d = this.d;
    matrix.tx = this.tx;
    matrix.ty = this.ty;
    return matrix;
  }
  /**
   * Changes the values of the given matrix to be the same as the ones in this matrix
   *
   * @param {InkPaint.Matrix} matrix - The matrix to copy from.
   * @return {InkPaint.Matrix} The matrix given in parameter with its values updated.
   */


  copy(matrix) {
    matrix.a = this.a;
    matrix.b = this.b;
    matrix.c = this.c;
    matrix.d = this.d;
    matrix.tx = this.tx;
    matrix.ty = this.ty;
    return matrix;
  }
  /**
   * A default (identity) matrix
   *
   * @static
   * @const
   */


  static get IDENTITY() {
    return new Matrix();
  }
  /**
   * A temp matrix
   *
   * @static
   * @const
   */


  static get TEMP_MATRIX() {
    return new Matrix();
  }

}

exports.default = Matrix;
//# sourceMappingURL=Matrix.js.map