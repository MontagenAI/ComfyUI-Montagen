"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _settings = _interopRequireDefault(require("./settings"));

var _Container = _interopRequireDefault(require("./display/Container"));

var _autoRenderer = require("./autoRenderer");

var _ticker = require("./ticker");

var _const = require("./const");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class Application {
  constructor(options, arg2, arg3, arg4, arg5) {
    if (typeof options === "number") {
      options = Object.assign({
        width: options,
        height: arg2 || _settings.default.RENDER_OPTIONS.height,
        useGL: !!arg4,
        sharedTicker: !!arg5
      }, arg3);
    }

    this._options = options = Object.assign({
      autoStart: true,
      sharedTicker: false,
      useGL: false,
      sharedLoader: false,
      autoRender: false
    }, options);
    this.renderer = (0, _autoRenderer.autoRenderer)(options);
    this.stage = new _Container.default();
    this.stage.isStage = true;
    this._ticker = null;

    if (options.autoRender) {
      this.ticker = options.sharedTicker ? _ticker.shared : new _ticker.Ticker();
    }

    if (options.autoStart) {
      this.start();
    }
  }

  set ticker(ticker) {
    if (this._ticker) this._ticker.remove(this.render, this);
    this._ticker = ticker;
    if (ticker) ticker.add(this.render, this, _const.UPDATE_PRIORITY.LOW);
  }

  get ticker() {
    return this._ticker;
  }

  render() {
    this.renderer.render(this.stage);
  }

  stop() {
    this.ticker && this.ticker.stop();
  }

  start() {
    this.ticker && this.ticker.start();
  }

  get view() {
    return this.renderer.view;
  }

  get screen() {
    return this.renderer.screen;
  }

  destroyChildren(options) {
    this.stage.destroyChildren(options);
  }

  destroy(removeView, stageOptions) {
    if (this._ticker) {
      var oldTicker = this._ticker;
      this.ticker = null;
      oldTicker.destroy();
    }

    this.stage.destroy(stageOptions);
    this.renderer.destroy(removeView);
    this.renderer = null;
    this._options = null;
    this.stage = null;
  }

}

exports.default = Application;
//# sourceMappingURL=Application.js.map