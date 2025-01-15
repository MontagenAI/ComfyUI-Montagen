"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;

class TickerListener {
  constructor(fn, context, priority, once) {
    if (context === void 0) {
      context = null;
    }

    if (priority === void 0) {
      priority = 0;
    }

    if (once === void 0) {
      once = false;
    }

    this.fn = fn;
    this.context = context;
    this.priority = priority;
    this.once = once;
    this.next = null;
    this.previous = null;
    this.destroyed = false;
  }

  match(fn, context) {
    context = context || null;
    return this.fn === fn && this.context === context;
  }

  emit(deltaTime) {
    if (this.fn) {
      if (this.context) {
        this.fn.call(this.context, deltaTime);
      } else {
        this.fn(deltaTime);
      }
    }

    var redirect = this.next;

    if (this.once) {
      this.destroy(true);
    }

    if (this.destroyed) {
      this.next = null;
    }

    return redirect;
  }

  connect(previous) {
    this.previous = previous;

    if (previous.next) {
      previous.next.previous = this;
    }

    this.next = previous.next;
    previous.next = this;
  }

  destroy(hard) {
    if (hard === void 0) {
      hard = false;
    }

    if (this.destroyed) return;
    this.destroyed = true;
    this.fn = null;
    this.context = null; // Disconnect, hook up next and previous

    if (this.previous) {
      this.previous.next = this.next;
    }

    if (this.next) {
      this.next.previous = this.previous;
    } // Redirect to the next item


    var redirect = this.next; // Remove references

    this.next = hard ? null : redirect;
    this.previous = null;
    return redirect;
  }

}

exports.default = TickerListener;
//# sourceMappingURL=TickerListener.js.map