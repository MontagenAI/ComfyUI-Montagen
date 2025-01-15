"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.WRAP_MODES = exports.URL_FILE_EXTENSION = exports.UPDATE_PRIORITY = exports.TRANSFORM_MODE = exports.TEXT_GRADIENT = exports.SVG_SIZE = exports.SHAPES = exports.SCALE_MODES = exports.RENDERER_TYPE = exports.RAD_TO_DEG = exports.PRECISION = exports.PI_2 = exports.GC_MODES = exports.DRAW_MODES = exports.DEG_TO_RAD = exports.DATA_URI = exports.BLEND_MODES = void 0;
var PI_2 = Math.PI * 2;
exports.PI_2 = PI_2;
var RAD_TO_DEG = 180 / Math.PI;
exports.RAD_TO_DEG = RAD_TO_DEG;
var DEG_TO_RAD = Math.PI / 180;
exports.DEG_TO_RAD = DEG_TO_RAD;
var RENDERER_TYPE = {
  UNKNOWN: 0,
  WEBGL: 1,
  CANVAS: 2
};
exports.RENDERER_TYPE = RENDERER_TYPE;
var BLEND_MODES = {
  NORMAL: 0,
  // 正常
  ADD: 1,
  // 线性加深(添加)
  MULTIPLY: 2,
  // 正片叠底
  SCREEN: 3,
  // 滤色
  OVERLAY: 4,
  // 叠加
  DARKEN: 5,
  // 变暗
  LIGHTEN: 6,
  // 变亮
  COLOR_DODGE: 7,
  // 颜色减淡
  COLOR_BURN: 8,
  // 颜色加深
  HARD_LIGHT: 9,
  // 强光
  SOFT_LIGHT: 10,
  // 柔光
  DIFFERENCE: 11,
  // 差值
  EXCLUSION: 12,
  // 排除: 与“差值”模式相似但对比度更低的效果
  HUE: 13,
  // 色相: 用基色的明亮度和饱和度以及混合色的色相创建结果色
  SATURATION: 14,
  // 饱和度: 用基色的明亮度和色相以及混合色的饱和度创建结果色
  COLOR: 15,
  // 颜色: 用基色的明亮度以及混合色的色相和饱和度创建结果色
  LUMINOSITY: 16,
  // 明度: 用基色的色相和饱和度以及混合色的明亮度创建结果色
  NORMAL_NPM: 17,
  // webgl的NORMAL, not-premultiplied, only for webgl
  ADD_NPM: 18,
  // webgl的ADD, not-premultiplied, only for webgl
  SCREEN_NPM: 19 // webgl的SCREEN, not-premultiplied, only for webgl

};
exports.BLEND_MODES = BLEND_MODES;
var DRAW_MODES = {
  POINTS: 0,
  LINES: 1,
  LINE_LOOP: 2,
  LINE_STRIP: 3,
  TRIANGLES: 4,
  TRIANGLE_STRIP: 5,
  TRIANGLE_FAN: 6
};
exports.DRAW_MODES = DRAW_MODES;
var SCALE_MODES = {
  LINEAR: 0,
  NEAREST: 1
};
exports.SCALE_MODES = SCALE_MODES;
var WRAP_MODES = {
  CLAMP: 0,
  REPEAT: 1,
  MIRRORED_REPEAT: 2
};
exports.WRAP_MODES = WRAP_MODES;
var GC_MODES = {
  AUTO: 0,
  MANUAL: 1
};
exports.GC_MODES = GC_MODES;
var URL_FILE_EXTENSION = /\.(\w{3,4})(?:$|\?|#)/i;
exports.URL_FILE_EXTENSION = URL_FILE_EXTENSION;
var DATA_URI = /^\s*data:(?:([\w-]+)\/([\w+.-]+))?(?:;charset=([\w-]+))?(?:;(base64))?,(.*)/i;
exports.DATA_URI = DATA_URI;
var SVG_SIZE = /<svg[^>]*(?:\s(width|height)=('|")(\d*(?:\.\d+)?)(?:px)?('|"))[^>]*(?:\s(width|height)=('|")(\d*(?:\.\d+)?)(?:px)?('|"))[^>]*>/i; // eslint-disable-line max-len

exports.SVG_SIZE = SVG_SIZE;
var SHAPES = {
  POLY: 0,
  RECT: 1,
  CIRC: 2,
  ELIP: 3,
  RREC: 4
};
exports.SHAPES = SHAPES;
var PRECISION = {
  LOW: "lowp",
  MEDIUM: "mediump",
  HIGH: "highp"
};
exports.PRECISION = PRECISION;
var TRANSFORM_MODE = {
  STATIC: 0,
  DYNAMIC: 1
};
exports.TRANSFORM_MODE = TRANSFORM_MODE;
var TEXT_GRADIENT = {
  LINEAR_VERTICAL: 0,
  LINEAR_HORIZONTAL: 1
};
exports.TEXT_GRADIENT = TEXT_GRADIENT;
var UPDATE_PRIORITY = {
  INTERACTION: 50,
  HIGH: 25,
  NORMAL: 0,
  LOW: -25,
  UTILITY: -50
};
exports.UPDATE_PRIORITY = UPDATE_PRIORITY;
//# sourceMappingURL=const.js.map