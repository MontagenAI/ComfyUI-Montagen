"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var GLFix = {
  // Temporary fix https://github.com/stackgl/headless-gl/issues/170
  fixGetUniformLocation(ctx) {
    var _getUniformLocation = ctx.getUniformLocation;

    ctx.getUniformLocation = function (program, name) {
      if (program._uniforms && !/\[\d+\]$/.test(name)) {
        var reg = new RegExp(name + "\\[\\d+\\]$");

        for (var i = 0; i < program._uniforms.length; i++) {
          var _name = program._uniforms[i].name;
          if (reg.test(_name)) name = _name;
        }
      }

      return _getUniformLocation.call(this, program, name);
    };
  },

  fixTexImage2D(ctx) {
    var _tetImage2D = ctx.texImage2D; // ctx.texImage2D = function(...args) {
    //   let pixels = args[args.length - 1];
    //   if (pixels._image) pixels = pixels._image;
    //   if (pixels instanceof Image) {
    //     const canvas = new Canvas(pixels.width, pixels.height);
    //     canvas.getContext("2d").drawImage(pixels, 0, 0);
    //     args[args.length - 1] = canvas;
    //   }
    //   return _tetImage2D.apply(this, args);
    // };
  }

};
var _default = GLFix;
exports.default = _default;
//# sourceMappingURL=glfix.js.map