"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _utils = require("../../utils");

var _const = require("../../const");

var _ObjectRenderer = _interopRequireDefault(require("../../renderers/webgl/utils/ObjectRenderer"));

var _WebGLRenderer = _interopRequireDefault(require("../../renderers/webgl/WebGLRenderer"));

var _WebGLGraphicsData = _interopRequireDefault(require("./WebGLGraphicsData"));

var _PrimitiveShader = _interopRequireDefault(require("./shaders/PrimitiveShader"));

var _buildPoly = _interopRequireDefault(require("./utils/buildPoly"));

var _buildRectangle = _interopRequireDefault(require("./utils/buildRectangle"));

var _buildRoundedRectangle = _interopRequireDefault(require("./utils/buildRoundedRectangle"));

var _buildCircle = _interopRequireDefault(require("./utils/buildCircle"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

/**
 * Renders the graphics object.
 *
 * @class
 * @memberof InkPaint
 * @extends InkPaint.ObjectRenderer
 */
class GraphicsRenderer extends _ObjectRenderer.default {
  /**
   * @param {InkPaint.WebGLRenderer} renderer - The renderer this object renderer works for.
   */
  constructor(renderer) {
    super(renderer);
    this.graphicsDataPool = [];
    this.primitiveShader = null;
    this.gl = renderer.gl; // easy access!

    this.CONTEXT_UID = 0;
  }
  /**
   * Called when there is a WebGL context change
   *
   * @private
   *
   */


  onContextChange() {
    this.gl = this.renderer.gl;
    this.CONTEXT_UID = this.renderer.CONTEXT_UID;
    this.primitiveShader = new _PrimitiveShader.default(this.gl);
  }
  /**
   * Destroys this renderer.
   *
   */


  destroy() {
    _ObjectRenderer.default.prototype.destroy.call(this);

    for (var i = 0; i < this.graphicsDataPool.length; ++i) {
      this.graphicsDataPool[i].destroy();
    }

    this.graphicsDataPool = null;
  }
  /**
   * Renders a graphics object.
   *
   * @param {InkPaint.Graphics} graphics - The graphics object to render.
   */


  render(graphics) {
    var renderer = this.renderer;
    var gl = renderer.gl;
    var webGLData;
    var webGL = graphics._webGL[this.CONTEXT_UID];

    if (!webGL || graphics.dirty !== webGL.dirty) {
      this.updateGraphics(graphics);
      webGL = graphics._webGL[this.CONTEXT_UID];
    } // This  could be speeded up for sure!


    var shader = this.primitiveShader;
    renderer.bindShader(shader);
    renderer.state.setBlendMode(graphics.blendMode);

    for (var i = 0, n = webGL.data.length; i < n; i++) {
      webGLData = webGL.data[i];
      var shaderTemp = webGLData.shader;
      renderer.bindShader(shaderTemp);
      shaderTemp.uniforms.translationMatrix = graphics.transform.worldTransform.toArray(true);
      shaderTemp.uniforms.tint = (0, _utils.hex2rgb)(graphics.tint);
      shaderTemp.uniforms.alpha = graphics.worldAlpha;
      renderer.bindVao(webGLData.vao);

      if (webGLData.nativeLines) {
        gl.drawArrays(gl.LINES, 0, webGLData.points.length / 6);
      } else {
        webGLData.vao.draw(gl.TRIANGLE_STRIP, webGLData.indices.length);
      }
    }
  }
  /**
   * Updates the graphics object
   *
   * @private
   * @param {InkPaint.Graphics} graphics - The graphics object to update
   */


  updateGraphics(graphics) {
    var gl = this.renderer.gl; // get the contexts graphics object

    var webGL = graphics._webGL[this.CONTEXT_UID]; // if the graphics object does not exist in the webGL context time to create it!

    if (!webGL) {
      webGL = graphics._webGL[this.CONTEXT_UID] = {
        lastIndex: 0,
        data: [],
        gl,
        clearDirty: -1,
        dirty: -1
      };
    } // flag the graphics as not dirty as we are about to update it...


    webGL.dirty = graphics.dirty; // if the user cleared the graphics object we will need to clear every object

    if (graphics.clearDirty !== webGL.clearDirty) {
      webGL.clearDirty = graphics.clearDirty; // loop through and return all the webGLDatas to the object pool so than can be reused later on

      for (var i = 0; i < webGL.data.length; i++) {
        this.graphicsDataPool.push(webGL.data[i]);
      } // clear the array and reset the index..


      webGL.data.length = 0;
      webGL.lastIndex = 0;
    }

    var webGLData;
    var webGLDataNativeLines; // loop through the graphics datas and construct each one..
    // if the object is a complex fill then the new stencil buffer technique will be used
    // other wise graphics objects will be pushed into a batch..

    for (var _i = webGL.lastIndex; _i < graphics.graphicsData.length; _i++) {
      var data = graphics.graphicsData[_i]; // TODO - this can be simplified

      webGLData = this.getWebGLData(webGL, 0);

      if (data.nativeLines && data.lineWidth) {
        webGLDataNativeLines = this.getWebGLData(webGL, 0, true);
        webGL.lastIndex++;
      }

      if (data.type === _const.SHAPES.POLY) {
        (0, _buildPoly.default)(data, webGLData, webGLDataNativeLines);
      }

      if (data.type === _const.SHAPES.RECT) {
        (0, _buildRectangle.default)(data, webGLData, webGLDataNativeLines);
      } else if (data.type === _const.SHAPES.CIRC || data.type === _const.SHAPES.ELIP) {
        (0, _buildCircle.default)(data, webGLData, webGLDataNativeLines);
      } else if (data.type === _const.SHAPES.RREC) {
        (0, _buildRoundedRectangle.default)(data, webGLData, webGLDataNativeLines);
      }

      webGL.lastIndex++;
    }

    this.renderer.bindVao(null); // upload all the dirty data...

    for (var _i2 = 0; _i2 < webGL.data.length; _i2++) {
      webGLData = webGL.data[_i2];

      if (webGLData.dirty) {
        webGLData.upload();
      }
    }
  }
  /**
   *
   * @private
   * @param {WebGLRenderingContext} gl - the current WebGL drawing context
   * @param {number} type - TODO @Alvin
   * @param {number} nativeLines - indicate whether the webGLData use for nativeLines.
   * @return {*} TODO
   */


  getWebGLData(gl, type, nativeLines) {
    var webGLData = gl.data[gl.data.length - 1];

    if (!webGLData || webGLData.nativeLines !== nativeLines || webGLData.points.length > 320000) {
      webGLData = this.graphicsDataPool.pop() || new _WebGLGraphicsData.default(this.renderer.gl, this.primitiveShader, this.renderer.state.attribsState);
      webGLData.nativeLines = nativeLines;
      webGLData.reset(type);
      gl.data.push(webGLData);
    }

    webGLData.dirty = true;
    return webGLData;
  }

}

exports.default = GraphicsRenderer;

_WebGLRenderer.default.registerPlugin("graphics", GraphicsRenderer);
//# sourceMappingURL=GraphicsRenderer.js.map