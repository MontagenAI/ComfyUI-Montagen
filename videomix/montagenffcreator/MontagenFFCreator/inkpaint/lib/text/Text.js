"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Sprite = _interopRequireDefault(require("../sprites/Sprite"));

var _Texture = _interopRequireDefault(require("../textures/Texture"));

var _utils = require("../utils");

var _math = require("../math");

var _const = require("../const");

var _settings = _interopRequireDefault(require("../settings"));

var _TextStyle = _interopRequireDefault(require("./TextStyle"));

var _TextMetrics = _interopRequireDefault(require("./TextMetrics"));

var _trimCanvas = _interopRequireDefault(require("../utils/trimCanvas"));

var _Doc = _interopRequireDefault(require("../polyfill/Doc"));

var _cache = require("../utils/cache");

var _lodash = _interopRequireDefault(require("lodash"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var defaultDestroyOptions = {
  texture: true,
  children: false,
  baseTexture: true
};

class Text extends _Sprite.default {
  constructor(text, style, canvas) {
    canvas = canvas || _Doc.default.createElement("canvas");
    canvas.width = 3;
    canvas.height = 3;

    var texture = _Texture.default.fromCanvas(canvas, _settings.default.SCALE_MODE, "text");

    texture.orig = new _math.Rectangle();
    texture.trim = new _math.Rectangle();
    super(texture);
    (0, _cache.addToTextureCache)(this._texture, this._texture.baseTexture.textureCacheIds[0]);
    this.canvas = canvas;
    this.context = this.canvas.getContext("2d");
    this.resolution = _settings.default.RESOLUTION;
    this._text = null;
    this._style = null;
    this._styleListener = null;
    this._font = "";
    this.text = text;
    this.style = style;
    this.localStyleID = -1;
  }

  updateText(respectDirty) {
    var style = this._style;

    if (this.localStyleID !== style.styleID) {
      this.dirty = true;
      this.localStyleID = style.styleID;
    }

    if (!this.dirty && respectDirty) {
      return;
    }

    this._font = this._style.toFontString();
    var context = this.context;

    var measured = _TextMetrics.default.measureText(this._text, this._style, this._style.wordWrap, this.canvas);

    var width = measured.width;
    var height = measured.height;
    var lines = measured.lines;
    var lineHeight = measured.lineHeight;
    var lineWidths = measured.lineWidths;
    var maxLineWidth = measured.maxLineWidth;
    var fontProperties = measured.fontProperties;
    this.lineHeight = measured.lineHeight;
    this.charWidth = fontProperties.fontSize + this._style.letterSpacing;
    this.canvas.width = Math.ceil((Math.max(1, width) + style.padding * 2) * this.resolution);
    this.canvas.height = Math.ceil((Math.max(1, height) + style.padding * 2) * this.resolution);
    context.scale(this.resolution, this.resolution);
    context.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.drawBackground(style);
    this.drawSelection();
    context.font = this._font;
    context.strokeStyle = style.stroke;
    context.lineWidth = style.strokeThickness;
    context.textBaseline = style.textBaseline;
    context.lineJoin = style.lineJoin;
    context.miterLimit = style.miterLimit;
    var linePositionX;
    var linePositionY; // vertical center in lineHeight

    var fontOffset = (lineHeight - fontProperties.fontSize) / 2;

    if (style.dropShadow) {
      context.fillStyle = style.dropShadowColor;
      context.globalAlpha = style.dropShadowAlpha;
      context.shadowBlur = style.dropShadowBlur;

      if (style.dropShadowBlur > 0) {
        context.shadowColor = style.dropShadowColor;
      }

      var xShadowOffset = Math.cos(style.dropShadowAngle) * style.dropShadowDistance;
      var yShadowOffset = Math.sin(style.dropShadowAngle) * style.dropShadowDistance;

      for (var i = 0; i < lines.length; i++) {
        linePositionX = style.strokeThickness / 2;
        linePositionY = fontOffset + style.strokeThickness / 2 + i * lineHeight + fontProperties.ascent;

        if (style.align === "right") {
          linePositionX += maxLineWidth - lineWidths[i];
        } else if (style.align === "center") {
          linePositionX += (maxLineWidth - lineWidths[i]) / 2;
        }

        if (style.fill) {
          this.drawLetterSpacing(lines[i], linePositionX + xShadowOffset + style.padding, linePositionY + yShadowOffset + style.padding);

          if (style.stroke && style.strokeThickness) {
            context.strokeStyle = style.dropShadowColor;
            this.drawLetterSpacing(lines[i], linePositionX + xShadowOffset + style.padding, linePositionY + yShadowOffset + style.padding, true);
            context.strokeStyle = style.stroke;
          }
        }
      }
    }

    context.shadowBlur = 0;
    context.globalAlpha = 1;
    context.fillStyle = this._generateFillStyle(style, lines);
    var chars = []; // draw lines line by line

    for (var _i = 0; _i < lines.length; _i++) {
      linePositionX = style.strokeThickness / 2;
      linePositionY = fontOffset + style.strokeThickness / 2 + _i * lineHeight + fontProperties.ascent;

      if (style.align === "right") {
        linePositionX += maxLineWidth - lineWidths[_i];
      } else if (style.align === "center") {
        linePositionX += (maxLineWidth - lineWidths[_i]) / 2;
      }

      if (style.stroke && style.strokeThickness) {
        this.drawLetterSpacing(lines[_i], linePositionX + style.padding, linePositionY + style.padding, true);
      }

      if (style.fill) {
        var lastLine = chars[chars.length - 1];
        var lastCharIdx = lastLine ? lastLine[lastLine.length - 1].ci : -1;
        chars.push(this.drawLetterSpacing(lines[_i], linePositionX + style.padding, linePositionY + style.padding, false, lastCharIdx + 1));
      }
    }

    this.chars = chars; // console.log('chars', chars);

    this.updateTexture();
  }

  drawBackground(style) {
    var background = style.background || style.backgroundColor;
    if (!background) return;
    var {
      context,
      canvas,
      text
    } = this;
    var ftext = String(text).trim();

    if (ftext) {
      context.fillStyle = background;
      context.fillRect(0, 0, canvas.width, canvas.height);
    } else {
      context.clearRect(0, 0, canvas.width, canvas.height);
    }
  }

  drawSelection() {
    if (!this.selectionStart || !this.selectionEnd) {
      this.selection = null;
      return;
    }

    var height = this.lineHeight; // make sure start < end;

    var [start, end] = this.selectionStart.lineIdx < this.selectionEnd.lineIdx || this.selectionStart.lineIdx == this.selectionEnd.lineIdx && this.selectionStart.charIdx <= this.selectionEnd.charIdx ? [this.selectionStart, this.selectionEnd] : [this.selectionEnd, this.selectionStart];
    this.selection = {
      start,
      end
    };

    for (var li = start.lineIdx; li <= end.lineIdx; li++) {
      var _this$chars$li$, _this$chars$li;

      var charStart = li === start.lineIdx ? start.x : ((_this$chars$li$ = this.chars[li][0]) == null ? void 0 : _this$chars$li$.left) || 0; // todo: align center / right

      var charEnd = li === end.lineIdx ? end.x : ((_this$chars$li = this.chars[li][this.chars[li].length - 1]) == null ? void 0 : _this$chars$li.right) || 0;
      this.context.fillStyle = this._style.selectionBgColor;
      this.context.fillRect(charStart, li * height, charEnd - charStart, height);
    }
  }

  drawLetterSpacing(text, x, y, isStroke, ci) {
    if (isStroke === void 0) {
      isStroke = false;
    }

    if (ci === void 0) {
      ci = 0;
    }

    var style = this._style; // letterSpacing of 0 means normal

    var letterSpacing = style.letterSpacing; // 需要计算单个字符的selection，暂时不用快捷的渲染，统一
    // if (letterSpacing === 0) {
    //   if (isStroke) {
    //     this.context.strokeText(text, x, y);
    //   } else {
    //     this.context.fillText(text, x, y);
    //   }
    //   return;
    // }

    var characters = Array.from(text);
    var currentPosition = x;
    var index = 0;
    var current = "";
    var previousWidth = this.context.measureText(text).width;
    var currentWidth = 0;
    var chars = [];

    while (index < characters.length) {
      current = characters[index++];
      x = currentPosition;

      if (isStroke) {
        this.context.strokeText(current, x, y);
      } else {
        this.context.fillText(current, x, y);
      }

      currentWidth = this.context.measureText(characters.slice(index).join('')).width;
      currentPosition += previousWidth - currentWidth + letterSpacing;
      previousWidth = currentWidth;
      var right = currentPosition - letterSpacing * 0.5;
      chars.push({
        char: current,
        ci,
        top: y,
        left: x,
        right,
        cx: 0.5 * (x + right)
      });
      ci++;
    }

    return chars;
  }

  updateStyle(style) {
    for (var key in style) {
      var newKey = this.camelCase(key);
      if (newKey === "color") newKey = "fill";
      this.style[newKey] = style[key];
    }
  }

  selectStart(point) {
    this.selectionStart = this.indexOf(point);
    this.selectionEnd = null;
  }

  selectEnd(point) {
    this.selectionEnd = this.indexOf(point);
    this.cursorPoint = {
      x: this.selectionEnd.x,
      y: this.selectionEnd.y + 1
    };
    this.updateText(false);
  }

  selectMove(x, y, withShift, withCtrl) {
    if (!this.selectionEnd) return; // todo: select 0 as default

    if (x !== 0) {
      var point;

      if (!withShift && this.selection && this.selection.start.ci < this.selection.end.ci) {
        // 有选中的时候，纯移动先移到开头/末尾
        var sel = this.selection[x > 0 ? 'end' : 'start'];
        point = {
          x: sel.x,
          y: sel.y + 1
        };
      } else if (!withCtrl && x < 0 && this.selectionEnd.charIdx <= 0) {
        // prev line
        if (this.selectionEnd.lineIdx > 0) {
          var prevLine = this.chars[this.selectionEnd.lineIdx - 1];
          var lastChar = prevLine[prevLine.length - 1]; // 上一行的lastChar可能是\n，也可能是强制换行的字符，都需要到【左边】

          point = {
            x: lastChar.left,
            y: lastChar.top + 1
          }; // console.log('selectMove', lastChar, point);
        }
      } else if (!withCtrl && x > 0 && this.selectionEnd.charIdx >= this.textLine(this.selectionEnd.lineIdx).length) {
        // next line
        if (this.selectionEnd.lineIdx + 1 < this.chars.length) {
          var line = this.chars[this.selectionEnd.lineIdx]; // 判断是否有强制换行

          var key = line[line.length - 1].char !== '\n' ? 'right' : 'left';
          var nextLine = this.chars[this.selectionEnd.lineIdx + 1];
          var firstChar = nextLine[0];
          point = {
            x: firstChar[key],
            y: firstChar.top + 1
          };
        }
      } else {
        var charIdx = this.selectionEnd.charIdx + (x > 0 ? 1 : -1);

        var _line = this.textLine(this.selectionEnd.lineIdx); // 跳到开头、末尾


        if (withCtrl) charIdx = x > 0 ? _line.length : 0; // 最后一个字符

        var _key = charIdx >= _line.length ? 'right' : 'left';

        var char = _line[Math.min(charIdx, _line.length - 1)];

        point = {
          x: char[_key],
          y: char.top + 1
        };
      }

      if (point) {
        this.cursorPoint = point;
        this.selectionEnd = this.indexOf(point);
      }
    } else {
      var i = this.selectionEnd.lineIdx + (y > 0 ? 1 : -1);
      var pX = this.cursorPoint.x;

      if (withCtrl) {
        // leftTop / rightBottom
        i = y > 0 ? this.chars.length : 0;
        pX = y > 0 ? this.width : 0;
      }

      this.selectionEnd = this.indexOf({
        x: pX,
        y: this.lineHeight * i + 1
      });
    } // cursor move, without shift


    if (!withShift) this.selectionStart = this.selectionEnd;
    this.updateText(false);
  }

  textLine(lineIdx) {
    return this.chars[lineIdx].filter(x => x.char != '\n');
  }

  indexOf(point) {
    var lineIdx = Math.max(0, Math.min(this.chars.length - 1, Math.floor(point.y / this.lineHeight)));
    var charIdx = 0;
    var ci = this.chars[lineIdx][0] ? this.chars[lineIdx][0].ci : 0;
    var x = this.chars[lineIdx][0] ? this.chars[lineIdx][0].left : 0;

    for (var char of this.chars[lineIdx]) {
      if (char.char === '\n') continue;
      if (point.x < char.cx) break;
      charIdx++;
      x = char.right;
      ci = char.ci + 1;
    }

    var height = this.lineHeight;
    return {
      lineIdx,
      charIdx,
      ci,
      x,
      y: lineIdx * height,
      height
    };
  }

  cursor(ci) {
    var index = ci;
    if (ci === undefined) index = this.selectionEnd.ci; // console.log('cursor', {index, ci}, Array.from(this.text).length);

    var char = this.charOf(index);
    var key = 'left';

    if (!char) {
      var lastLine = this.chars[this.chars.length - 1];
      char = lastLine[lastLine.length - 1];
      key = 'right';
    } // update


    this.selectionEnd = this.indexOf({
      x: char[key],
      y: char.top + 1
    });
    if (ci === undefined) return this.selectionEnd; // get

    this.selectionStart = this.selectionEnd; // set
  }

  input(val) {
    var {
      text,
      cursorIndex: ci
    } = this.delete(false); // remove selection

    var strs = Array.from(text);
    strs.splice(ci, 0, val);
    return {
      text: strs.join(''),
      cursorIndex: ci + Array.from(val).length
    };
  }

  delete(force) {
    if (force === void 0) {
      force = true;
    }

    var strs = Array.from(this.text);
    var start = this.selection.start.ci - 1;
    var count = 1;
    var cursor = this.selectionEnd;

    if (this.selection && this.selection.start.ci < this.selection.end.ci) {
      start = this.selection.start.ci;
      count = this.selection.end.ci - this.selection.start.ci;
      cursor = this.selection.end; // 确保是后边那个

      this.selectionStart = this.selectionEnd = cursor; // 去掉选中
    } else if (!force || !cursor || cursor.ci < 1) {
      return {
        text: this.text,
        cursorIndex: cursor ? cursor.ci : strs.length + 1
      };
    } // 从数组中删除


    strs.splice(start, count); // 找到当前光标右边的char

    var line = this.chars[cursor.lineIdx];
    var key = cursor.charIdx < line.length ? 'left' : 'right';
    var char = line[Math.min(cursor.charIdx, line.length - 1)];

    if (key === 'right' && this.chars[cursor.lineIdx + 1] && this.chars[cursor.lineIdx + 1][0]) {
      char = this.chars[cursor.lineIdx + 1][0];
      key = 'left';
    }

    var cursorIndex = char.ci + (key === 'right' ? 1 : 0) - count;
    return {
      text: strs.join(''),
      cursorIndex
    };
  }

  charOf(ci) {
    for (var line of this.chars) {
      for (var char of line) {
        if (char.ci === ci) return char;
      }
    }
  }

  selectionText() {
    if (this.selection && this.selection.start.ci < this.selection.end.ci) {
      var strs = Array.from(this.text);
      return strs.slice(this.selection.start.ci, this.selection.end.ci).join('');
    }

    return '';
  }

  camelCase(name) {
    var SPECIAL_CHARS_REGEXP = /([\:\-\_]+(.))/g;
    var MOZ_HACK_REGEXP = /^moz([A-Z])/;
    return name.replace(SPECIAL_CHARS_REGEXP, function (_, separator, letter, offset) {
      return offset ? letter.toUpperCase() : letter;
    }).replace(MOZ_HACK_REGEXP, "Moz$1");
  }

  updateTexture() {
    var canvas = this.canvas;

    if (this._style.trim) {
      var trimmed = (0, _trimCanvas.default)(canvas);

      if (trimmed.data) {
        canvas.width = trimmed.width;
        canvas.height = trimmed.height;
        this.context.putImageData(trimmed.data, 0, 0);
      }
    }

    var texture = this._texture;
    var style = this._style;
    var padding = style.trim ? 0 : style.padding;
    var baseTexture = texture.baseTexture;
    baseTexture.hasLoaded = true;
    baseTexture.resolution = this.resolution;
    baseTexture.realWidth = canvas.width;
    baseTexture.realHeight = canvas.height;
    baseTexture.width = canvas.width / this.resolution;
    baseTexture.height = canvas.height / this.resolution;
    texture.trim.width = texture._frame.width = canvas.width / this.resolution;
    texture.trim.height = texture._frame.height = canvas.height / this.resolution;
    texture.trim.x = -padding;
    texture.trim.y = -padding;
    texture.orig.width = texture._frame.width - padding * 2;
    texture.orig.height = texture._frame.height - padding * 2; // call sprite onTextureUpdate to update scale if _width or _height were set

    this._onTextureUpdate();

    baseTexture.emit("update", baseTexture);
    baseTexture.adaptedNodeCanvas();
    this.dirty = false;
  }

  renderWebGL(renderer) {
    if (this.resolution !== renderer.resolution) {
      this.resolution = renderer.resolution;
      this.dirty = true;
    }

    this.updateText(true);
    super.renderWebGL(renderer);
  }

  _renderCanvas(renderer) {
    if (this.resolution !== renderer.resolution) {
      this.resolution = renderer.resolution;
      this.dirty = true;
    }

    this.updateText(true);

    super._renderCanvas(renderer);
  }

  getLocalBounds(rect) {
    this.updateText(true);
    return super.getLocalBounds.call(this, rect);
  }

  _calculateBounds() {
    this.updateText(true);
    this.calculateVertices(); // if we have already done this on THIS frame.

    this._bounds.addQuad(this.vertexData);
  }

  _onStyleChange() {
    this.dirty = true;
  }

  _generateFillStyle(style, lines) {
    if (style.fillImage) {
      return this.context.createPattern(style.fillImage, 'repeat');
    }

    if (!Array.isArray(style.fill)) {
      return style.fill;
    }

    var gradient;
    var totalIterations;
    var currentIteration;
    var stop;
    var width = this.canvas.width / this.resolution;
    var height = this.canvas.height / this.resolution;
    var fill = style.fill.slice();
    var fillGradientStops = style.fillGradientStops.slice();

    if (!fillGradientStops.length) {
      var lengthPlus1 = fill.length + 1;

      for (var i = 1; i < lengthPlus1; ++i) {
        fillGradientStops.push(i / lengthPlus1);
      }
    }

    fill.unshift(style.fill[0]);
    fillGradientStops.unshift(0);
    fill.push(style.fill[style.fill.length - 1]);
    fillGradientStops.push(1);

    if (style.fillGradientType === _const.TEXT_GRADIENT.LINEAR_VERTICAL) {
      gradient = this.context.createLinearGradient(width / 2, 0, width / 2, height);
      totalIterations = (fill.length + 1) * lines.length;
      currentIteration = 0;

      for (var _i2 = 0; _i2 < lines.length; _i2++) {
        currentIteration += 1;

        for (var j = 0; j < fill.length; j++) {
          if (typeof fillGradientStops[j] === "number") {
            stop = fillGradientStops[j] / lines.length + _i2 / lines.length;
          } else {
            stop = currentIteration / totalIterations;
          }

          gradient.addColorStop(stop, fill[j]);
          currentIteration++;
        }
      }
    } else {
      gradient = this.context.createLinearGradient(0, height / 2, width, height / 2);
      totalIterations = fill.length + 1;
      currentIteration = 1;

      for (var _i3 = 0; _i3 < fill.length; _i3++) {
        if (typeof fillGradientStops[_i3] === "number") {
          stop = fillGradientStops[_i3];
        } else {
          stop = currentIteration / totalIterations;
        }

        gradient.addColorStop(stop, fill[_i3]);
        currentIteration++;
      }
    }

    return gradient;
  }

  destroy(options) {
    if (this.destroyed) return;

    if (typeof options === "boolean") {
      options = {
        children: options
      };
    }

    options = Object.assign({}, defaultDestroyOptions, options);
    super.destroy(options);
    this.context = null;
    this.canvas = null;
    this._style = null;
  }

  get width() {
    this.updateText(true);
    return Math.abs(this.scale.x) * this._texture.orig.width;
  }

  set width(value) {
    this.updateText(true);
    var s = (0, _utils.sign)(this.scale.x) || 1;
    this.scale.x = s * value / this._texture.orig.width;
    this._width = value;
  }

  get height() {
    this.updateText(true);
    return Math.abs(this.scale.y) * this._texture.orig.height;
  }

  set height(value) {
    this.updateText(true);
    var s = (0, _utils.sign)(this.scale.y) || 1;
    this.scale.y = s * value / this._texture.orig.height;
    this._height = value;
  }

  get font() {
    return this._font;
  }

  get style() {
    return this._style;
  }

  set style(style) {
    style = style || {};

    if (style instanceof _TextStyle.default) {
      this._style = style;
    } else {
      this._style = new _TextStyle.default(style);
    }

    this.localStyleID = -1;
    this.dirty = true;
  }

  get text() {
    return this._text;
  }

  set text(text) {
    text = String(text === "" || text === null || text === undefined ? " " : text);
    if (this._text === text) return;
    this._text = text;
    this.dirty = true;
  }

}

exports.default = Text;
//# sourceMappingURL=Text.js.map