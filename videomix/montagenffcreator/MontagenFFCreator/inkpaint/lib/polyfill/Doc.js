"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _browserOrNode = require("browser-or-node");

var _Canvas = _interopRequireDefault(require("./Canvas"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var Doc = {
  createElement(tag) {
    var element;

    switch (tag) {
      case "canvas":
        element = new _Canvas.default(1, 1);
        break;

      default:
        element = new _Canvas.default(1, 1);
        break;
    }

    return element;
  }

};

var _default = _browserOrNode.isBrowser ? window.document : Doc;

exports.default = _default;
//# sourceMappingURL=Doc.js.map