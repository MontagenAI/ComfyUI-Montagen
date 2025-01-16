"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

function pluginTarget(obj) {
  obj.__plugins = {};

  obj.registerPlugin = function registerPlugin(pluginName, ctor) {
    obj.__plugins[pluginName] = ctor;
  };

  obj.prototype.initPlugins = function initPlugins() {
    this.plugins = this.plugins || {};

    for (var o in obj.__plugins) {
      this.plugins[o] = new obj.__plugins[o](this);
    }
  };

  obj.prototype.destroyPlugins = function destroyPlugins() {
    for (var o in this.plugins) {
      this.plugins[o].destroy();
      this.plugins[o] = null;
    }

    this.plugins = null;
  };
}

var _default = {
  mixin: function mixin(obj) {
    pluginTarget(obj);
  }
};
exports.default = _default;
//# sourceMappingURL=pluginTarget.js.map