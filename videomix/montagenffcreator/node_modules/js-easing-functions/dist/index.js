"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function easeInQuad(elapsed, initialValue, amountOfChange, duration) {
    return amountOfChange * (elapsed /= duration) * elapsed + initialValue;
}
exports.easeInQuad = easeInQuad;
function easeOutQuad(elapsed, initialValue, amountOfChange, duration) {
    return -amountOfChange * (elapsed /= duration) * (elapsed - 2) + initialValue;
}
exports.easeOutQuad = easeOutQuad;
function easeInOutQuad(elapsed, initialValue, amountOfChange, duration) {
    if ((elapsed /= duration / 2) < 1) {
        return amountOfChange / 2 * elapsed * elapsed + initialValue;
    }
    return -amountOfChange / 2 * (--elapsed * (elapsed - 2) - 1) + initialValue;
}
exports.easeInOutQuad = easeInOutQuad;
function easeInCubic(elapsed, initialValue, amountOfChange, duration) {
    return amountOfChange * (elapsed /= duration) * elapsed * elapsed + initialValue;
}
exports.easeInCubic = easeInCubic;
function easeOutCubic(elapsed, initialValue, amountOfChange, duration) {
    return amountOfChange * ((elapsed = elapsed / duration - 1) * elapsed * elapsed + 1) + initialValue;
}
exports.easeOutCubic = easeOutCubic;
function easeInOutCubic(elapsed, initialValue, amountOfChange, duration) {
    if ((elapsed /= duration / 2) < 1) {
        return amountOfChange / 2 * elapsed * elapsed * elapsed + initialValue;
    }
    return amountOfChange / 2 * ((elapsed -= 2) * elapsed * elapsed + 2) + initialValue;
}
exports.easeInOutCubic = easeInOutCubic;
function easeInQuart(elapsed, initialValue, amountOfChange, duration) {
    return amountOfChange * (elapsed /= duration) * elapsed * elapsed * elapsed + initialValue;
}
exports.easeInQuart = easeInQuart;
function easeOutQuart(elapsed, initialValue, amountOfChange, duration) {
    return -amountOfChange * ((elapsed = elapsed / duration - 1) * elapsed * elapsed * elapsed - 1) + initialValue;
}
exports.easeOutQuart = easeOutQuart;
function easeInOutQuart(elapsed, initialValue, amountOfChange, duration) {
    if ((elapsed /= duration / 2) < 1) {
        return amountOfChange / 2 * elapsed * elapsed * elapsed * elapsed + initialValue;
    }
    return -amountOfChange / 2 * ((elapsed -= 2) * elapsed * elapsed * elapsed - 2) + initialValue;
}
exports.easeInOutQuart = easeInOutQuart;
function easeInQuint(elapsed, initialValue, amountOfChange, duration) {
    return amountOfChange * (elapsed /= duration) * elapsed * elapsed * elapsed * elapsed + initialValue;
}
exports.easeInQuint = easeInQuint;
function easeOutQuint(elapsed, initialValue, amountOfChange, duration) {
    return amountOfChange * ((elapsed = elapsed / duration - 1) * elapsed * elapsed * elapsed * elapsed + 1) + initialValue;
}
exports.easeOutQuint = easeOutQuint;
function easeInOutQuint(elapsed, initialValue, amountOfChange, duration) {
    if ((elapsed /= duration / 2) < 1) {
        return amountOfChange / 2 * elapsed * elapsed * elapsed * elapsed * elapsed + initialValue;
    }
    return amountOfChange / 2 * ((elapsed -= 2) * elapsed * elapsed * elapsed * elapsed + 2) + initialValue;
}
exports.easeInOutQuint = easeInOutQuint;
function easeInSine(elapsed, initialValue, amountOfChange, duration) {
    return -amountOfChange * Math.cos(elapsed / duration * (Math.PI / 2)) + amountOfChange + initialValue;
}
exports.easeInSine = easeInSine;
function easeOutSine(elapsed, initialValue, amountOfChange, duration) {
    return amountOfChange * Math.sin(elapsed / duration * (Math.PI / 2)) + initialValue;
}
exports.easeOutSine = easeOutSine;
function easeInOutSine(elapsed, initialValue, amountOfChange, duration) {
    return -amountOfChange / 2 * (Math.cos(Math.PI * elapsed / duration) - 1) + initialValue;
}
exports.easeInOutSine = easeInOutSine;
function easeInExpo(elapsed, initialValue, amountOfChange, duration) {
    return elapsed === 0 ? initialValue : amountOfChange * Math.pow(2, 10 * (elapsed / duration - 1)) + initialValue;
}
exports.easeInExpo = easeInExpo;
function easeOutExpo(elapsed, initialValue, amountOfChange, duration) {
    return elapsed === duration
        ? initialValue + amountOfChange
        : amountOfChange * (-Math.pow(2, -10 * elapsed / duration) + 1) + initialValue;
}
exports.easeOutExpo = easeOutExpo;
function easeInOutExpo(elapsed, initialValue, amountOfChange, duration) {
    if (elapsed === 0) {
        return initialValue;
    }
    if (elapsed === duration) {
        return initialValue + amountOfChange;
    }
    if ((elapsed /= duration / 2) < 1) {
        return amountOfChange / 2 * Math.pow(2, 10 * (elapsed - 1)) + initialValue;
    }
    return amountOfChange / 2 * (-Math.pow(2, -10 * --elapsed) + 2) + initialValue;
}
exports.easeInOutExpo = easeInOutExpo;
function easeInCirc(elapsed, initialValue, amountOfChange, duration) {
    return -amountOfChange * (Math.sqrt(1 - (elapsed /= duration) * elapsed) - 1) + initialValue;
}
exports.easeInCirc = easeInCirc;
function easeOutCirc(elapsed, initialValue, amountOfChange, duration) {
    return amountOfChange * Math.sqrt(1 - (elapsed = elapsed / duration - 1) * elapsed) + initialValue;
}
exports.easeOutCirc = easeOutCirc;
function easeInOutCirc(elapsed, initialValue, amountOfChange, duration) {
    if ((elapsed /= duration / 2) < 1) {
        return -amountOfChange / 2 * (Math.sqrt(1 - elapsed * elapsed) - 1) + initialValue;
    }
    return amountOfChange / 2 * (Math.sqrt(1 - (elapsed -= 2) * elapsed) + 1) + initialValue;
}
exports.easeInOutCirc = easeInOutCirc;
function easeInElastic(elapsed, initialValue, amountOfChange, duration) {
    var s = 1.70158;
    var p = 0;
    var a = amountOfChange;
    if (elapsed === 0) {
        return initialValue;
    }
    if ((elapsed /= duration) === 1) {
        return initialValue + amountOfChange;
    }
    if (!p) {
        p = duration * 0.3;
    }
    if (a < Math.abs(amountOfChange)) {
        a = amountOfChange;
        s = p / 4;
    }
    else {
        s = p / (2 * Math.PI) * Math.asin(amountOfChange / a);
    }
    return -(a * Math.pow(2, 10 * (elapsed -= 1)) * Math.sin((elapsed * duration - s) * (2 * Math.PI) / p)) + initialValue;
}
exports.easeInElastic = easeInElastic;
function easeOutElastic(elapsed, initialValue, amountOfChange, duration) {
    var s = 1.70158;
    var p = 0;
    var a = amountOfChange;
    if (elapsed === 0) {
        return initialValue;
    }
    if ((elapsed /= duration) === 1) {
        return initialValue + amountOfChange;
    }
    if (!p) {
        p = duration * 0.3;
    }
    if (a < Math.abs(amountOfChange)) {
        a = amountOfChange;
        s = p / 4;
    }
    else {
        s = p / (2 * Math.PI) * Math.asin(amountOfChange / a);
    }
    return a * Math.pow(2, -10 * elapsed) * Math.sin((elapsed * duration - s) * (2 * Math.PI) / p) + amountOfChange + initialValue;
}
exports.easeOutElastic = easeOutElastic;
function easeInOutElastic(elapsed, initialValue, amountOfChange, duration) {
    var s = 1.70158;
    var p = 0;
    var a = amountOfChange;
    if (elapsed === 0) {
        return initialValue;
    }
    if ((elapsed /= duration / 2) === 2) {
        return initialValue + amountOfChange;
    }
    if (!p) {
        p = duration * (0.3 * 1.5);
    }
    if (a < Math.abs(amountOfChange)) {
        a = amountOfChange;
        s = p / 4;
    }
    else {
        s = p / (2 * Math.PI) * Math.asin(amountOfChange / a);
    }
    if (elapsed < 1) {
        return -0.5 * (a * Math.pow(2, 10 * (elapsed -= 1)) * Math.sin((elapsed * duration - s) * (2 * Math.PI) / p)) + initialValue;
    }
    return (a * Math.pow(2, -10 * (elapsed -= 1)) * Math.sin((elapsed * duration - s) * (2 * Math.PI) / p) * 0.5 + amountOfChange + initialValue);
}
exports.easeInOutElastic = easeInOutElastic;
function easeInBack(elapsed, initialValue, amountOfChange, duration, s) {
    if (s === void 0) { s = 1.70158; }
    return amountOfChange * (elapsed /= duration) * elapsed * ((s + 1) * elapsed - s) + initialValue;
}
exports.easeInBack = easeInBack;
function easeOutBack(elapsed, initialValue, amountOfChange, duration, s) {
    if (s === void 0) { s = 1.70158; }
    return amountOfChange * ((elapsed = elapsed / duration - 1) * elapsed * ((s + 1) * elapsed + s) + 1) + initialValue;
}
exports.easeOutBack = easeOutBack;
function easeInOutBack(elapsed, initialValue, amountOfChange, duration, s) {
    if (s === void 0) { s = 1.70158; }
    if ((elapsed /= duration / 2) < 1) {
        return amountOfChange / 2 * (elapsed * elapsed * (((s *= 1.525) + 1) * elapsed - s)) + initialValue;
    }
    return amountOfChange / 2 * ((elapsed -= 2) * elapsed * (((s *= 1.525) + 1) * elapsed + s) + 2) + initialValue;
}
exports.easeInOutBack = easeInOutBack;
function easeInBounce(elapsed, initialValue, amountOfChange, duration) {
    return amountOfChange - easeOutBounce(duration - elapsed, 0, amountOfChange, duration) + initialValue;
}
exports.easeInBounce = easeInBounce;
function easeOutBounce(elapsed, initialValue, amountOfChange, duration) {
    if ((elapsed /= duration) < 1 / 2.75) {
        return amountOfChange * (7.5625 * elapsed * elapsed) + initialValue;
    }
    else if (elapsed < 2 / 2.75) {
        return amountOfChange * (7.5625 * (elapsed -= 1.5 / 2.75) * elapsed + 0.75) + initialValue;
    }
    else if (elapsed < 2.5 / 2.75) {
        return amountOfChange * (7.5625 * (elapsed -= 2.25 / 2.75) * elapsed + 0.9375) + initialValue;
    }
    else {
        return amountOfChange * (7.5625 * (elapsed -= 2.625 / 2.75) * elapsed + 0.984375) + initialValue;
    }
}
exports.easeOutBounce = easeOutBounce;
function easeInOutBounce(elapsed, initialValue, amountOfChange, duration) {
    if (elapsed < duration / 2) {
        return easeInBounce(elapsed * 2, 0, amountOfChange, duration) * 0.5 + initialValue;
    }
    return easeOutBounce(elapsed * 2 - duration, 0, amountOfChange, duration) * 0.5 + amountOfChange * 0.5 + initialValue;
}
exports.easeInOutBounce = easeInOutBounce;
