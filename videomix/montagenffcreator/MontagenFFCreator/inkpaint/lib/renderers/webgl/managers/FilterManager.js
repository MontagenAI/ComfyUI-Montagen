"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _WebGLManager = _interopRequireDefault(require("./WebGLManager"));

var _RenderTarget = _interopRequireDefault(require("../utils/RenderTarget"));

var _Quad = _interopRequireDefault(require("../utils/Quad"));

var _math = require("../../../math");

var _Shader = _interopRequireDefault(require("../../../Shader"));

var filterTransforms = _interopRequireWildcard(require("../filters/filterTransforms"));

var _bitTwiddle = _interopRequireDefault(require("bit-twiddle"));

function _getRequireWildcardCache(nodeInterop) { if (typeof WeakMap !== "function") return null; var cacheBabelInterop = new WeakMap(); var cacheNodeInterop = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(nodeInterop) { return nodeInterop ? cacheNodeInterop : cacheBabelInterop; })(nodeInterop); }

function _interopRequireWildcard(obj, nodeInterop) { if (!nodeInterop && obj && obj.__esModule) { return obj; } if (obj === null || typeof obj !== "object" && typeof obj !== "function") { return { default: obj }; } var cache = _getRequireWildcardCache(nodeInterop); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (key !== "default" && Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj.default = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class FilterState {
  constructor() {
    this.renderTarget = null;
    this.target = null;
    this.resolution = 1;
    this.sourceFrame = new _math.Rectangle();
    this.destinationFrame = new _math.Rectangle();
    this.filters = [];
  }

  clear() {
    this.filters = null;
    this.target = null;
    this.renderTarget = null;
  }

}

var screenKey = "screen";

class FilterManager extends _WebGLManager.default {
  constructor(renderer) {
    super(renderer);
    this.gl = this.renderer.gl; // know about sprites!

    this.quad = new _Quad.default(this.gl, renderer.state.attribState);
    this.shaderCache = {}; // todo add default!

    this.pool = {};
    this.filterData = null;
    this.managedFilters = [];
    this.renderer.on("prerender", this.onPrerender, this);
    this._screenWidth = renderer.view.width;
    this._screenHeight = renderer.view.height;
  }

  pushFilter(target, filters) {
    var renderer = this.renderer;
    var filterData = this.filterData;

    if (!filterData) {
      filterData = this.renderer._activeRenderTarget.filterStack; // add new stack

      var filterState = new FilterState();
      filterState.sourceFrame = filterState.destinationFrame = this.renderer._activeRenderTarget.size;
      filterState.renderTarget = renderer._activeRenderTarget;
      this.renderer._activeRenderTarget.filterData = filterData = {
        index: 0,
        stack: [filterState]
      };
      this.filterData = filterData;
    } // get the current filter state..


    var currentState = filterData.stack[++filterData.index];
    var renderTargetFrame = filterData.stack[0].destinationFrame;

    if (!currentState) {
      currentState = filterData.stack[filterData.index] = new FilterState();
    }

    var fullScreen = target.filterArea && target.filterArea.x === 0 && target.filterArea.y === 0 && target.filterArea.width === renderer.screen.width && target.filterArea.height === renderer.screen.height; // for now we go off the filter of the first resolution..

    var resolution = filters[0].resolution;
    var padding = filters[0].padding | 0;
    var targetBounds = fullScreen ? renderer.screen : target.filterArea || target.getBounds(true);
    var sourceFrame = currentState.sourceFrame;
    var destinationFrame = currentState.destinationFrame;
    sourceFrame.x = (targetBounds.x * resolution | 0) / resolution;
    sourceFrame.y = (targetBounds.y * resolution | 0) / resolution;
    sourceFrame.width = (targetBounds.width * resolution | 0) / resolution;
    sourceFrame.height = (targetBounds.height * resolution | 0) / resolution;

    if (!fullScreen) {
      if (filterData.stack[0].renderTarget.transform) {} else if (filters[0].autoFit) {
        sourceFrame.fit(renderTargetFrame);
      }

      sourceFrame.pad(padding);
    }

    destinationFrame.width = sourceFrame.width;
    destinationFrame.height = sourceFrame.height;
    var renderTarget = this.getPotRenderTarget(renderer.gl, sourceFrame.width, sourceFrame.height, resolution);
    currentState.target = target;
    currentState.filters = filters;
    currentState.resolution = resolution;
    currentState.renderTarget = renderTarget;
    renderTarget.setFrame(destinationFrame, sourceFrame);
    renderer.bindRenderTarget(renderTarget);
    renderTarget.clear();
  }

  popFilter() {
    var filterData = this.filterData;
    var lastState = filterData.stack[filterData.index - 1];
    var currentState = filterData.stack[filterData.index];
    this.quad.map(currentState.renderTarget.size, currentState.sourceFrame).upload();
    var filters = currentState.filters;

    if (filters.length === 1) {
      filters[0].apply(this, currentState.renderTarget, lastState.renderTarget, false, currentState);
      this.freePotRenderTarget(currentState.renderTarget);
    } else {
      var flip = currentState.renderTarget;
      var flop = this.getPotRenderTarget(this.renderer.gl, currentState.sourceFrame.width, currentState.sourceFrame.height, currentState.resolution);
      flop.setFrame(currentState.destinationFrame, currentState.sourceFrame); // finally lets clear the render target before drawing to it..

      flop.clear();
      var i = 0;

      for (i = 0; i < filters.length - 1; ++i) {
        filters[i].apply(this, flip, flop, true, currentState);
        var t = flip;
        flip = flop;
        flop = t;
      }

      filters[i].apply(this, flip, lastState.renderTarget, false, currentState);
      this.freePotRenderTarget(flip);
      this.freePotRenderTarget(flop);
    }

    currentState.clear();
    filterData.index--;

    if (filterData.index === 0) {
      this.filterData = null;
    }
  }

  applyFilter(filter, input, output, clear) {
    var renderer = this.renderer;
    var gl = renderer.gl;
    var shader = filter.glShaders[renderer.CONTEXT_UID]; // caching..

    if (!shader) {
      if (filter.glShaderKey) {
        shader = this.shaderCache[filter.glShaderKey];

        if (!shader) {
          shader = new _Shader.default(this.gl, filter.vertexSrc, filter.fragmentSrc);
          filter.glShaders[renderer.CONTEXT_UID] = this.shaderCache[filter.glShaderKey] = shader;
          this.managedFilters.push(filter);
        }
      } else {
        shader = filter.glShaders[renderer.CONTEXT_UID] = new _Shader.default(this.gl, filter.vertexSrc, filter.fragmentSrc);
        this.managedFilters.push(filter);
      } // TODO - this only needs to be done once?


      renderer.bindVao(null);
      this.quad.initVao(shader);
    }

    renderer.bindVao(this.quad.vao);
    renderer.bindRenderTarget(output);

    if (clear) {
      gl.disable(gl.SCISSOR_TEST);
      renderer.clear(); // [1, 1, 1, 1]);

      gl.enable(gl.SCISSOR_TEST);
    } // in case the render target is being masked using a scissor rect


    if (output === renderer.maskManager.scissorRenderTarget) {
      renderer.maskManager.pushScissorMask(null, renderer.maskManager.scissorData);
    }

    renderer.bindShader(shader); // free unit 0 for us, doesn't matter what was there
    // don't try to restore it, because syncUniforms can upload it to another slot
    // and it'll be a problem

    var tex = this.renderer.emptyTextures[0];
    this.renderer.boundTextures[0] = tex; // this syncs the PixiJS filters  uniforms with glsl uniforms

    this.syncUniforms(shader, filter);
    renderer.state.setBlendMode(filter.blendMode);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, input.texture.texture);
    this.quad.vao.draw(this.renderer.gl.TRIANGLES, 6, 0);
    gl.bindTexture(gl.TEXTURE_2D, tex._glTextures[this.renderer.CONTEXT_UID].texture);
  }

  syncUniforms(shader, filter) {
    var uniformData = filter.uniformData;
    var uniforms = filter.uniforms; // 0 is reserved for the PixiJS texture so we start at 1!

    var textureCount = 1;
    var currentState; // filterArea and filterClamp that are handled by FilterManager directly
    // they must not appear in uniformData

    if (shader.uniforms.filterArea) {
      currentState = this.filterData.stack[this.filterData.index];
      var filterArea = shader.uniforms.filterArea;
      filterArea[0] = currentState.renderTarget.size.width;
      filterArea[1] = currentState.renderTarget.size.height;
      filterArea[2] = currentState.sourceFrame.x;
      filterArea[3] = currentState.sourceFrame.y;
      shader.uniforms.filterArea = filterArea;
    } // use this to clamp displaced texture coords so they belong to filterArea
    // see displacementFilter fragment shader for an example


    if (shader.uniforms.filterClamp) {
      currentState = currentState || this.filterData.stack[this.filterData.index];
      var filterClamp = shader.uniforms.filterClamp;
      filterClamp[0] = 0;
      filterClamp[1] = 0;
      filterClamp[2] = (currentState.sourceFrame.width - 1) / currentState.renderTarget.size.width;
      filterClamp[3] = (currentState.sourceFrame.height - 1) / currentState.renderTarget.size.height;
      shader.uniforms.filterClamp = filterClamp;
    } // TODO Caching layer..


    for (var i in uniformData) {
      if (!shader.uniforms.data[i]) {
        continue;
      }

      var type = uniformData[i].type;

      if (type === "sampler2d" && uniforms[i] !== 0) {
        if (uniforms[i].baseTexture) {
          shader.uniforms[i] = this.renderer.bindTexture(uniforms[i].baseTexture, textureCount);
        } else {
          shader.uniforms[i] = textureCount; // TODO
          // this is helpful as renderTargets can also be set.
          // Although thinking about it, we could probably
          // make the filter texture cache return a RenderTexture
          // rather than a renderTarget

          var gl = this.renderer.gl;
          this.renderer.boundTextures[textureCount] = this.renderer.emptyTextures[textureCount];
          gl.activeTexture(gl.TEXTURE0 + textureCount);
          uniforms[i].texture.bind();
        }

        textureCount++;
      } else if (type === "mat3") {
        // check if its PixiJS matrix..
        if (uniforms[i].a !== undefined) {
          shader.uniforms[i] = uniforms[i].toArray(true);
        } else {
          shader.uniforms[i] = uniforms[i];
        }
      } else if (type === "vec2") {
        // check if its a point..
        if (uniforms[i].x !== undefined) {
          var val = shader.uniforms[i] || new Float32Array(2);
          val[0] = uniforms[i].x;
          val[1] = uniforms[i].y;
          shader.uniforms[i] = val;
        } else {
          shader.uniforms[i] = uniforms[i];
        }
      } else if (type === "float") {
        if (shader.uniforms.data[i].value !== uniformData[i]) {
          shader.uniforms[i] = uniforms[i];
        }
      } else {
        shader.uniforms[i] = uniforms[i];
      }
    }
  }

  getRenderTarget(clear, resolution) {
    var currentState = this.filterData.stack[this.filterData.index];
    var renderTarget = this.getPotRenderTarget(this.renderer.gl, currentState.sourceFrame.width, currentState.sourceFrame.height, resolution || currentState.resolution);
    renderTarget.setFrame(currentState.destinationFrame, currentState.sourceFrame);
    return renderTarget;
  }

  returnRenderTarget(renderTarget) {
    this.freePotRenderTarget(renderTarget);
  }

  calculateScreenSpaceMatrix(outputMatrix) {
    var currentState = this.filterData.stack[this.filterData.index];
    return filterTransforms.calculateScreenSpaceMatrix(outputMatrix, currentState.sourceFrame, currentState.renderTarget.size);
  }

  calculateNormalizedScreenSpaceMatrix(outputMatrix) {
    var currentState = this.filterData.stack[this.filterData.index];
    return filterTransforms.calculateNormalizedScreenSpaceMatrix(outputMatrix, currentState.sourceFrame, currentState.renderTarget.size, currentState.destinationFrame);
  }

  calculateSpriteMatrix(outputMatrix, sprite) {
    var currentState = this.filterData.stack[this.filterData.index];
    return filterTransforms.calculateSpriteMatrix(outputMatrix, currentState.sourceFrame, currentState.renderTarget.size, sprite);
  }

  destroy(contextLost) {
    if (contextLost === void 0) {
      contextLost = false;
    }

    var renderer = this.renderer;
    var filters = this.managedFilters;
    renderer.off("prerender", this.onPrerender, this);

    for (var i = 0; i < filters.length; i++) {
      if (!contextLost) {
        filters[i].glShaders[renderer.CONTEXT_UID].destroy();
      }

      delete filters[i].glShaders[renderer.CONTEXT_UID];
    }

    this.shaderCache = {};

    if (!contextLost) {
      this.emptyPool();
    } else {
      this.pool = {};
    }
  }

  getPotRenderTarget(gl, minWidth, minHeight, resolution) {
    var key = screenKey;
    minWidth *= resolution;
    minHeight *= resolution;

    if (minWidth !== this._screenWidth || minHeight !== this._screenHeight) {
      // TODO you could return a bigger texture if there is not one in the pool?
      minWidth = _bitTwiddle.default.nextPow2(minWidth);
      minHeight = _bitTwiddle.default.nextPow2(minHeight);
      key = (minWidth & 0xffff) << 16 | minHeight & 0xffff;
    }

    if (!this.pool[key]) {
      this.pool[key] = [];
    }

    var renderTarget = this.pool[key].pop(); // creating render target will cause texture to be bound!

    if (!renderTarget) {
      // temporary bypass cache..
      var tex = this.renderer.boundTextures[0];
      gl.activeTexture(gl.TEXTURE0); // internally - this will cause a texture to be bound..

      renderTarget = new _RenderTarget.default(gl, minWidth, minHeight, null, 1); // set the current one back

      gl.bindTexture(gl.TEXTURE_2D, tex._glTextures[this.renderer.CONTEXT_UID].texture);
    } // manually tweak the resolution...
    // this will not modify the size of the frame buffer, just its resolution.


    renderTarget.resolution = resolution;
    renderTarget.defaultFrame.width = renderTarget.size.width = minWidth / resolution;
    renderTarget.defaultFrame.height = renderTarget.size.height = minHeight / resolution;
    renderTarget.filterPoolKey = key;
    return renderTarget;
  }

  emptyPool() {
    for (var i in this.pool) {
      var textures = this.pool[i];

      if (textures) {
        for (var j = 0; j < textures.length; j++) {
          textures[j].destroy(true);
        }
      }
    }

    this.pool = {};
  }

  freePotRenderTarget(renderTarget) {
    this.pool[renderTarget.filterPoolKey].push(renderTarget);
  }

  onPrerender() {
    if (this._screenWidth !== this.renderer.view.width || this._screenHeight !== this.renderer.view.height) {
      this._screenWidth = this.renderer.view.width;
      this._screenHeight = this.renderer.view.height;
      var textures = this.pool[screenKey];

      if (textures) {
        for (var j = 0; j < textures.length; j++) {
          textures[j].destroy(true);
        }
      }

      this.pool[screenKey] = [];
    }
  }

}

exports.default = FilterManager;
//# sourceMappingURL=FilterManager.js.map