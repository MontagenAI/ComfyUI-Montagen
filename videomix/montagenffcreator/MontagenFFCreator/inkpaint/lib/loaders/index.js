"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
Object.defineProperty(exports, "Loader", {
  enumerable: true,
  get: function get() {
    return _loader.default;
  }
});
Object.defineProperty(exports, "Resource", {
  enumerable: true,
  get: function get() {
    return _resource.Resource;
  }
});
Object.defineProperty(exports, "getResourcePath", {
  enumerable: true,
  get: function get() {
    return _spritesheetParser.getResourcePath;
  }
});
exports.shared = exports.loader = void 0;
Object.defineProperty(exports, "spritesheetParser", {
  enumerable: true,
  get: function get() {
    return _spritesheetParser.default;
  }
});
Object.defineProperty(exports, "textureParser", {
  enumerable: true,
  get: function get() {
    return _textureParser.default;
  }
});

var _loader = _interopRequireDefault(require("./loader"));

var _resource = require("../resource");

var _spritesheetParser = _interopRequireWildcard(require("./spritesheetParser"));

var _textureParser = _interopRequireDefault(require("./textureParser"));

function _getRequireWildcardCache(nodeInterop) { if (typeof WeakMap !== "function") return null; var cacheBabelInterop = new WeakMap(); var cacheNodeInterop = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(nodeInterop) { return nodeInterop ? cacheNodeInterop : cacheBabelInterop; })(nodeInterop); }

function _interopRequireWildcard(obj, nodeInterop) { if (!nodeInterop && obj && obj.__esModule) { return obj; } if (obj === null || typeof obj !== "object" && typeof obj !== "function") { return { default: obj }; } var cache = _getRequireWildcardCache(nodeInterop); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (key !== "default" && Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj.default = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var shared = new _loader.default();
exports.shared = shared;

shared.destroy = () => {};

var loader = shared || null;
exports.loader = loader;
//# sourceMappingURL=index.js.map