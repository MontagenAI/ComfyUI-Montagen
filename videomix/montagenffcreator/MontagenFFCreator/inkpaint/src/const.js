export const PI_2 = Math.PI * 2;
export const RAD_TO_DEG = 180 / Math.PI;
export const DEG_TO_RAD = Math.PI / 180;
export const RENDERER_TYPE = {
  UNKNOWN: 0,
  WEBGL: 1,
  CANVAS: 2
};

export const BLEND_MODES = {
  NORMAL: 0, // 正常
  ADD: 1, // 线性加深(添加)
  MULTIPLY: 2, // 正片叠底
  SCREEN: 3, // 滤色
  OVERLAY: 4, // 叠加
  DARKEN: 5, // 变暗
  LIGHTEN: 6, // 变亮
  COLOR_DODGE: 7, // 颜色减淡
  COLOR_BURN: 8, // 颜色加深
  HARD_LIGHT: 9, // 强光
  SOFT_LIGHT: 10, // 柔光
  DIFFERENCE: 11, // 差值
  EXCLUSION: 12, // 排除: 与“差值”模式相似但对比度更低的效果
  HUE: 13, // 色相: 用基色的明亮度和饱和度以及混合色的色相创建结果色
  SATURATION: 14, // 饱和度: 用基色的明亮度和色相以及混合色的饱和度创建结果色
  COLOR: 15, // 颜色: 用基色的明亮度以及混合色的色相和饱和度创建结果色
  LUMINOSITY: 16, // 明度: 用基色的色相和饱和度以及混合色的明亮度创建结果色
  NORMAL_NPM: 17, // webgl的NORMAL, not-premultiplied, only for webgl
  ADD_NPM: 18, // webgl的ADD, not-premultiplied, only for webgl
  SCREEN_NPM: 19 // webgl的SCREEN, not-premultiplied, only for webgl
};

export const DRAW_MODES = {
  POINTS: 0,
  LINES: 1,
  LINE_LOOP: 2,
  LINE_STRIP: 3,
  TRIANGLES: 4,
  TRIANGLE_STRIP: 5,
  TRIANGLE_FAN: 6
};

export const SCALE_MODES = {
  LINEAR: 0,
  NEAREST: 1
};

export const WRAP_MODES = {
  CLAMP: 0,
  REPEAT: 1,
  MIRRORED_REPEAT: 2
};

export const GC_MODES = {
  AUTO: 0,
  MANUAL: 1
};

export const URL_FILE_EXTENSION = /\.(\w{3,4})(?:$|\?|#)/i;

export const DATA_URI = /^\s*data:(?:([\w-]+)\/([\w+.-]+))?(?:;charset=([\w-]+))?(?:;(base64))?,(.*)/i;

export const SVG_SIZE = /<svg[^>]*(?:\s(width|height)=('|")(\d*(?:\.\d+)?)(?:px)?('|"))[^>]*(?:\s(width|height)=('|")(\d*(?:\.\d+)?)(?:px)?('|"))[^>]*>/i; // eslint-disable-line max-len

export const SHAPES = {
  POLY: 0,
  RECT: 1,
  CIRC: 2,
  ELIP: 3,
  RREC: 4
};

export const PRECISION = {
  LOW: "lowp",
  MEDIUM: "mediump",
  HIGH: "highp"
};

export const TRANSFORM_MODE = {
  STATIC: 0,
  DYNAMIC: 1
};

export const TEXT_GRADIENT = {
  LINEAR_VERTICAL: 0,
  LINEAR_HORIZONTAL: 1
};

export const UPDATE_PRIORITY = {
  INTERACTION: 50,
  HIGH: 25,
  NORMAL: 0,
  LOW: -25,
  UTILITY: -50
};
