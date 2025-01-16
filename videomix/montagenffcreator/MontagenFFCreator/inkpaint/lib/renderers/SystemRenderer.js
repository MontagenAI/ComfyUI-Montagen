"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _utils = require("../utils");

var _math = require("../math");

var _const = require("../const");

var _eventemitter = _interopRequireDefault(require("eventemitter3"));

var _Doc = _interopRequireDefault(require("../polyfill/Doc"));

var _settings = _interopRequireDefault(require("../settings"));

var _Container = _interopRequireDefault(require("../display/Container"));

var _RenderTexture = _interopRequireDefault(require("../textures/RenderTexture"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var tempMatrix = new _math.Matrix();

class SystemRenderer extends _eventemitter.default {
  constructor(system, options, arg2, arg3) {
    super();

    if (typeof options === "number") {
      options = Object.assign({
        width: options,
        height: arg2 || _settings.default.RENDER_OPTIONS.height
      }, arg3);
    }

    options = Object.assign({}, _settings.default.RENDER_OPTIONS, options);
    this.options = options;
    this.type = _const.RENDERER_TYPE.UNKNOWN;
    this.screen = new _math.Rectangle(0, 0, options.width, options.height);
    this.view = options.view || _Doc.default.createElement("canvas");
    this.resolution = options.resolution || _settings.default.RESOLUTION;
    this.transparent = options.transparent;
    this.autoResize = options.autoResize || false;
    this.blendModes = null;
    this.preserveDrawingBuffer = options.preserveDrawingBuffer;
    this.clearBeforeRender = options.clearBeforeRender;
    this.roundPixels = options.roundPixels;
    this._backgroundColor = 0x000000;
    this._backgroundColorRgba = [0, 0, 0, 0];
    this._backgroundColorString = "#000000";
    this.backgroundColor = options.backgroundColor || this._backgroundColor; // run bg color setter

    this._tempDisplayObjectParent = new _Container.default();
    this._lastObjectRendered = this._tempDisplayObjectParent;
  }

  get width() {
    return this.view.width;
  }

  get height() {
    return this.view.height;
  }

  resize(screenWidth, screenHeight) {
    this.screen.width = screenWidth;
    this.screen.height = screenHeight;
    this.view.width = screenWidth * this.resolution;
    this.view.height = screenHeight * this.resolution;

    if (this.autoResize) {
      this.view.style.width = screenWidth + "px";
      this.view.style.height = screenHeight + "px";
    }
  }

  destroy(removeView) {
    if (removeView && this.view.parentNode) {
      this.view.parentNode.removeChild(this.view);
    }

    this.type = _const.RENDERER_TYPE.UNKNOWN;
    this.view = null;
    this.screen = null;
    this.resolution = 0;
    this.transparent = false;
    this.autoResize = false;
    this.blendModes = null;
    this.options = null;
    this.preserveDrawingBuffer = false;
    this.clearBeforeRender = false;
    this.roundPixels = false;
    this._backgroundColor = 0;
    this._backgroundColorRgba = null;
    this._backgroundColorString = null;
    this._tempDisplayObjectParent = null;
    this._lastObjectRendered = null;
  }

  get backgroundColor() {
    return this._backgroundColor;
  }

  set backgroundColor(value) {
    this._backgroundColor = value;
    this._backgroundColorString = (0, _utils.hex2string)(value);
    (0, _utils.hex2rgb)(value, this._backgroundColorRgba);
  }

}

exports.default = SystemRenderer;
//# sourceMappingURL=SystemRenderer.js.map