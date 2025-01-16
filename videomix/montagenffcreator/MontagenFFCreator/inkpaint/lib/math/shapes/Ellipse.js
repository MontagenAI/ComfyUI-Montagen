"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Rectangle = _interopRequireDefault(require("./Rectangle"));

var _const = require("../../const");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

/**
 * The Ellipse object can be used to specify a hit area for displayObjects
 *
 * @class
 * @memberof InkPaint
 */
class Ellipse {
  /**
   * @param {number} [x=0] - The X coordinate of the center of this ellipse
   * @param {number} [y=0] - The Y coordinate of the center of this ellipse
   * @param {number} [halfWidth=0] - The half width of this ellipse
   * @param {number} [halfHeight=0] - The half height of this ellipse
   */
  constructor(x, y, halfWidth, halfHeight) {
    if (x === void 0) {
      x = 0;
    }

    if (y === void 0) {
      y = 0;
    }

    if (halfWidth === void 0) {
      halfWidth = 0;
    }

    if (halfHeight === void 0) {
      halfHeight = 0;
    }

    /**
     * @member {number}
     * @default 0
     */
    this.x = x;
    /**
     * @member {number}
     * @default 0
     */

    this.y = y;
    /**
     * @member {number}
     * @default 0
     */

    this.width = halfWidth;
    /**
     * @member {number}
     * @default 0
     */

    this.height = halfHeight;
    /**
     * The type of the object, mainly used to avoid `instanceof` checks
     *
     * @member {number}
     * @readOnly
     * @default InkPaint.SHAPES.ELIP
     * @see InkPaint.SHAPES
     */

    this.type = _const.SHAPES.ELIP;
  }
  /**
   * Creates a clone of this Ellipse instance
   *
   * @return {InkPaint.Ellipse} a copy of the ellipse
   */


  clone() {
    return new Ellipse(this.x, this.y, this.width, this.height);
  }
  /**
   * Checks whether the x and y coordinates given are contained within this ellipse
   *
   * @param {number} x - The X coordinate of the point to test
   * @param {number} y - The Y coordinate of the point to test
   * @return {boolean} Whether the x/y coords are within this ellipse
   */


  contains(x, y) {
    if (this.width <= 0 || this.height <= 0) {
      return false;
    } // normalize the coords to an ellipse with center 0,0


    var normx = (x - this.x) / this.width;
    var normy = (y - this.y) / this.height;
    normx *= normx;
    normy *= normy;
    return normx + normy <= 1;
  }
  /**
   * Returns the framing rectangle of the ellipse as a Rectangle object
   *
   * @return {InkPaint.Rectangle} the framing rectangle
   */


  getBounds() {
    return new _Rectangle.default(this.x - this.width, this.y - this.height, this.width, this.height);
  }

}

exports.default = Ellipse;
//# sourceMappingURL=Ellipse.js.map