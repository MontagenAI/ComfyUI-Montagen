"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Point = _interopRequireDefault(require("../Point"));

var _const = require("../../const");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

/**
 * @class
 * @memberof InkPaint
 */
class Polygon {
  constructor() {
    for (var _len = arguments.length, points = new Array(_len), _key = 0; _key < _len; _key++) {
      points[_key] = arguments[_key];
    }

    if (Array.isArray(points[0])) {
      points = points[0];
    } // if this is an array of points, convert it to a flat array of numbers


    if (points[0] instanceof _Point.default) {
      var p = [];

      for (var i = 0, il = points.length; i < il; i++) {
        p.push(points[i].x, points[i].y);
      }

      points = p;
    }

    this.closed = true;
    /**
     * An array of the points of this polygon
     *
     * @member {number[]}
     */

    this.points = points;
    /**
     * The type of the object, mainly used to avoid `instanceof` checks
     *
     * @member {number}
     * @readOnly
     * @default InkPaint.SHAPES.POLY
     * @see InkPaint.SHAPES
     */

    this.type = _const.SHAPES.POLY;
  }
  /**
   * Creates a clone of this polygon
   *
   * @return {InkPaint.Polygon} a copy of the polygon
   */


  clone() {
    return new Polygon(this.points.slice());
  }
  /**
   * Closes the polygon, adding points if necessary.
   *
   */


  close() {
    var points = this.points; // close the poly if the value is true!

    if (points[0] !== points[points.length - 2] || points[1] !== points[points.length - 1]) {
      points.push(points[0], points[1]);
    }
  }
  /**
   * Checks whether the x and y coordinates passed to this function are contained within this polygon
   *
   * @param {number} x - The X coordinate of the point to test
   * @param {number} y - The Y coordinate of the point to test
   * @return {boolean} Whether the x/y coordinates are within this polygon
   */


  contains(x, y) {
    var inside = false; // use some raycasting to test hits
    // https://github.com/substack/point-in-polygon/blob/master/index.js

    var length = this.points.length / 2;

    for (var i = 0, j = length - 1; i < length; j = i++) {
      var xi = this.points[i * 2];
      var yi = this.points[i * 2 + 1];
      var xj = this.points[j * 2];
      var yj = this.points[j * 2 + 1];
      var intersect = yi > y !== yj > y && x < (xj - xi) * ((y - yi) / (yj - yi)) + xi;

      if (intersect) {
        inside = !inside;
      }
    }

    return inside;
  }

}

exports.default = Polygon;
//# sourceMappingURL=Polygon.js.map