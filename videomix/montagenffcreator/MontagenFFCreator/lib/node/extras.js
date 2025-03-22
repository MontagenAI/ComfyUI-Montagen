'use strict';

/**
 * FFExtras - A component that can be expanded freely
 *
 * ####Example:
 *
 *     const extras = new FFExtras();
 *     extras.init = function(InkPaint){ ... }
 *     extras.update = function(InkPaint){ ... }
 *     extras.destroyed = function(InkPaint){ ... }
 *     scene.addChild(extras);
 *
 * @class
 */
const InkPaint = require('../../inkpaint/lib/index');
const FFNode = require('./node');

class FFExtras extends FFNode {
  constructor(conf = {}) {
    super({ type: 'extras', ...conf });
  }

  createDisplay() {
    this.display = new InkPaint.Container();
    this.container = this.display;
  }

  enable() {
    super.enable();
    this.enableFn && this.enableFn(InkPaint);
    this.emit('enable');
  }

  disable() {
    super.disable();
    this.disableFn && this.disableFn(InkPaint);
    this.emit('disable');
  }

  drawing(time, delta) {
    super.drawing(time, delta);
    this.update && this.update(InkPaint, time, delta);
    this.emit('update');
  }

  destroyContainer() {
    try {
      this.container.destroy();
      this.container.removeAllChildren();
    } catch (e) {}
  }

  destroy() {
    super.destroy();
    this.destroyContainer();

    this.destroyed && this.destroyed(InkPaint);
    this.emit('destroy');

    this.enableFn = null;
    this.disableFn = null;
    this.update = null;
    this.container = null;
  }
}

module.exports = FFExtras;
