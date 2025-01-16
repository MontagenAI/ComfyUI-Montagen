"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = mapPremultipliedBlendModes;

var _const = require("../const");

function mapPremultipliedBlendModes() {
  var pm = [];
  var npm = [];

  for (var i = 0; i < 32; i++) {
    pm[i] = i;
    npm[i] = i;
  }

  pm[_const.BLEND_MODES.NORMAL_NPM] = _const.BLEND_MODES.NORMAL;
  pm[_const.BLEND_MODES.ADD_NPM] = _const.BLEND_MODES.ADD;
  pm[_const.BLEND_MODES.SCREEN_NPM] = _const.BLEND_MODES.SCREEN;
  npm[_const.BLEND_MODES.NORMAL] = _const.BLEND_MODES.NORMAL_NPM;
  npm[_const.BLEND_MODES.ADD] = _const.BLEND_MODES.ADD_NPM;
  npm[_const.BLEND_MODES.SCREEN] = _const.BLEND_MODES.SCREEN_NPM;
  var array = [];
  array.push(npm);
  array.push(pm);
  return array;
}
//# sourceMappingURL=mapPremultipliedBlendModes.js.map