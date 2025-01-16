"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _math = require("../math");

var _eventemitter = _interopRequireDefault(require("eventemitter3"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class ProxyObj extends _eventemitter.default {
  constructor() {
    super();
    this.width = null;
    this.height = null;
    this.alpha = 1;
    this.worldAlpha = 1;
    this.rotation = 0;
    this.x = 0;
    this.y = 0;
    this.scale = new _math.Point(1, 1);
    this.anchor = new _math.Point();
    this.transform = {};
    this.blendMode = null;
    this.text = null;
    this.style = null;
    this.parent = null;
    this.isProxy = true;
  }

  attr(attrs) {}

  replaceFromParent(display) {
    var {
      parent
    } = this;
    if (!parent) return;
    var index = parent.getChildIndex(this);
    parent.removeChild(this);
    parent.addChildAt(display, index);
  }

  updateStyle(style) {
    if (!this.style) this.style = {};

    for (var key in style) {
      var newKey = this.camelCase(key);
      if (newKey === "color") newKey = "fill";
      this.style[newKey] = style[key];
    }
  }

  camelCase(name) {
    var SPECIAL_CHARS_REGEXP = /([\:\-\_]+(.))/g;
    var MOZ_HACK_REGEXP = /^moz([A-Z])/;
    return name.replace(SPECIAL_CHARS_REGEXP, function (_, separator, letter, offset) {
      return offset ? letter.toUpperCase() : letter;
    }).replace(MOZ_HACK_REGEXP, "Moz$1");
  }

  destroy() {
    this.width = null;
    this.height = null;
    this.alpha = null;
    this.x = null;
    this.y = null;
    this.scale = null;
    this.pivot = null;
    this.anchor = null;
    this.text = null;
    this.style = null;
    this.transform = null;
    this.parent = null;
    this.removeAllListeners();
  }

}

exports.default = ProxyObj;
//# sourceMappingURL=ProxyObj.js.map