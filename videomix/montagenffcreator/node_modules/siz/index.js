(function(global, factory) {
  if (typeof define === "function" && define.amd) {
    define([], factory);
  } else if (typeof module !== "undefined" && module.exports) {
    module.exports = factory();
  } else {
    global.siz = factory();
  }
})(this, function() {
  function siz(size) {
    var num = parseInt(size);
    if (/[0-9]*k(b|B)?/gi.test(size)) {
      return num * 1024;
    }

    if (/[0-9]*m(b|B)?/gi.test(size)) {
      return num * 1024 * 1024;
    }

    if (/[0-9]*g(b|B)?/gi.test(size)) {
      return num * 1024 * 1024 * 1024;
    }

    if (/[0-9]*t(b|B)?/gi.test(size)) {
      return num * 1024 * 1024 * 1024 * 1024;
    }

    return num;
  }

  return siz;
});
