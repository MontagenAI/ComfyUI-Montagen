"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = _default;

var _resource = require("../resource");

var _Texture = _interopRequireDefault(require("../textures/Texture"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _default() {
  return function textureParser(resource, next) {
    if (resource.data && resource.type === _resource.Resource.TYPE.IMAGE) {
      resource.texture = _Texture.default.fromLoader(resource.data, resource.url, resource.name);
    }

    next();
  };
}
//# sourceMappingURL=textureParser.js.map