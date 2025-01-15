"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _eventemitter = _interopRequireDefault(require("eventemitter3"));

var _textureParser = _interopRequireDefault(require("./textureParser"));

var _utils = require("../utils");

var _resource = require("../resource");

var _spritesheetParser = _interopRequireDefault(require("./spritesheetParser"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class Loader extends _resource.ResourceLoader {
  constructor(baseUrl, concurrency) {
    super(baseUrl, concurrency);

    _eventemitter.default.call(this);

    for (var i = 0; i < Loader._pixiMiddleware.length; ++i) {
      this.use(Loader._pixiMiddleware[i]());
    }

    this.onStart.add(l => this.emit("start", l));
    this.onLoad.add((l, r) => this.emit("load", l, r));
    this.onProgress.add((l, r) => this.emit("progress", l, r));
    this.onError.add((e, l, r) => this.emit("error", e, l, r));
    this.onComplete.add((l, r) => this.emit("complete", l, r));
  }

  static addPixiMiddleware(fn) {
    Loader._pixiMiddleware.push(fn);
  }

  destroy() {
    this.removeAllListeners();
    super.destroy();
  }

}

exports.default = Loader;
(0, _utils.inherit)(Loader, _eventemitter.default);
Loader._pixiMiddleware = [_textureParser.default, _spritesheetParser.default];
//# sourceMappingURL=loader.js.map