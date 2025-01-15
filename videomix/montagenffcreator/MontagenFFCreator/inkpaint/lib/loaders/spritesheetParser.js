"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = _default;
exports.getResourcePath = getResourcePath;

var _url = _interopRequireDefault(require("url"));

var _resource = require("../resource");

var _Spritesheet = _interopRequireDefault(require("../textures/Spritesheet"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _default() {
  return function spritesheetParser(resource, next) {
    var imageResourceName = resource.name + "_image";

    if (!resource.data || resource.type !== _resource.Resource.TYPE.JSON || !resource.data.frames || this.resources[imageResourceName]) {
      next();
      return;
    }

    var loadOptions = {
      crossOrigin: resource.crossOrigin,
      metadata: resource.metadata.imageMetadata,
      parentResource: resource
    };
    var resourcePath = getResourcePath(resource, this.baseUrl); // load the image for this sheet

    this.add(imageResourceName, resourcePath, loadOptions, function onImageLoad(res) {
      if (res.error) {
        next(res.error);
        return;
      }

      var spritesheet = new _Spritesheet.default(res.texture.baseTexture, resource.data, resource.url);
      spritesheet.parse(() => {
        resource.spritesheet = spritesheet;
        resource.textures = spritesheet.textures;
        next();
      });
    });
  };
}

function getResourcePath(resource, baseUrl) {
  // Prepend url path unless the resource image is a data url
  if (resource.isDataUrl) {
    return resource.data.meta.image;
  }

  return _url.default.resolve(resource.url.replace(baseUrl, ""), resource.data.meta.image);
}
//# sourceMappingURL=spritesheetParser.js.map