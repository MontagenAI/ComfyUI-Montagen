"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

var _Sprite = _interopRequireDefault(require("./Sprite"));

var _ticker = require("../ticker");

var _Maths = _interopRequireDefault(require("../math/Maths"));

var _Texture = _interopRequireDefault(require("../textures/Texture"));

var _const = require("../const");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

class AnimatedSprite extends _Sprite.default {
  constructor(textures, autoUpdate) {
    super(textures[0] instanceof _Texture.default ? textures[0] : textures[0].texture);
    this._textures = null;
    this._durations = null;
    this.textures = textures;
    this._autoUpdate = autoUpdate !== false;
    this.animationSpeed = 1;
    this.loop = true;
    this.updateAnchor = false;
    this.onComplete = null;
    this.onFrameChange = null;
    this.onLoop = null;
    this._currentTime = 0;
    this.playing = false;
  }

  stop() {
    if (!this.playing) return;
    this.playing = false;

    if (this._autoUpdate) {
      _ticker.shared.remove(this.update, this);
    }
  }

  play() {
    if (this.playing) return;
    this.playing = true;

    if (this._autoUpdate) {
      _ticker.shared.add(this.update, this, _const.UPDATE_PRIORITY.HIGH);
    }
  }

  gotoAndStop(frameNumber) {
    this.stop();
    var previousFrame = this.currentFrame;
    this._currentTime = frameNumber;

    if (previousFrame !== this.currentFrame) {
      this.updateTexture();
    }
  }

  gotoAndPlay(frameNumber) {
    var previousFrame = this.currentFrame;
    this._currentTime = frameNumber;

    if (previousFrame !== this.currentFrame) {
      this.updateTexture();
    }

    this.play();
  }

  update(deltaTime) {
    var elapsed = this.animationSpeed * deltaTime;
    var previousFrame = this.currentFrame;

    if (this._durations !== null) {
      var lag = this._currentTime % 1 * this._durations[this.currentFrame];
      lag += elapsed / 60 * 1000;

      while (lag < 0) {
        this._currentTime--;
        lag += this._durations[this.currentFrame];
      }

      var sign = _Maths.default.sign(this.animationSpeed * deltaTime);

      this._currentTime = Math.floor(this._currentTime);

      while (lag >= this._durations[this.currentFrame]) {
        lag -= this._durations[this.currentFrame] * sign;
        this._currentTime += sign;
      }

      this._currentTime += lag / this._durations[this.currentFrame];
    } else {
      this._currentTime += elapsed;
    }

    if (this._currentTime < 0 && !this.loop) {
      this.gotoAndStop(0);

      if (this.onComplete) {
        this.onComplete();
      }
    } else if (this._currentTime >= this._textures.length && !this.loop) {
      this.gotoAndStop(this._textures.length - 1);

      if (this.onComplete) {
        this.onComplete();
      }
    } else if (previousFrame !== this.currentFrame) {
      if (this.loop && this.onLoop) {
        if (this.animationSpeed > 0 && this.currentFrame < previousFrame) {
          this.onLoop();
        } else if (this.animationSpeed < 0 && this.currentFrame > previousFrame) {
          this.onLoop();
        }
      }

      this.updateTexture();
    }
  }

  updateTexture() {
    this._texture = this._textures[this.currentFrame];
    this._textureID = -1;
    this.cachedTint = 0xffffff;

    if (this.updateAnchor) {
      this._anchor.copy(this._texture.defaultAnchor);
    }

    if (this.onFrameChange) {
      this.onFrameChange(this.currentFrame);
    }
  }

  destroy(options) {
    this.stop();
    super.destroy(options);
  }

  static fromFrames(frames) {
    var textures = [];

    for (var i = 0; i < frames.length; ++i) {
      textures.push(_Texture.default.fromFrame(frames[i]));
    }

    return new AnimatedSprite(textures);
  }

  static fromImages(images) {
    var textures = [];

    for (var i = 0; i < images.length; ++i) {
      textures.push(_Texture.default.fromImage(images[i]));
    }

    return new AnimatedSprite(textures);
  }

  get totalFrames() {
    return this._textures.length;
  }

  get textures() {
    return this._textures;
  }

  set textures(value) {
    if (value[0] instanceof _Texture.default) {
      this._textures = value;
      this._durations = null;
    } else {
      this._textures = [];
      this._durations = [];

      for (var i = 0; i < value.length; i++) {
        this._textures.push(value[i].texture);

        this._durations.push(value[i].time);
      }
    }

    this.gotoAndStop(0);
    this.updateTexture();
  }

  get currentFrame() {
    var currentFrame = Math.floor(this._currentTime) % this._textures.length;

    if (currentFrame < 0) {
      currentFrame += this._textures.length;
    }

    return currentFrame;
  }

}

exports.default = AnimatedSprite;
//# sourceMappingURL=AnimatedSprite.js.map