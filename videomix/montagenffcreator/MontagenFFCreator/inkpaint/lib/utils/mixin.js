"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.delayMixin = delayMixin;
exports.mixin = mixin;
exports.performMixins = performMixins;

function mixin(target, source) {
  if (!target || !source) return;
  var keys = Object.keys(source); // loop through properties

  for (var i = 0; i < keys.length; ++i) {
    var propertyName = keys[i]; // Set the property using the property descriptor - this works for accessors and normal value properties

    Object.defineProperty(target, propertyName, Object.getOwnPropertyDescriptor(source, propertyName));
  }
}

var mixins = [];

function delayMixin(target, source) {
  mixins.push(target, source);
}

function performMixins() {
  for (var i = 0; i < mixins.length; i += 2) {
    mixin(mixins[i], mixins[i + 1]);
  }

  mixins.length = 0;
}
//# sourceMappingURL=mixin.js.map