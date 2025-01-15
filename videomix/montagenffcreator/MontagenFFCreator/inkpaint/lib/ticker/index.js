"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
Object.defineProperty(exports, "Ticker", {
  enumerable: true,
  get: function get() {
    return _Ticker.default;
  }
});
exports.shared = void 0;

var _Ticker = _interopRequireDefault(require("./Ticker"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var shared = new _Ticker.default();
exports.shared = shared;
shared.autoStart = true;

shared.destroy = () => {};
//# sourceMappingURL=index.js.map