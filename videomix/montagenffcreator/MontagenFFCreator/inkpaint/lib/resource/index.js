"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
Object.defineProperty(exports, "Resource", {
  enumerable: true,
  get: function get() {
    return _Resource.default;
  }
});
Object.defineProperty(exports, "ResourceLoader", {
  enumerable: true,
  get: function get() {
    return _Loader.default;
  }
});

var _b = _interopRequireDefault(require("./b64"));

var _async = _interopRequireDefault(require("./async"));

var _Loader = _interopRequireDefault(require("./Loader"));

var _Resource = _interopRequireDefault(require("./Resource"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

_Loader.default.base64 = _b.default;
_Loader.default.async = _async.default;
_Loader.default.encodeBinary = _b.default;
_Loader.default.Resource = _Resource.default;
//# sourceMappingURL=index.js.map