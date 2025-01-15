import Sprite from "../sprites/Sprite";
import Texture from "../textures/Texture";
import { sign } from "../utils";
import { Rectangle } from "../math";
import { TEXT_GRADIENT } from "../const";
import settings from "../settings";
import TextStyle from "./TextStyle";
import TextMetrics from "./TextMetrics";
import trimCanvas from "../utils/trimCanvas";
import Doc from "../polyfill/Doc";
import { addToTextureCache } from "../utils/cache";
import _ from "lodash";

const defaultDestroyOptions = {
  texture: true,
  children: false,
  baseTexture: true
};

export default class Text extends Sprite {
  constructor(text, style, canvas) {
    canvas = canvas || Doc.createElement("canvas");
    canvas.width = 3;
    canvas.height = 3;

    const texture = Texture.fromCanvas(canvas, settings.SCALE_MODE, "text");
    texture.orig = new Rectangle();
    texture.trim = new Rectangle();

    super(texture);
    addToTextureCache(
      this._texture,
      this._texture.baseTexture.textureCacheIds[0]
    );

    this.canvas = canvas;
    this.context = this.canvas.getContext("2d");
    this.resolution = settings.RESOLUTION;
    this._text = null;
    this._style = null;
    this._styleListener = null;
    this._font = "";
    this.text = text;
    this.style = style;
    this.localStyleID = -1;
  }

  updateText(respectDirty) {
    const style = this._style;

    if (this.localStyleID !== style.styleID) {
      this.dirty = true;
      this.localStyleID = style.styleID;
    }

    if (!this.dirty && respectDirty) {
      return;
    }

    this._font = this._style.toFontString();

    const context = this.context;
    const measured = TextMetrics.measureText(
      this._text,
      this._style,
      this._style.wordWrap,
      this.canvas
    );
    const width = measured.width;
    const height = measured.height;
    const lines = measured.lines;
    const lineHeight = measured.lineHeight;
    const lineWidths = measured.lineWidths;
    const maxLineWidth = measured.maxLineWidth;
    const fontProperties = measured.fontProperties;
    this.lineHeight = measured.lineHeight;
    this.charWidth = fontProperties.fontSize + this._style.letterSpacing;

    this.canvas.width = Math.ceil(
      (Math.max(1, width) + style.padding * 2) * this.resolution
    );
    this.canvas.height = Math.ceil(
      (Math.max(1, height) + style.padding * 2) * this.resolution
    );

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

    let linePositionX;
    let linePositionY;

    // vertical center in lineHeight
    let fontOffset = (lineHeight - fontProperties.fontSize) / 2;

    if (style.dropShadow) {
      context.fillStyle = style.dropShadowColor;
      context.globalAlpha = style.dropShadowAlpha;
      context.shadowBlur = style.dropShadowBlur;

      if (style.dropShadowBlur > 0) {
        context.shadowColor = style.dropShadowColor;
      }

      const xShadowOffset =
        Math.cos(style.dropShadowAngle) * style.dropShadowDistance;
      const yShadowOffset =
        Math.sin(style.dropShadowAngle) * style.dropShadowDistance;

      for (let i = 0; i < lines.length; i++) {
        linePositionX = style.strokeThickness / 2;
        linePositionY = fontOffset + 
          style.strokeThickness / 2 + i * lineHeight + fontProperties.ascent;

        if (style.align === "right") {
          linePositionX += maxLineWidth - lineWidths[i];
        } else if (style.align === "center") {
          linePositionX += (maxLineWidth - lineWidths[i]) / 2;
        }

        if (style.fill) {
          this.drawLetterSpacing(
            lines[i],
            linePositionX + xShadowOffset + style.padding,
            linePositionY + yShadowOffset + style.padding
          );

          if (style.stroke && style.strokeThickness) {
            context.strokeStyle = style.dropShadowColor;
            this.drawLetterSpacing(
              lines[i],
              linePositionX + xShadowOffset + style.padding,
              linePositionY + yShadowOffset + style.padding,
              true
            );
            context.strokeStyle = style.stroke;
          }
        }
      }
    }

    context.shadowBlur = 0;
    context.globalAlpha = 1;
    context.fillStyle = this._generateFillStyle(style, lines);

    const chars = [];
    // draw lines line by line
    for (let i = 0; i < lines.length; i++) {
      linePositionX = style.strokeThickness / 2;
      linePositionY = fontOffset + 
        style.strokeThickness / 2 + i * lineHeight + fontProperties.ascent;

      if (style.align === "right") {
        linePositionX += maxLineWidth - lineWidths[i];
      } else if (style.align === "center") {
        linePositionX += (maxLineWidth - lineWidths[i]) / 2;
      }

      if (style.stroke && style.strokeThickness) {
        this.drawLetterSpacing(
          lines[i],
          linePositionX + style.padding,
          linePositionY + style.padding,
          true
        );
      }

      if (style.fill) {
        const lastLine = chars[chars.length - 1];
        const lastCharIdx = lastLine ? lastLine[lastLine.length - 1].ci : -1;
        chars.push(this.drawLetterSpacing(
          lines[i],
          linePositionX + style.padding,
          linePositionY + style.padding,
          false, 
          lastCharIdx + 1
        ));
      }
    }
    this.chars = chars;
    // console.log('chars', chars);

    this.updateTexture();
  }

  drawBackground(style) {
    const background = style.background || style.backgroundColor;
    if (!background) return;

    const { context, canvas, text } = this;
    const ftext = String(text).trim();
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
    const height = this.lineHeight;
    // make sure start < end;
    const [ start, end ] = (this.selectionStart.lineIdx < this.selectionEnd.lineIdx
       || (this.selectionStart.lineIdx == this.selectionEnd.lineIdx && this.selectionStart.charIdx <= this.selectionEnd.charIdx))
        ? [this.selectionStart, this.selectionEnd] : [this.selectionEnd, this.selectionStart];

    this.selection = {start, end};
    for (let li = start.lineIdx; li <= end.lineIdx; li++) {
      const charStart = li === start.lineIdx ? start.x : 
        (this.chars[li][0]?.left || 0); // todo: align center / right
      const charEnd = li === end.lineIdx ? end.x : 
        (this.chars[li][this.chars[li].length - 1]?.right || 0);
      this.context.fillStyle = this._style.selectionBgColor;
      this.context.fillRect(charStart, li * height, charEnd - charStart, height);
    }
  }

  drawLetterSpacing(text, x, y, isStroke=false, ci=0) {
    const style = this._style;

    // letterSpacing of 0 means normal
    const letterSpacing = style.letterSpacing;

    // 需要计算单个字符的selection，暂时不用快捷的渲染，统一
    // if (letterSpacing === 0) {
    //   if (isStroke) {
    //     this.context.strokeText(text, x, y);
    //   } else {
    //     this.context.fillText(text, x, y);
    //   }
    //   return;
    // }

    const characters = Array.from(text);
    let currentPosition = x;
    let index = 0;
    let current = "";
    let previousWidth = this.context.measureText(text).width;
    let currentWidth = 0;

    const chars = [];
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
      const right = currentPosition - (letterSpacing * 0.5);
      chars.push({ char: current, ci, top: y, left: x, right, cx: 0.5 * (x + right) });
      ci++;
    }
    return chars;
  }

  updateStyle(style) {
    for (let key in style) {
      let newKey = this.camelCase(key);
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
    this.cursorPoint = { x: this.selectionEnd.x, y: this.selectionEnd.y + 1};
    this.updateText(false);
  }

  selectMove(x, y, withShift, withCtrl) {
    if (!this.selectionEnd) return; // todo: select 0 as default
    if (x !== 0) {
      let point;
      if (!withShift && this.selection && this.selection.start.ci < this.selection.end.ci) {
        // 有选中的时候，纯移动先移到开头/末尾
        const sel = this.selection[x > 0 ? 'end' : 'start'];
        point = { x: sel.x, y: sel.y + 1 };
      } else if (!withCtrl && x < 0 && this.selectionEnd.charIdx <= 0) {
        // prev line
        if (this.selectionEnd.lineIdx > 0) {
          const prevLine = this.chars[this.selectionEnd.lineIdx - 1];
          const lastChar = prevLine[prevLine.length - 1];
          // 上一行的lastChar可能是\n，也可能是强制换行的字符，都需要到【左边】
          point = { x: lastChar.left, y: lastChar.top + 1 };
          // console.log('selectMove', lastChar, point);
        }
      } else if (!withCtrl && x > 0 && this.selectionEnd.charIdx >= this.textLine(this.selectionEnd.lineIdx).length) {
        // next line
        if (this.selectionEnd.lineIdx + 1 < this.chars.length) {
          const line = this.chars[this.selectionEnd.lineIdx];
          // 判断是否有强制换行
          const key = (line[line.length - 1].char !== '\n') ? 'right' : 'left';
          const nextLine = this.chars[this.selectionEnd.lineIdx + 1];
          const firstChar = nextLine[0];
          point = { x: firstChar[key], y: firstChar.top + 1 };
        }
      } else {
        let charIdx = this.selectionEnd.charIdx + (x > 0 ? 1 : -1);
        const line = this.textLine(this.selectionEnd.lineIdx);
        // 跳到开头、末尾
        if (withCtrl) charIdx = x > 0 ? line.length : 0;
        // 最后一个字符
        const key = charIdx >= line.length ? 'right' : 'left';
        const char = line[Math.min(charIdx, line.length - 1)];
        point = { x: char[key], y: char.top + 1 };
      }

      if (point) {
        this.cursorPoint = point;
        this.selectionEnd = this.indexOf(point);
      }
    } else {
      let i = this.selectionEnd.lineIdx + (y > 0 ? 1 : -1);
      let pX = this.cursorPoint.x;
      if (withCtrl) { // leftTop / rightBottom
        i = y > 0 ? this.chars.length : 0; 
        pX = y > 0 ? this.width : 0;
      }
      this.selectionEnd = this.indexOf({ x: pX, y: this.lineHeight * i + 1 });
    }

    // cursor move, without shift
    if (!withShift) this.selectionStart = this.selectionEnd;

    this.updateText(false);
  }

  textLine(lineIdx) {
    return this.chars[lineIdx].filter(x => x.char != '\n');
  }

  indexOf(point) {
    const lineIdx = Math.max(0, Math.min(this.chars.length - 1, Math.floor(point.y / this.lineHeight)));
    let charIdx = 0;
    let ci = this.chars[lineIdx][0] ? this.chars[lineIdx][0].ci : 0;
    let x = this.chars[lineIdx][0] ? this.chars[lineIdx][0].left : 0;
    for (const char of this.chars[lineIdx]) {
      if (char.char === '\n') continue;
      if (point.x < char.cx) break;
      charIdx++;
      x = char.right;
      ci = char.ci + 1;
    }
    const height = this.lineHeight;
    return { lineIdx, charIdx, ci, x, y: lineIdx * height, height };
  }

  cursor(ci) {
    let index = ci;
    if (ci === undefined) index = this.selectionEnd.ci;
    // console.log('cursor', {index, ci}, Array.from(this.text).length);
    let char = this.charOf(index);
    let key = 'left';
    if (!char) {
      const lastLine = this.chars[this.chars.length - 1];
      char = lastLine[lastLine.length - 1];
      key = 'right';
    }

    // update
    this.selectionEnd = this.indexOf({ x: char[key], y: char.top + 1 });
    if (ci === undefined) return this.selectionEnd; // get
    this.selectionStart = this.selectionEnd; // set
  }

  input(val) {
    const { text, cursorIndex: ci } = this.delete(false); // remove selection
    const strs = Array.from(text);
    strs.splice(ci, 0, val);
    return { text: strs.join(''), cursorIndex: ci + Array.from(val).length };
  }

  delete(force=true) {
    const strs = Array.from(this.text);
    let start = this.selection.start.ci - 1;
    let count = 1;
    let cursor = this.selectionEnd;
    if (this.selection && this.selection.start.ci < this.selection.end.ci) {
      start = this.selection.start.ci;
      count = this.selection.end.ci - this.selection.start.ci;
      cursor = this.selection.end; // 确保是后边那个
      this.selectionStart = this.selectionEnd = cursor; // 去掉选中
    } else if (!force || !cursor || cursor.ci < 1) {
      return { text: this.text, cursorIndex: cursor ? cursor.ci : strs.length + 1 };
    }
    // 从数组中删除
    strs.splice(start, count);

    // 找到当前光标右边的char
    let line = this.chars[cursor.lineIdx];
    let key = cursor.charIdx < line.length ? 'left' : 'right';
    let char = line[Math.min(cursor.charIdx, line.length - 1)];
    if (key === 'right' && this.chars[cursor.lineIdx + 1]
       && this.chars[cursor.lineIdx + 1][0]) {
      char = this.chars[cursor.lineIdx + 1][0];
      key = 'left';
    }

    const cursorIndex = char.ci + (key === 'right' ? 1 : 0) - count;
    return { text: strs.join(''), cursorIndex };
  }

  charOf(ci) {
    for (const line of this.chars) {
      for (const char of line) {
        if (char.ci === ci) return char;
      }
    }
  }

  selectionText() {
    if (this.selection && this.selection.start.ci < this.selection.end.ci) {
      const strs = Array.from(this.text);
      return strs.slice(this.selection.start.ci, this.selection.end.ci).join('');
    }
    return '';
  }

  camelCase(name) {
    const SPECIAL_CHARS_REGEXP = /([\:\-\_]+(.))/g;
    const MOZ_HACK_REGEXP = /^moz([A-Z])/;

    return name
      .replace(SPECIAL_CHARS_REGEXP, function(_, separator, letter, offset) {
        return offset ? letter.toUpperCase() : letter;
      })
      .replace(MOZ_HACK_REGEXP, "Moz$1");
  }

  updateTexture() {
    const canvas = this.canvas;

    if (this._style.trim) {
      const trimmed = trimCanvas(canvas);

      if (trimmed.data) {
        canvas.width = trimmed.width;
        canvas.height = trimmed.height;
        this.context.putImageData(trimmed.data, 0, 0);
      }
    }

    const texture = this._texture;
    const style = this._style;
    const padding = style.trim ? 0 : style.padding;
    const baseTexture = texture.baseTexture;

    baseTexture.hasLoaded = true;
    baseTexture.resolution = this.resolution;

    baseTexture.realWidth = canvas.width;
    baseTexture.realHeight = canvas.height;
    baseTexture.width = canvas.width / this.resolution;
    baseTexture.height = canvas.height / this.resolution;

    texture.trim.width = texture._frame.width = canvas.width / this.resolution;
    texture.trim.height = texture._frame.height =
      canvas.height / this.resolution;
    texture.trim.x = -padding;
    texture.trim.y = -padding;

    texture.orig.width = texture._frame.width - padding * 2;
    texture.orig.height = texture._frame.height - padding * 2;

    // call sprite onTextureUpdate to update scale if _width or _height were set
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
    this.calculateVertices();
    // if we have already done this on THIS frame.
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

    let gradient;
    let totalIterations;
    let currentIteration;
    let stop;

    const width = this.canvas.width / this.resolution;
    const height = this.canvas.height / this.resolution;
    const fill = style.fill.slice();
    const fillGradientStops = style.fillGradientStops.slice();

    if (!fillGradientStops.length) {
      const lengthPlus1 = fill.length + 1;

      for (let i = 1; i < lengthPlus1; ++i) {
        fillGradientStops.push(i / lengthPlus1);
      }
    }

    fill.unshift(style.fill[0]);
    fillGradientStops.unshift(0);

    fill.push(style.fill[style.fill.length - 1]);
    fillGradientStops.push(1);

    if (style.fillGradientType === TEXT_GRADIENT.LINEAR_VERTICAL) {
      gradient = this.context.createLinearGradient(
        width / 2,
        0,
        width / 2,
        height
      );

      totalIterations = (fill.length + 1) * lines.length;
      currentIteration = 0;
      for (let i = 0; i < lines.length; i++) {
        currentIteration += 1;
        for (let j = 0; j < fill.length; j++) {
          if (typeof fillGradientStops[j] === "number") {
            stop = fillGradientStops[j] / lines.length + i / lines.length;
          } else {
            stop = currentIteration / totalIterations;
          }
          gradient.addColorStop(stop, fill[j]);
          currentIteration++;
        }
      }
    } else {
      gradient = this.context.createLinearGradient(
        0,
        height / 2,
        width,
        height / 2
      );

      totalIterations = fill.length + 1;
      currentIteration = 1;

      for (let i = 0; i < fill.length; i++) {
        if (typeof fillGradientStops[i] === "number") {
          stop = fillGradientStops[i];
        } else {
          stop = currentIteration / totalIterations;
        }
        gradient.addColorStop(stop, fill[i]);
        currentIteration++;
      }
    }

    return gradient;
  }

  destroy(options) {
    if (this.destroyed) return;

    if (typeof options === "boolean") {
      options = { children: options };
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
    const s = sign(this.scale.x) || 1;
    this.scale.x = (s * value) / this._texture.orig.width;
    this._width = value;
  }

  get height() {
    this.updateText(true);
    return Math.abs(this.scale.y) * this._texture.orig.height;
  }

  set height(value) {
    this.updateText(true);
    const s = sign(this.scale.y) || 1;
    this.scale.y = (s * value) / this._texture.orig.height;
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

    if (style instanceof TextStyle) {
      this._style = style;
    } else {
      this._style = new TextStyle(style);
    }

    this.localStyleID = -1;
    this.dirty = true;
  }

  get text() {
    return this._text;
  }

  set text(text) {
    text = String(
      text === "" || text === null || text === undefined ? " " : text
    );

    if (this._text === text) return;
    this._text = text;
    this.dirty = true;
  }
}
