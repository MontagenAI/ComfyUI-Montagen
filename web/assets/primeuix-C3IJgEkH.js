function hasClass(element, className) {
  if (element) {
    if (element.classList) return element.classList.contains(className);
    else return new RegExp("(^| )" + className + "( |$)", "gi").test(element.className);
  }
  return false;
}
function addClass(element, className) {
  if (element && className) {
    const fn = (_className) => {
      if (!hasClass(element, _className)) {
        if (element.classList) element.classList.add(_className);
        else element.className += " " + _className;
      }
    };
    [className].flat().filter(Boolean).forEach((_classNames) => _classNames.split(" ").forEach(fn));
  }
}
function calculateBodyScrollbarWidth() {
  return window.innerWidth - document.documentElement.offsetWidth;
}
function blockBodyScroll(option) {
  if (typeof option === "string") {
    addClass(document.body, option || "p-overflow-hidden");
  } else {
    (option == null ? void 0 : option.variableName) && document.body.style.setProperty(option.variableName, calculateBodyScrollbarWidth() + "px");
    addClass(document.body, (option == null ? void 0 : option.className) || "p-overflow-hidden");
  }
}
function removeClass(element, className) {
  if (element && className) {
    const fn = (_className) => {
      if (element.classList) element.classList.remove(_className);
      else element.className = element.className.replace(new RegExp("(^|\\b)" + _className.split(" ").join("|") + "(\\b|$)", "gi"), " ");
    };
    [className].flat().filter(Boolean).forEach((_classNames) => _classNames.split(" ").forEach(fn));
  }
}
function unblockBodyScroll(option) {
  if (typeof option === "string") {
    removeClass(document.body, option || "p-overflow-hidden");
  } else {
    if (option == null ? void 0 : option.variableName) document.body.style.removeProperty(option.variableName);
    removeClass(document.body, (option == null ? void 0 : option.className) || "p-overflow-hidden");
  }
}
function getCSSVariableByRegex(variableRegex) {
  for (const sheet of document == null ? void 0 : document.styleSheets) {
    try {
      for (const rule of sheet == null ? void 0 : sheet.cssRules) {
        for (const property of rule == null ? void 0 : rule.style) {
          if (variableRegex.test(property)) {
            return { name: property, value: rule.style.getPropertyValue(property).trim() };
          }
        }
      }
    } catch (e) {
    }
  }
  return null;
}
function getHiddenElementDimensions(element) {
  const dimensions = { width: 0, height: 0 };
  if (element) {
    element.style.visibility = "hidden";
    element.style.display = "block";
    dimensions.width = element.offsetWidth;
    dimensions.height = element.offsetHeight;
    element.style.display = "none";
    element.style.visibility = "visible";
  }
  return dimensions;
}
function getViewport() {
  const win = window, d = document, e = d.documentElement, g = d.getElementsByTagName("body")[0], w = win.innerWidth || e.clientWidth || g.clientWidth, h = win.innerHeight || e.clientHeight || g.clientHeight;
  return { width: w, height: h };
}
function getScrollLeft(element) {
  return element ? Math.abs(element.scrollLeft) : 0;
}
function getWindowScrollLeft() {
  const doc = document.documentElement;
  return (window.pageXOffset || getScrollLeft(doc)) - (doc.clientLeft || 0);
}
function getWindowScrollTop() {
  const doc = document.documentElement;
  return (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
}
function isRTL(element) {
  return element ? getComputedStyle(element).direction === "rtl" : false;
}
function absolutePosition(element, target, gutter = true) {
  var _a, _b, _c, _d;
  if (element) {
    const elementDimensions = element.offsetParent ? { width: element.offsetWidth, height: element.offsetHeight } : getHiddenElementDimensions(element);
    const elementOuterHeight = elementDimensions.height;
    const elementOuterWidth = elementDimensions.width;
    const targetOuterHeight = target.offsetHeight;
    const targetOuterWidth = target.offsetWidth;
    const targetOffset = target.getBoundingClientRect();
    const windowScrollTop = getWindowScrollTop();
    const windowScrollLeft = getWindowScrollLeft();
    const viewport = getViewport();
    let top, left, origin = "top";
    if (targetOffset.top + targetOuterHeight + elementOuterHeight > viewport.height) {
      top = targetOffset.top + windowScrollTop - elementOuterHeight;
      origin = "bottom";
      if (top < 0) {
        top = windowScrollTop;
      }
    } else {
      top = targetOuterHeight + targetOffset.top + windowScrollTop;
    }
    if (targetOffset.left + elementOuterWidth > viewport.width) left = Math.max(0, targetOffset.left + windowScrollLeft + targetOuterWidth - elementOuterWidth);
    else left = targetOffset.left + windowScrollLeft;
    if (isRTL(element)) {
      element.style.insetInlineEnd = left + "px";
    } else {
      element.style.insetInlineStart = left + "px";
    }
    element.style.top = top + "px";
    element.style.transformOrigin = origin;
    if (gutter) element.style.marginTop = origin === "bottom" ? `calc(${(_b = (_a = getCSSVariableByRegex(/-anchor-gutter$/)) == null ? void 0 : _a.value) != null ? _b : "2px"} * -1)` : (_d = (_c = getCSSVariableByRegex(/-anchor-gutter$/)) == null ? void 0 : _c.value) != null ? _d : "";
  }
}
function addStyle(element, style2) {
  if (element) {
    if (typeof style2 === "string") {
      element.style.cssText = style2;
    } else {
      Object.entries(style2 || {}).forEach(([key, value]) => element.style[key] = value);
    }
  }
}
function getOuterWidth(element, margin) {
  if (element instanceof HTMLElement) {
    let width = element.offsetWidth;
    if (margin) {
      const style2 = getComputedStyle(element);
      width += parseFloat(style2.marginLeft) + parseFloat(style2.marginRight);
    }
    return width;
  }
  return 0;
}
function relativePosition(element, target, gutter = true) {
  var _a, _b, _c, _d;
  if (element) {
    const elementDimensions = element.offsetParent ? { width: element.offsetWidth, height: element.offsetHeight } : getHiddenElementDimensions(element);
    const targetHeight = target.offsetHeight;
    const targetOffset = target.getBoundingClientRect();
    const viewport = getViewport();
    let top, left, origin = "top";
    if (targetOffset.top + targetHeight + elementDimensions.height > viewport.height) {
      top = -1 * elementDimensions.height;
      origin = "bottom";
      if (targetOffset.top + top < 0) {
        top = -1 * targetOffset.top;
      }
    } else {
      top = targetHeight;
    }
    if (elementDimensions.width > viewport.width) {
      left = targetOffset.left * -1;
    } else if (targetOffset.left + elementDimensions.width > viewport.width) {
      left = (targetOffset.left + elementDimensions.width - viewport.width) * -1;
    } else {
      left = 0;
    }
    element.style.top = top + "px";
    element.style.insetInlineStart = left + "px";
    element.style.transformOrigin = origin;
    gutter && (element.style.marginTop = origin === "bottom" ? `calc(${(_b = (_a = getCSSVariableByRegex(/-anchor-gutter$/)) == null ? void 0 : _a.value) != null ? _b : "2px"} * -1)` : (_d = (_c = getCSSVariableByRegex(/-anchor-gutter$/)) == null ? void 0 : _c.value) != null ? _d : "");
  }
}
function getParentNode(element) {
  if (element) {
    let parent = element.parentNode;
    if (parent && parent instanceof ShadowRoot && parent.host) {
      parent = parent.host;
    }
    return parent;
  }
  return null;
}
function isExist(element) {
  return !!(element !== null && typeof element !== "undefined" && element.nodeName && getParentNode(element));
}
function isElement(element) {
  return typeof Element !== "undefined" ? element instanceof Element : element !== null && typeof element === "object" && element.nodeType === 1 && typeof element.nodeName === "string";
}
var calculatedScrollbarWidth = void 0;
function calculateScrollbarWidth(element) {
  {
    if (calculatedScrollbarWidth != null) return calculatedScrollbarWidth;
    const scrollDiv = document.createElement("div");
    addStyle(scrollDiv, {
      width: "100px",
      height: "100px",
      overflow: "scroll",
      position: "absolute",
      top: "-9999px"
    });
    document.body.appendChild(scrollDiv);
    const scrollbarWidth = scrollDiv.offsetWidth - scrollDiv.clientWidth;
    document.body.removeChild(scrollDiv);
    calculatedScrollbarWidth = scrollbarWidth;
    return scrollbarWidth;
  }
}
function setAttributes(element, attributes = {}) {
  if (isElement(element)) {
    const computedStyles = (rule, value) => {
      var _a, _b;
      const styles = ((_a = element == null ? void 0 : element.$attrs) == null ? void 0 : _a[rule]) ? [(_b = element == null ? void 0 : element.$attrs) == null ? void 0 : _b[rule]] : [];
      return [value].flat().reduce((cv, v) => {
        if (v !== null && v !== void 0) {
          const type = typeof v;
          if (type === "string" || type === "number") {
            cv.push(v);
          } else if (type === "object") {
            const _cv = Array.isArray(v) ? computedStyles(rule, v) : Object.entries(v).map(([_k, _v]) => rule === "style" && (!!_v || _v === 0) ? `${_k.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase()}:${_v}` : _v ? _k : void 0);
            cv = _cv.length ? cv.concat(_cv.filter((c) => !!c)) : cv;
          }
        }
        return cv;
      }, styles);
    };
    Object.entries(attributes).forEach(([key, value]) => {
      if (value !== void 0 && value !== null) {
        const matchedEvent = key.match(/^on(.+)/);
        if (matchedEvent) {
          element.addEventListener(matchedEvent[1].toLowerCase(), value);
        } else if (key === "p-bind" || key === "pBind") {
          setAttributes(element, value);
        } else {
          value = key === "class" ? [...new Set(computedStyles("class", value))].join(" ").trim() : key === "style" ? computedStyles("style", value).join(";").trim() : value;
          (element.$attrs = element.$attrs || {}) && (element.$attrs[key] = value);
          element.setAttribute(key, value);
        }
      }
    });
  }
}
function createElement(type, attributes = {}, ...children) {
  if (type) {
    const element = document.createElement(type);
    setAttributes(element, attributes);
    element.append(...children);
    return element;
  }
  return void 0;
}
function fadeIn(element, duration) {
  if (element) {
    element.style.opacity = "0";
    let last = +/* @__PURE__ */ new Date();
    let opacity = "0";
    const tick = function() {
      opacity = `${+element.style.opacity + ((/* @__PURE__ */ new Date()).getTime() - last) / duration}`;
      element.style.opacity = opacity;
      last = +/* @__PURE__ */ new Date();
      if (+opacity < 1) {
        if ("requestAnimationFrame" in window) requestAnimationFrame(tick);
        else setTimeout(tick, 16);
      }
    };
    tick();
  }
}
function find(element, selector) {
  return isElement(element) ? Array.from(element.querySelectorAll(selector)) : [];
}
function findSingle(element, selector) {
  return isElement(element) ? element.matches(selector) ? element : element.querySelector(selector) : null;
}
function focus(element, options) {
  if (element && document.activeElement !== element) element.focus(options);
}
function getAttribute(element, name) {
  if (isElement(element)) {
    const value = element.getAttribute(name);
    if (!isNaN(value)) {
      return +value;
    }
    if (value === "true" || value === "false") {
      return value === "true";
    }
    return value;
  }
  return void 0;
}
function getFocusableElements(element, selector = "") {
  const focusableElements = find(
    element,
    `button:not([tabindex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            [href][clientHeight][clientWidth]:not([tabindex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            input:not([tabindex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            select:not([tabindex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            textarea:not([tabindex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            [tabIndex]:not([tabIndex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            [contenteditable]:not([tabIndex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector}`
  );
  const visibleFocusableElements = [];
  for (const focusableElement of focusableElements) {
    if (getComputedStyle(focusableElement).display != "none" && getComputedStyle(focusableElement).visibility != "hidden") visibleFocusableElements.push(focusableElement);
  }
  return visibleFocusableElements;
}
function getFirstFocusableElement(element, selector) {
  const focusableElements = getFocusableElements(element, selector);
  return focusableElements.length > 0 ? focusableElements[0] : null;
}
function getHeight(element) {
  if (element) {
    let height = element.offsetHeight;
    const style2 = getComputedStyle(element);
    height -= parseFloat(style2.paddingTop) + parseFloat(style2.paddingBottom) + parseFloat(style2.borderTopWidth) + parseFloat(style2.borderBottomWidth);
    return height;
  }
  return 0;
}
function getHiddenElementOuterHeight(element) {
  if (element) {
    element.style.visibility = "hidden";
    element.style.display = "block";
    const elementHeight = element.offsetHeight;
    element.style.display = "none";
    element.style.visibility = "visible";
    return elementHeight;
  }
  return 0;
}
function getHiddenElementOuterWidth(element) {
  if (element) {
    element.style.visibility = "hidden";
    element.style.display = "block";
    const elementWidth = element.offsetWidth;
    element.style.display = "none";
    element.style.visibility = "visible";
    return elementWidth;
  }
  return 0;
}
function getLastFocusableElement(element, selector) {
  const focusableElements = getFocusableElements(element, selector);
  return focusableElements.length > 0 ? focusableElements[focusableElements.length - 1] : null;
}
function getOffset(element) {
  if (element) {
    const rect = element.getBoundingClientRect();
    return {
      top: rect.top + (window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0),
      left: rect.left + (window.pageXOffset || getScrollLeft(document.documentElement) || getScrollLeft(document.body) || 0)
    };
  }
  return {
    top: "auto",
    left: "auto"
  };
}
function getOuterHeight(element, margin) {
  if (element) {
    let height = element.offsetHeight;
    if (margin) {
      const style2 = getComputedStyle(element);
      height += parseFloat(style2.marginTop) + parseFloat(style2.marginBottom);
    }
    return height;
  }
  return 0;
}
function getParents(element, parents = []) {
  const parent = getParentNode(element);
  return parent === null ? parents : getParents(parent, parents.concat([parent]));
}
function getScrollableParents(element) {
  const scrollableParents = [];
  if (element) {
    const parents = getParents(element);
    const overflowRegex = /(auto|scroll)/;
    const overflowCheck = (node) => {
      try {
        const styleDeclaration = window["getComputedStyle"](node, null);
        return overflowRegex.test(styleDeclaration.getPropertyValue("overflow")) || overflowRegex.test(styleDeclaration.getPropertyValue("overflowX")) || overflowRegex.test(styleDeclaration.getPropertyValue("overflowY"));
      } catch (e) {
        return false;
      }
    };
    for (const parent of parents) {
      const scrollSelectors = parent.nodeType === 1 && parent.dataset["scrollselectors"];
      if (scrollSelectors) {
        const selectors = scrollSelectors.split(",");
        for (const selector of selectors) {
          const el = findSingle(parent, selector);
          if (el && overflowCheck(el)) {
            scrollableParents.push(el);
          }
        }
      }
      if (parent.nodeType !== 9 && overflowCheck(parent)) {
        scrollableParents.push(parent);
      }
    }
  }
  return scrollableParents;
}
function getWidth(element) {
  if (element) {
    let width = element.offsetWidth;
    const style2 = getComputedStyle(element);
    width -= parseFloat(style2.paddingLeft) + parseFloat(style2.paddingRight) + parseFloat(style2.borderLeftWidth) + parseFloat(style2.borderRightWidth);
    return width;
  }
  return 0;
}
function isAndroid() {
  return /(android)/i.test(navigator.userAgent);
}
function isClient() {
  return !!(typeof window !== "undefined" && window.document && window.document.createElement);
}
function isFocusableElement(element, selector = "") {
  return isElement(element) ? element.matches(`button:not([tabindex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            [href][clientHeight][clientWidth]:not([tabindex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            input:not([tabindex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            select:not([tabindex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            textarea:not([tabindex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            [tabIndex]:not([tabIndex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector},
            [contenteditable]:not([tabIndex = "-1"]):not([disabled]):not([style*="display:none"]):not([hidden])${selector}`) : false;
}
function isVisible(element) {
  return !!(element && element.offsetParent != null);
}
function isTouchDevice() {
  return "ontouchstart" in window || navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0;
}
function nestedPosition(element, level) {
  var _a, _b;
  if (element) {
    const parentItem = element.parentElement;
    const elementOffset = getOffset(parentItem);
    const viewport = getViewport();
    const sublistWidth = element.offsetParent ? element.offsetWidth : getHiddenElementOuterWidth(element);
    const sublistHeight = element.offsetParent ? element.offsetHeight : getHiddenElementOuterHeight(element);
    const itemOuterWidth = getOuterWidth((_a = parentItem == null ? void 0 : parentItem.children) == null ? void 0 : _a[0]);
    const itemOuterHeight = getOuterHeight((_b = parentItem == null ? void 0 : parentItem.children) == null ? void 0 : _b[0]);
    let left = "";
    let top = "";
    if (elementOffset.left + itemOuterWidth + sublistWidth > viewport.width - calculateScrollbarWidth()) {
      if (elementOffset.left < sublistWidth) {
        if (level % 2 === 1) {
          left = elementOffset.left ? "-" + elementOffset.left + "px" : "100%";
        } else if (level % 2 === 0) {
          left = viewport.width - sublistWidth - calculateScrollbarWidth() + "px";
        }
      } else {
        left = "-100%";
      }
    } else {
      left = "100%";
    }
    if (element.getBoundingClientRect().top + itemOuterHeight + sublistHeight > viewport.height) {
      top = `-${sublistHeight - itemOuterHeight}px`;
    } else {
      top = "0px";
    }
    element.style.top = top;
    element.style.insetInlineStart = left;
  }
}
function setAttribute(element, attribute = "", value) {
  if (isElement(element) && value !== null && value !== void 0) {
    element.setAttribute(attribute, value);
  }
}
var __defProp$1 = Object.defineProperty;
var __getOwnPropSymbols$1 = Object.getOwnPropertySymbols;
var __hasOwnProp$1 = Object.prototype.hasOwnProperty;
var __propIsEnum$1 = Object.prototype.propertyIsEnumerable;
var __defNormalProp$1 = (obj, key, value) => key in obj ? __defProp$1(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __spreadValues$1 = (a, b) => {
  for (var prop in b || (b = {}))
    if (__hasOwnProp$1.call(b, prop))
      __defNormalProp$1(a, prop, b[prop]);
  if (__getOwnPropSymbols$1)
    for (var prop of __getOwnPropSymbols$1(b)) {
      if (__propIsEnum$1.call(b, prop))
        __defNormalProp$1(a, prop, b[prop]);
    }
  return a;
};
function isEmpty$1(value) {
  return value === null || value === void 0 || value === "" || Array.isArray(value) && value.length === 0 || !(value instanceof Date) && typeof value === "object" && Object.keys(value).length === 0;
}
function _deepEquals(obj1, obj2, visited = /* @__PURE__ */ new WeakSet()) {
  if (obj1 === obj2) return true;
  if (!obj1 || !obj2 || typeof obj1 !== "object" || typeof obj2 !== "object") return false;
  if (visited.has(obj1) || visited.has(obj2)) return false;
  visited.add(obj1).add(obj2);
  const arrObj1 = Array.isArray(obj1);
  const arrObj2 = Array.isArray(obj2);
  let i, length, key;
  if (arrObj1 && arrObj2) {
    length = obj1.length;
    if (length != obj2.length) return false;
    for (i = length; i-- !== 0; ) if (!_deepEquals(obj1[i], obj2[i], visited)) return false;
    return true;
  }
  if (arrObj1 != arrObj2) return false;
  const dateObj1 = obj1 instanceof Date, dateObj2 = obj2 instanceof Date;
  if (dateObj1 != dateObj2) return false;
  if (dateObj1 && dateObj2) return obj1.getTime() == obj2.getTime();
  const regexpObj1 = obj1 instanceof RegExp, regexpObj2 = obj2 instanceof RegExp;
  if (regexpObj1 != regexpObj2) return false;
  if (regexpObj1 && regexpObj2) return obj1.toString() == obj2.toString();
  const keys = Object.keys(obj1);
  length = keys.length;
  if (length !== Object.keys(obj2).length) return false;
  for (i = length; i-- !== 0; ) if (!Object.prototype.hasOwnProperty.call(obj2, keys[i])) return false;
  for (i = length; i-- !== 0; ) {
    key = keys[i];
    if (!_deepEquals(obj1[key], obj2[key], visited)) return false;
  }
  return true;
}
function deepEquals(obj1, obj2) {
  return _deepEquals(obj1, obj2);
}
function isFunction(value) {
  return typeof value === "function" && "call" in value && "apply" in value;
}
function isNotEmpty$1(value) {
  return !isEmpty$1(value);
}
function resolveFieldData(data, field) {
  if (!data || !field) {
    return null;
  }
  try {
    const value = data[field];
    if (isNotEmpty$1(value)) return value;
  } catch (e) {
  }
  if (Object.keys(data).length) {
    if (isFunction(field)) {
      return field(data);
    } else if (field.indexOf(".") === -1) {
      return data[field];
    } else {
      const fields = field.split(".");
      let value = data;
      for (let i = 0, len = fields.length; i < len; ++i) {
        if (value == null) {
          return null;
        }
        value = value[fields[i]];
      }
      return value;
    }
  }
  return null;
}
function equals(obj1, obj2, field) {
  if (field) return resolveFieldData(obj1, field) === resolveFieldData(obj2, field);
  else return deepEquals(obj1, obj2);
}
function contains(value, list) {
  if (value != null && list && list.length) {
    for (const val of list) {
      if (equals(value, val)) return true;
    }
  }
  return false;
}
function isObject$1(value, empty = true) {
  return value instanceof Object && value.constructor === Object && (empty || Object.keys(value).length !== 0);
}
function _deepMerge(target = {}, source = {}) {
  const mergedObj = __spreadValues$1({}, target);
  Object.keys(source).forEach((key) => {
    const typedKey = key;
    if (isObject$1(source[typedKey]) && typedKey in target && isObject$1(target[typedKey])) {
      mergedObj[typedKey] = _deepMerge(target[typedKey], source[typedKey]);
    } else {
      mergedObj[typedKey] = source[typedKey];
    }
  });
  return mergedObj;
}
function deepMerge(...args) {
  return args.reduce((acc, obj, i) => i === 0 ? obj : _deepMerge(acc, obj), {});
}
function findLastIndex(arr, callback) {
  let index = -1;
  if (isNotEmpty$1(arr)) {
    try {
      index = arr.findLastIndex(callback);
    } catch (e) {
      index = arr.lastIndexOf([...arr].reverse().find(callback));
    }
  }
  return index;
}
function resolve(obj, ...params) {
  return isFunction(obj) ? obj(...params) : obj;
}
function isString(value, empty = true) {
  return typeof value === "string" && (empty || value !== "");
}
function toFlatCase(str) {
  return isString(str) ? str.replace(/(-|_)/g, "").toLowerCase() : str;
}
function getKeyValue(obj, key = "", params = {}) {
  const fKeys = toFlatCase(key).split(".");
  const fKey = fKeys.shift();
  if (fKey) {
    if (isObject$1(obj)) {
      const matchedKey = Object.keys(obj).find((k) => toFlatCase(k) === fKey) || "";
      return getKeyValue(resolve(obj[matchedKey], params), fKeys.join("."), params);
    }
    return void 0;
  }
  return resolve(obj, params);
}
function isArray(value, empty = true) {
  return Array.isArray(value) && (empty || value.length !== 0);
}
function isNumber(value) {
  return isNotEmpty$1(value) && !isNaN(value);
}
function isPrintableCharacter(char = "") {
  return isNotEmpty$1(char) && char.length === 1 && !!char.match(/\S| /);
}
function matchRegex(str, regex) {
  if (regex) {
    const match = regex.test(str);
    regex.lastIndex = 0;
    return match;
  }
  return false;
}
function mergeKeys(...args) {
  return deepMerge(...args);
}
function minifyCSS(css2) {
  return css2 ? css2.replace(/\/\*(?:(?!\*\/)[\s\S])*\*\/|[\r\n\t]+/g, "").replace(/ {2,}/g, " ").replace(/ ([{:}]) /g, "$1").replace(/([;,]) /g, "$1").replace(/ !/g, "!").replace(/: /g, ":") : css2;
}
function removeAccents(str) {
  const accentCheckRegex = /[\xC0-\xFF\u0100-\u017E]/;
  if (str && accentCheckRegex.test(str)) {
    const accentsMap = {
      A: /[\xC0-\xC5\u0100\u0102\u0104]/g,
      AE: /[\xC6]/g,
      C: /[\xC7\u0106\u0108\u010A\u010C]/g,
      D: /[\xD0\u010E\u0110]/g,
      E: /[\xC8-\xCB\u0112\u0114\u0116\u0118\u011A]/g,
      G: /[\u011C\u011E\u0120\u0122]/g,
      H: /[\u0124\u0126]/g,
      I: /[\xCC-\xCF\u0128\u012A\u012C\u012E\u0130]/g,
      IJ: /[\u0132]/g,
      J: /[\u0134]/g,
      K: /[\u0136]/g,
      L: /[\u0139\u013B\u013D\u013F\u0141]/g,
      N: /[\xD1\u0143\u0145\u0147\u014A]/g,
      O: /[\xD2-\xD6\xD8\u014C\u014E\u0150]/g,
      OE: /[\u0152]/g,
      R: /[\u0154\u0156\u0158]/g,
      S: /[\u015A\u015C\u015E\u0160]/g,
      T: /[\u0162\u0164\u0166]/g,
      U: /[\xD9-\xDC\u0168\u016A\u016C\u016E\u0170\u0172]/g,
      W: /[\u0174]/g,
      Y: /[\xDD\u0176\u0178]/g,
      Z: /[\u0179\u017B\u017D]/g,
      a: /[\xE0-\xE5\u0101\u0103\u0105]/g,
      ae: /[\xE6]/g,
      c: /[\xE7\u0107\u0109\u010B\u010D]/g,
      d: /[\u010F\u0111]/g,
      e: /[\xE8-\xEB\u0113\u0115\u0117\u0119\u011B]/g,
      g: /[\u011D\u011F\u0121\u0123]/g,
      i: /[\xEC-\xEF\u0129\u012B\u012D\u012F\u0131]/g,
      ij: /[\u0133]/g,
      j: /[\u0135]/g,
      k: /[\u0137,\u0138]/g,
      l: /[\u013A\u013C\u013E\u0140\u0142]/g,
      n: /[\xF1\u0144\u0146\u0148\u014B]/g,
      p: /[\xFE]/g,
      o: /[\xF2-\xF6\xF8\u014D\u014F\u0151]/g,
      oe: /[\u0153]/g,
      r: /[\u0155\u0157\u0159]/g,
      s: /[\u015B\u015D\u015F\u0161]/g,
      t: /[\u0163\u0165\u0167]/g,
      u: /[\xF9-\xFC\u0169\u016B\u016D\u016F\u0171\u0173]/g,
      w: /[\u0175]/g,
      y: /[\xFD\xFF\u0177]/g,
      z: /[\u017A\u017C\u017E]/g
    };
    for (const key in accentsMap) {
      str = str.replace(accentsMap[key], key);
    }
  }
  return str;
}
function toCapitalCase(str) {
  return isString(str, false) ? str[0].toUpperCase() + str.slice(1) : str;
}
function toKebabCase(str) {
  return isString(str) ? str.replace(/(_)/g, "-").replace(/[A-Z]/g, (c, i) => i === 0 ? c : "-" + c.toLowerCase()).toLowerCase() : str;
}
function toTokenKey(str) {
  return isString(str) ? str.replace(/[A-Z]/g, (c, i) => i === 0 ? c : "." + c.toLowerCase()).toLowerCase() : str;
}
var lastIds = {};
function uuid(prefix = "pui_id_") {
  if (!Object.hasOwn(lastIds, prefix)) {
    lastIds[prefix] = 0;
  }
  lastIds[prefix]++;
  return `${prefix}${lastIds[prefix]}`;
}
function handler() {
  let zIndexes = [];
  const generateZIndex = (key, autoZIndex, baseZIndex = 999) => {
    const lastZIndex = getLastZIndex(key, autoZIndex, baseZIndex);
    const newZIndex = lastZIndex.value + (lastZIndex.key === key ? 0 : baseZIndex) + 1;
    zIndexes.push({ key, value: newZIndex });
    return newZIndex;
  };
  const revertZIndex = (zIndex) => {
    zIndexes = zIndexes.filter((obj) => obj.value !== zIndex);
  };
  const getCurrentZIndex = (key, autoZIndex) => {
    return getLastZIndex(key).value;
  };
  const getLastZIndex = (key, autoZIndex, baseZIndex = 0) => {
    return [...zIndexes].reverse().find((obj) => true) || { key, value: baseZIndex };
  };
  const getZIndex = (element) => {
    return element ? parseInt(element.style.zIndex, 10) || 0 : 0;
  };
  return {
    get: getZIndex,
    set: (key, element, baseZIndex) => {
      if (element) {
        element.style.zIndex = String(generateZIndex(key, true, baseZIndex));
      }
    },
    clear: (element) => {
      if (element) {
        revertZIndex(getZIndex(element));
        element.style.zIndex = "";
      }
    },
    getCurrent: (key) => getCurrentZIndex(key)
  };
}
var ZIndex = handler();
function cn(...args) {
  if (args) {
    let classes = [];
    for (let i = 0; i < args.length; i++) {
      const className = args[i];
      if (!className) {
        continue;
      }
      const type = typeof className;
      if (type === "string" || type === "number") {
        classes.push(className);
      } else if (type === "object") {
        const _classes = Array.isArray(className) ? [cn(...className)] : Object.entries(className).map(([key, value]) => value ? key : void 0);
        classes = _classes.length ? classes.concat(_classes.filter((c) => !!c)) : classes;
      }
    }
    return classes.join(" ").trim();
  }
  return void 0;
}
function EventBus() {
  const allHandlers = /* @__PURE__ */ new Map();
  return {
    on(type, handler2) {
      let handlers = allHandlers.get(type);
      if (!handlers) handlers = [handler2];
      else handlers.push(handler2);
      allHandlers.set(type, handlers);
      return this;
    },
    off(type, handler2) {
      const handlers = allHandlers.get(type);
      if (handlers) {
        handlers.splice(handlers.indexOf(handler2) >>> 0, 1);
      }
      return this;
    },
    emit(type, evt) {
      const handlers = allHandlers.get(type);
      if (handlers) {
        handlers.forEach((handler2) => {
          handler2(evt);
        });
      }
    },
    clear() {
      allHandlers.clear();
    }
  };
}
var __defProp = Object.defineProperty;
var __defProps = Object.defineProperties;
var __getOwnPropDescs = Object.getOwnPropertyDescriptors;
var __getOwnPropSymbols = Object.getOwnPropertySymbols;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __propIsEnum = Object.prototype.propertyIsEnumerable;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __spreadValues = (a, b) => {
  for (var prop in b || (b = {}))
    if (__hasOwnProp.call(b, prop))
      __defNormalProp(a, prop, b[prop]);
  if (__getOwnPropSymbols)
    for (var prop of __getOwnPropSymbols(b)) {
      if (__propIsEnum.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    }
  return a;
};
var __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));
var __objRest = (source, exclude) => {
  var target = {};
  for (var prop in source)
    if (__hasOwnProp.call(source, prop) && exclude.indexOf(prop) < 0)
      target[prop] = source[prop];
  if (source != null && __getOwnPropSymbols)
    for (var prop of __getOwnPropSymbols(source)) {
      if (exclude.indexOf(prop) < 0 && __propIsEnum.call(source, prop))
        target[prop] = source[prop];
    }
  return target;
};
var ThemeService = EventBus();
var service_default = ThemeService;
var EXPR_REGEX = /{([^}]*)}/g;
var CALC_REGEX = /(\d+\s+[\+\-\*\/]\s+\d+)/g;
var VAR_REGEX = /var\([^)]+\)/g;
function toValue(value) {
  return isObject$1(value) && value.hasOwnProperty("$value") && value.hasOwnProperty("$type") ? value.$value : value;
}
function toNormalizePrefix(prefix) {
  return prefix.replaceAll(/ /g, "").replace(/[^\w]/g, "-");
}
function toNormalizeVariable(prefix = "", variable = "") {
  return toNormalizePrefix(`${isString(prefix, false) && isString(variable, false) ? `${prefix}-` : prefix}${variable}`);
}
function getVariableName(prefix = "", variable = "") {
  return `--${toNormalizeVariable(prefix, variable)}`;
}
function hasOddBraces(str = "") {
  const openBraces = (str.match(/{/g) || []).length;
  const closeBraces = (str.match(/}/g) || []).length;
  return (openBraces + closeBraces) % 2 !== 0;
}
function getVariableValue(value, variable = "", prefix = "", excludedKeyRegexes = [], fallback) {
  if (isString(value)) {
    const val = value.trim();
    if (hasOddBraces(val)) {
      return void 0;
    } else if (matchRegex(val, EXPR_REGEX)) {
      const _val = val.replaceAll(EXPR_REGEX, (v) => {
        const path = v.replace(/{|}/g, "");
        const keys = path.split(".").filter((_v) => !excludedKeyRegexes.some((_r) => matchRegex(_v, _r)));
        return `var(${getVariableName(prefix, toKebabCase(keys.join("-")))}${isNotEmpty$1(fallback) ? `, ${fallback}` : ""})`;
      });
      return matchRegex(_val.replace(VAR_REGEX, "0"), CALC_REGEX) ? `calc(${_val})` : _val;
    }
    return val;
  } else if (isNumber(value)) {
    return value;
  }
  return void 0;
}
function setProperty(properties, key, value) {
  if (isString(key, false)) {
    properties.push(`${key}:${value};`);
  }
}
function getRule(selector, properties) {
  if (selector) {
    return `${selector}{${properties}}`;
  }
  return "";
}
function evaluateDtExpressions(input, fn) {
  if (input.indexOf("dt(") === -1) return input;
  function fastParseArgs(str, fn2) {
    const args = [];
    let i = 0;
    let current = "";
    let quote = null;
    let depth = 0;
    while (i <= str.length) {
      const c = str[i];
      if ((c === '"' || c === "'" || c === "`") && str[i - 1] !== "\\") {
        quote = quote === c ? null : c;
      }
      if (!quote) {
        if (c === "(") depth++;
        if (c === ")") depth--;
        if ((c === "," || i === str.length) && depth === 0) {
          const arg = current.trim();
          if (arg.startsWith("dt(")) {
            args.push(evaluateDtExpressions(arg, fn2));
          } else {
            args.push(parseArg(arg));
          }
          current = "";
          i++;
          continue;
        }
      }
      if (c !== void 0) current += c;
      i++;
    }
    return args;
  }
  function parseArg(arg) {
    const q = arg[0];
    if ((q === '"' || q === "'" || q === "`") && arg[arg.length - 1] === q) {
      return arg.slice(1, -1);
    }
    const num = Number(arg);
    return isNaN(num) ? arg : num;
  }
  const indices = [];
  const stack = [];
  for (let i = 0; i < input.length; i++) {
    if (input[i] === "d" && input.slice(i, i + 3) === "dt(") {
      stack.push(i);
      i += 2;
    } else if (input[i] === ")" && stack.length > 0) {
      const start = stack.pop();
      if (stack.length === 0) {
        indices.push([start, i]);
      }
    }
  }
  if (!indices.length) return input;
  for (let i = indices.length - 1; i >= 0; i--) {
    const [start, end] = indices[i];
    const inner = input.slice(start + 3, end);
    const args = fastParseArgs(inner, fn);
    const resolved = fn(...args);
    input = input.slice(0, start) + resolved + input.slice(end + 1);
  }
  return input;
}
var $dt = (tokenPath) => {
  var _a;
  const theme = config_default.getTheme();
  const variable = dtwt(theme, tokenPath, void 0, "variable");
  const name = (_a = variable == null ? void 0 : variable.match(/--[\w-]+/g)) == null ? void 0 : _a[0];
  const value = dtwt(theme, tokenPath, void 0, "value");
  return {
    name,
    variable,
    value
  };
};
var dt = (...args) => {
  return dtwt(config_default.getTheme(), ...args);
};
var dtwt = (theme = {}, tokenPath, fallback, type) => {
  if (tokenPath) {
    const { variable: VARIABLE, options: OPTIONS } = config_default.defaults || {};
    const { prefix, transform } = (theme == null ? void 0 : theme.options) || OPTIONS || {};
    const token = matchRegex(tokenPath, EXPR_REGEX) ? tokenPath : `{${tokenPath}}`;
    const isStrictTransform = type === "value" || isEmpty$1(type) && transform === "strict";
    return isStrictTransform ? config_default.getTokenValue(tokenPath) : getVariableValue(token, void 0, prefix, [VARIABLE.excludedKeyRegex], fallback);
  }
  return "";
};
function css(strings, ...exprs) {
  if (strings instanceof Array) {
    const raw = strings.reduce((acc, str, i) => {
      var _a;
      return acc + str + ((_a = resolve(exprs[i], { dt })) != null ? _a : "");
    }, "");
    return evaluateDtExpressions(raw, dt);
  }
  return resolve(strings, { dt });
}
function toVariables_default(theme, options = {}) {
  const VARIABLE = config_default.defaults.variable;
  const { prefix = VARIABLE.prefix, selector = VARIABLE.selector, excludedKeyRegex = VARIABLE.excludedKeyRegex } = options;
  const tokens = [];
  const variables = [];
  const stack = [{ node: theme, path: prefix }];
  while (stack.length) {
    const { node, path } = stack.pop();
    for (const key in node) {
      const raw = node[key];
      const val = toValue(raw);
      const skipNormalize = matchRegex(key, excludedKeyRegex);
      const variablePath = skipNormalize ? toNormalizeVariable(path) : toNormalizeVariable(path, toKebabCase(key));
      if (isObject$1(val)) {
        stack.push({ node: val, path: variablePath });
      } else {
        const varName = getVariableName(variablePath);
        const varValue = getVariableValue(val, variablePath, prefix, [excludedKeyRegex]);
        setProperty(variables, varName, varValue);
        let token = variablePath;
        if (prefix && token.startsWith(prefix + "-")) {
          token = token.slice(prefix.length + 1);
        }
        tokens.push(token.replace(/-/g, "."));
      }
    }
  }
  const declarations = variables.join("");
  return {
    value: variables,
    tokens,
    declarations,
    css: getRule(selector, declarations)
  };
}
var themeUtils_default = {
  regex: {
    rules: {
      class: {
        pattern: /^\.([a-zA-Z][\w-]*)$/,
        resolve(value) {
          return { type: "class", selector: value, matched: this.pattern.test(value.trim()) };
        }
      },
      attr: {
        pattern: /^\[(.*)\]$/,
        resolve(value) {
          return { type: "attr", selector: `:root${value}`, matched: this.pattern.test(value.trim()) };
        }
      },
      media: {
        pattern: /^@media (.*)$/,
        resolve(value) {
          return { type: "media", selector: `${value}{:root{[CSS]}}`, matched: this.pattern.test(value.trim()) };
        }
      },
      system: {
        pattern: /^system$/,
        resolve(value) {
          return { type: "system", selector: "@media (prefers-color-scheme: dark){:root{[CSS]}}", matched: this.pattern.test(value.trim()) };
        }
      },
      custom: {
        resolve(value) {
          return { type: "custom", selector: value, matched: true };
        }
      }
    },
    resolve(value) {
      const rules = Object.keys(this.rules).filter((k) => k !== "custom").map((r) => this.rules[r]);
      return [value].flat().map((v) => {
        var _a;
        return (_a = rules.map((r) => r.resolve(v)).find((rr) => rr.matched)) != null ? _a : this.rules.custom.resolve(v);
      });
    }
  },
  _toVariables(theme, options) {
    return toVariables_default(theme, { prefix: options == null ? void 0 : options.prefix });
  },
  getCommon({ name = "", theme = {}, params, set, defaults }) {
    var _e, _f, _g, _h, _i, _j, _k;
    const { preset, options } = theme;
    let primitive_css, primitive_tokens, semantic_css, semantic_tokens, global_css, global_tokens, style2;
    if (isNotEmpty$1(preset) && options.transform !== "strict") {
      const { primitive, semantic, extend } = preset;
      const _a = semantic || {}, { colorScheme } = _a, sRest = __objRest(_a, ["colorScheme"]);
      const _b = extend || {}, { colorScheme: eColorScheme } = _b, eRest = __objRest(_b, ["colorScheme"]);
      const _c = colorScheme || {}, { dark } = _c, csRest = __objRest(_c, ["dark"]);
      const _d = eColorScheme || {}, { dark: eDark } = _d, ecsRest = __objRest(_d, ["dark"]);
      const prim_var = isNotEmpty$1(primitive) ? this._toVariables({ primitive }, options) : {};
      const sRest_var = isNotEmpty$1(sRest) ? this._toVariables({ semantic: sRest }, options) : {};
      const csRest_var = isNotEmpty$1(csRest) ? this._toVariables({ light: csRest }, options) : {};
      const csDark_var = isNotEmpty$1(dark) ? this._toVariables({ dark }, options) : {};
      const eRest_var = isNotEmpty$1(eRest) ? this._toVariables({ semantic: eRest }, options) : {};
      const ecsRest_var = isNotEmpty$1(ecsRest) ? this._toVariables({ light: ecsRest }, options) : {};
      const ecsDark_var = isNotEmpty$1(eDark) ? this._toVariables({ dark: eDark }, options) : {};
      const [prim_css, prim_tokens] = [(_e = prim_var.declarations) != null ? _e : "", prim_var.tokens];
      const [sRest_css, sRest_tokens] = [(_f = sRest_var.declarations) != null ? _f : "", sRest_var.tokens || []];
      const [csRest_css, csRest_tokens] = [(_g = csRest_var.declarations) != null ? _g : "", csRest_var.tokens || []];
      const [csDark_css, csDark_tokens] = [(_h = csDark_var.declarations) != null ? _h : "", csDark_var.tokens || []];
      const [eRest_css, eRest_tokens] = [(_i = eRest_var.declarations) != null ? _i : "", eRest_var.tokens || []];
      const [ecsRest_css, ecsRest_tokens] = [(_j = ecsRest_var.declarations) != null ? _j : "", ecsRest_var.tokens || []];
      const [ecsDark_css, ecsDark_tokens] = [(_k = ecsDark_var.declarations) != null ? _k : "", ecsDark_var.tokens || []];
      primitive_css = this.transformCSS(name, prim_css, "light", "variable", options, set, defaults);
      primitive_tokens = prim_tokens;
      const semantic_light_css = this.transformCSS(name, `${sRest_css}${csRest_css}`, "light", "variable", options, set, defaults);
      const semantic_dark_css = this.transformCSS(name, `${csDark_css}`, "dark", "variable", options, set, defaults);
      semantic_css = `${semantic_light_css}${semantic_dark_css}`;
      semantic_tokens = [.../* @__PURE__ */ new Set([...sRest_tokens, ...csRest_tokens, ...csDark_tokens])];
      const global_light_css = this.transformCSS(name, `${eRest_css}${ecsRest_css}color-scheme:light`, "light", "variable", options, set, defaults);
      const global_dark_css = this.transformCSS(name, `${ecsDark_css}color-scheme:dark`, "dark", "variable", options, set, defaults);
      global_css = `${global_light_css}${global_dark_css}`;
      global_tokens = [.../* @__PURE__ */ new Set([...eRest_tokens, ...ecsRest_tokens, ...ecsDark_tokens])];
      style2 = resolve(preset.css, { dt });
    }
    return {
      primitive: {
        css: primitive_css,
        tokens: primitive_tokens
      },
      semantic: {
        css: semantic_css,
        tokens: semantic_tokens
      },
      global: {
        css: global_css,
        tokens: global_tokens
      },
      style: style2
    };
  },
  getPreset({ name = "", preset = {}, options, params, set, defaults, selector }) {
    var _e, _f, _g;
    let p_css, p_tokens, p_style;
    if (isNotEmpty$1(preset) && options.transform !== "strict") {
      const _name = name.replace("-directive", "");
      const _a = preset, { colorScheme, extend, css: css2 } = _a, vRest = __objRest(_a, ["colorScheme", "extend", "css"]);
      const _b = extend || {}, { colorScheme: eColorScheme } = _b, evRest = __objRest(_b, ["colorScheme"]);
      const _c = colorScheme || {}, { dark } = _c, csRest = __objRest(_c, ["dark"]);
      const _d = eColorScheme || {}, { dark: ecsDark } = _d, ecsRest = __objRest(_d, ["dark"]);
      const vRest_var = isNotEmpty$1(vRest) ? this._toVariables({ [_name]: __spreadValues(__spreadValues({}, vRest), evRest) }, options) : {};
      const csRest_var = isNotEmpty$1(csRest) ? this._toVariables({ [_name]: __spreadValues(__spreadValues({}, csRest), ecsRest) }, options) : {};
      const csDark_var = isNotEmpty$1(dark) ? this._toVariables({ [_name]: __spreadValues(__spreadValues({}, dark), ecsDark) }, options) : {};
      const [vRest_css, vRest_tokens] = [(_e = vRest_var.declarations) != null ? _e : "", vRest_var.tokens || []];
      const [csRest_css, csRest_tokens] = [(_f = csRest_var.declarations) != null ? _f : "", csRest_var.tokens || []];
      const [csDark_css, csDark_tokens] = [(_g = csDark_var.declarations) != null ? _g : "", csDark_var.tokens || []];
      const light_variable_css = this.transformCSS(_name, `${vRest_css}${csRest_css}`, "light", "variable", options, set, defaults, selector);
      const dark_variable_css = this.transformCSS(_name, csDark_css, "dark", "variable", options, set, defaults, selector);
      p_css = `${light_variable_css}${dark_variable_css}`;
      p_tokens = [.../* @__PURE__ */ new Set([...vRest_tokens, ...csRest_tokens, ...csDark_tokens])];
      p_style = resolve(css2, { dt });
    }
    return {
      css: p_css,
      tokens: p_tokens,
      style: p_style
    };
  },
  getPresetC({ name = "", theme = {}, params, set, defaults }) {
    var _a;
    const { preset, options } = theme;
    const cPreset = (_a = preset == null ? void 0 : preset.components) == null ? void 0 : _a[name];
    return this.getPreset({ name, preset: cPreset, options, params, set, defaults });
  },
  // @deprecated - use getPresetC instead
  getPresetD({ name = "", theme = {}, params, set, defaults }) {
    var _a, _b;
    const dName = name.replace("-directive", "");
    const { preset, options } = theme;
    const dPreset = ((_a = preset == null ? void 0 : preset.components) == null ? void 0 : _a[dName]) || ((_b = preset == null ? void 0 : preset.directives) == null ? void 0 : _b[dName]);
    return this.getPreset({ name: dName, preset: dPreset, options, params, set, defaults });
  },
  applyDarkColorScheme(options) {
    return !(options.darkModeSelector === "none" || options.darkModeSelector === false);
  },
  getColorSchemeOption(options, defaults) {
    var _a;
    return this.applyDarkColorScheme(options) ? this.regex.resolve(options.darkModeSelector === true ? defaults.options.darkModeSelector : (_a = options.darkModeSelector) != null ? _a : defaults.options.darkModeSelector) : [];
  },
  getLayerOrder(name, options = {}, params, defaults) {
    const { cssLayer } = options;
    if (cssLayer) {
      const order = resolve(cssLayer.order || "primeui", params);
      return `@layer ${order}`;
    }
    return "";
  },
  getCommonStyleSheet({ name = "", theme = {}, params, props = {}, set, defaults }) {
    const common = this.getCommon({ name, theme, params, set, defaults });
    const _props = Object.entries(props).reduce((acc, [k, v]) => acc.push(`${k}="${v}"`) && acc, []).join(" ");
    return Object.entries(common || {}).reduce((acc, [key, value]) => {
      if (isObject$1(value) && Object.hasOwn(value, "css")) {
        const _css = minifyCSS(value.css);
        const id = `${key}-variables`;
        acc.push(`<style type="text/css" data-primevue-style-id="${id}" ${_props}>${_css}</style>`);
      }
      return acc;
    }, []).join("");
  },
  getStyleSheet({ name = "", theme = {}, params, props = {}, set, defaults }) {
    var _a;
    const options = { name, theme, params, set, defaults };
    const preset_css = (_a = name.includes("-directive") ? this.getPresetD(options) : this.getPresetC(options)) == null ? void 0 : _a.css;
    const _props = Object.entries(props).reduce((acc, [k, v]) => acc.push(`${k}="${v}"`) && acc, []).join(" ");
    return preset_css ? `<style type="text/css" data-primevue-style-id="${name}-variables" ${_props}>${minifyCSS(preset_css)}</style>` : "";
  },
  createTokens(obj = {}, defaults, parentKey = "", parentPath = "", tokens = {}) {
    Object.entries(obj).forEach(([key, value]) => {
      const currentKey = matchRegex(key, defaults.variable.excludedKeyRegex) ? parentKey : parentKey ? `${parentKey}.${toTokenKey(key)}` : toTokenKey(key);
      const currentPath = parentPath ? `${parentPath}.${key}` : key;
      if (isObject$1(value)) {
        this.createTokens(value, defaults, currentKey, currentPath, tokens);
      } else {
        tokens[currentKey] || (tokens[currentKey] = {
          paths: [],
          computed(colorScheme, tokenPathMap = {}) {
            var _a, _b;
            if (this.paths.length === 1) {
              return (_a = this.paths[0]) == null ? void 0 : _a.computed(this.paths[0].scheme, tokenPathMap["binding"]);
            } else if (colorScheme && colorScheme !== "none") {
              return (_b = this.paths.find((p) => p.scheme === colorScheme)) == null ? void 0 : _b.computed(colorScheme, tokenPathMap["binding"]);
            }
            return this.paths.map((p) => p.computed(p.scheme, tokenPathMap[p.scheme]));
          }
        });
        tokens[currentKey].paths.push({
          path: currentPath,
          value,
          scheme: currentPath.includes("colorScheme.light") ? "light" : currentPath.includes("colorScheme.dark") ? "dark" : "none",
          computed(colorScheme, tokenPathMap = {}) {
            let computedValue = value;
            tokenPathMap["name"] = this.path;
            tokenPathMap["binding"] || (tokenPathMap["binding"] = {});
            if (matchRegex(value, EXPR_REGEX)) {
              const val = value.trim();
              const _val = val.replaceAll(EXPR_REGEX, (v) => {
                var _a;
                const path = v.replace(/{|}/g, "");
                const computed = (_a = tokens[path]) == null ? void 0 : _a.computed(colorScheme, tokenPathMap);
                return isArray(computed) && computed.length === 2 ? `light-dark(${computed[0].value},${computed[1].value})` : computed == null ? void 0 : computed.value;
              });
              computedValue = matchRegex(_val.replace(VAR_REGEX, "0"), CALC_REGEX) ? `calc(${_val})` : _val;
            }
            isEmpty$1(tokenPathMap["binding"]) && delete tokenPathMap["binding"];
            return {
              colorScheme,
              path: this.path,
              paths: tokenPathMap,
              value: computedValue.includes("undefined") ? void 0 : computedValue
            };
          }
        });
      }
    });
    return tokens;
  },
  getTokenValue(tokens, path, defaults) {
    var _a;
    const normalizePath = (str) => {
      const strArr = str.split(".");
      return strArr.filter((s) => !matchRegex(s.toLowerCase(), defaults.variable.excludedKeyRegex)).join(".");
    };
    const token = normalizePath(path);
    const colorScheme = path.includes("colorScheme.light") ? "light" : path.includes("colorScheme.dark") ? "dark" : void 0;
    const computedValues = [(_a = tokens[token]) == null ? void 0 : _a.computed(colorScheme)].flat().filter((computed) => computed);
    return computedValues.length === 1 ? computedValues[0].value : computedValues.reduce((acc = {}, computed) => {
      const _a2 = computed, { colorScheme: cs } = _a2, rest = __objRest(_a2, ["colorScheme"]);
      acc[cs] = rest;
      return acc;
    }, void 0);
  },
  getSelectorRule(selector1, selector2, type, css2) {
    return type === "class" || type === "attr" ? getRule(isNotEmpty$1(selector2) ? `${selector1}${selector2},${selector1} ${selector2}` : selector1, css2) : getRule(selector1, isNotEmpty$1(selector2) ? getRule(selector2, css2) : css2);
  },
  transformCSS(name, css2, mode, type, options = {}, set, defaults, selector) {
    if (isNotEmpty$1(css2)) {
      const { cssLayer } = options;
      if (type !== "style") {
        const colorSchemeOption = this.getColorSchemeOption(options, defaults);
        css2 = mode === "dark" ? colorSchemeOption.reduce((acc, { type: type2, selector: _selector }) => {
          if (isNotEmpty$1(_selector)) {
            acc += _selector.includes("[CSS]") ? _selector.replace("[CSS]", css2) : this.getSelectorRule(_selector, selector, type2, css2);
          }
          return acc;
        }, "") : getRule(selector != null ? selector : ":root", css2);
      }
      if (cssLayer) {
        const layerOptions = {
          name: "primeui",
          order: "primeui"
        };
        isObject$1(cssLayer) && (layerOptions.name = resolve(cssLayer.name, { name, type }));
        if (isNotEmpty$1(layerOptions.name)) {
          css2 = getRule(`@layer ${layerOptions.name}`, css2);
          set == null ? void 0 : set.layerNames(layerOptions.name);
        }
      }
      return css2;
    }
    return "";
  }
};
var config_default = {
  defaults: {
    variable: {
      prefix: "p",
      selector: ":root",
      excludedKeyRegex: /^(primitive|semantic|components|directives|variables|colorscheme|light|dark|common|root|states|extend|css)$/gi
    },
    options: {
      prefix: "p",
      darkModeSelector: "system",
      cssLayer: false
    }
  },
  _theme: void 0,
  _layerNames: /* @__PURE__ */ new Set(),
  _loadedStyleNames: /* @__PURE__ */ new Set(),
  _loadingStyles: /* @__PURE__ */ new Set(),
  _tokens: {},
  update(newValues = {}) {
    const { theme } = newValues;
    if (theme) {
      this._theme = __spreadProps(__spreadValues({}, theme), {
        options: __spreadValues(__spreadValues({}, this.defaults.options), theme.options)
      });
      this._tokens = themeUtils_default.createTokens(this.preset, this.defaults);
      this.clearLoadedStyleNames();
    }
  },
  get theme() {
    return this._theme;
  },
  get preset() {
    var _a;
    return ((_a = this.theme) == null ? void 0 : _a.preset) || {};
  },
  get options() {
    var _a;
    return ((_a = this.theme) == null ? void 0 : _a.options) || {};
  },
  get tokens() {
    return this._tokens;
  },
  getTheme() {
    return this.theme;
  },
  setTheme(newValue) {
    this.update({ theme: newValue });
    service_default.emit("theme:change", newValue);
  },
  getPreset() {
    return this.preset;
  },
  setPreset(newValue) {
    this._theme = __spreadProps(__spreadValues({}, this.theme), { preset: newValue });
    this._tokens = themeUtils_default.createTokens(newValue, this.defaults);
    this.clearLoadedStyleNames();
    service_default.emit("preset:change", newValue);
    service_default.emit("theme:change", this.theme);
  },
  getOptions() {
    return this.options;
  },
  setOptions(newValue) {
    this._theme = __spreadProps(__spreadValues({}, this.theme), { options: newValue });
    this.clearLoadedStyleNames();
    service_default.emit("options:change", newValue);
    service_default.emit("theme:change", this.theme);
  },
  getLayerNames() {
    return [...this._layerNames];
  },
  setLayerNames(layerName) {
    this._layerNames.add(layerName);
  },
  getLoadedStyleNames() {
    return this._loadedStyleNames;
  },
  isStyleNameLoaded(name) {
    return this._loadedStyleNames.has(name);
  },
  setLoadedStyleName(name) {
    this._loadedStyleNames.add(name);
  },
  deleteLoadedStyleName(name) {
    this._loadedStyleNames.delete(name);
  },
  clearLoadedStyleNames() {
    this._loadedStyleNames.clear();
  },
  getTokenValue(tokenPath) {
    return themeUtils_default.getTokenValue(this.tokens, tokenPath, this.defaults);
  },
  getCommon(name = "", params) {
    return themeUtils_default.getCommon({ name, theme: this.theme, params, defaults: this.defaults, set: { layerNames: this.setLayerNames.bind(this) } });
  },
  getComponent(name = "", params) {
    const options = { name, theme: this.theme, params, defaults: this.defaults, set: { layerNames: this.setLayerNames.bind(this) } };
    return themeUtils_default.getPresetC(options);
  },
  // @deprecated - use getComponent instead
  getDirective(name = "", params) {
    const options = { name, theme: this.theme, params, defaults: this.defaults, set: { layerNames: this.setLayerNames.bind(this) } };
    return themeUtils_default.getPresetD(options);
  },
  getCustomPreset(name = "", preset, selector, params) {
    const options = { name, preset, options: this.options, selector, params, defaults: this.defaults, set: { layerNames: this.setLayerNames.bind(this) } };
    return themeUtils_default.getPreset(options);
  },
  getLayerOrderCSS(name = "") {
    return themeUtils_default.getLayerOrder(name, this.options, { names: this.getLayerNames() }, this.defaults);
  },
  transformCSS(name = "", css2, type = "style", mode) {
    return themeUtils_default.transformCSS(name, css2, mode, type, this.options, { layerNames: this.setLayerNames.bind(this) }, this.defaults);
  },
  getCommonStyleSheet(name = "", params, props = {}) {
    return themeUtils_default.getCommonStyleSheet({ name, theme: this.theme, params, props, defaults: this.defaults, set: { layerNames: this.setLayerNames.bind(this) } });
  },
  getStyleSheet(name, params, props = {}) {
    return themeUtils_default.getStyleSheet({ name, theme: this.theme, params, props, defaults: this.defaults, set: { layerNames: this.setLayerNames.bind(this) } });
  },
  onStyleMounted(name) {
    this._loadingStyles.add(name);
  },
  onStyleUpdated(name) {
    this._loadingStyles.add(name);
  },
  onStyleLoaded(event, { name }) {
    if (this._loadingStyles.size) {
      this._loadingStyles.delete(name);
      service_default.emit(`theme:${name}:load`, event);
      !this._loadingStyles.size && service_default.emit("theme:load");
    }
  }
};
var style$r = css`
    *,
    ::before,
    ::after {
        box-sizing: border-box;
    }

    /* Non vue overlay animations */
    .p-connected-overlay {
        opacity: 0;
        transform: scaleY(0.8);
        transition:
            transform 0.12s cubic-bezier(0, 0, 0.2, 1),
            opacity 0.12s cubic-bezier(0, 0, 0.2, 1);
    }

    .p-connected-overlay-visible {
        opacity: 1;
        transform: scaleY(1);
    }

    .p-connected-overlay-hidden {
        opacity: 0;
        transform: scaleY(1);
        transition: opacity 0.1s linear;
    }

    /* Vue based overlay animations */
    .p-connected-overlay-enter-from {
        opacity: 0;
        transform: scaleY(0.8);
    }

    .p-connected-overlay-leave-to {
        opacity: 0;
    }

    .p-connected-overlay-enter-active {
        transition:
            transform 0.12s cubic-bezier(0, 0, 0.2, 1),
            opacity 0.12s cubic-bezier(0, 0, 0.2, 1);
    }

    .p-connected-overlay-leave-active {
        transition: opacity 0.1s linear;
    }

    /* Toggleable Content */
    .p-toggleable-content-enter-from,
    .p-toggleable-content-leave-to {
        max-height: 0;
    }

    .p-toggleable-content-enter-to,
    .p-toggleable-content-leave-from {
        max-height: 1000px;
    }

    .p-toggleable-content-leave-active {
        overflow: hidden;
        transition: max-height 0.45s cubic-bezier(0, 1, 0, 1);
    }

    .p-toggleable-content-enter-active {
        overflow: hidden;
        transition: max-height 1s ease-in-out;
    }

    .p-disabled,
    .p-disabled * {
        cursor: default;
        pointer-events: none;
        user-select: none;
    }

    .p-disabled,
    .p-component:disabled {
        opacity: dt('disabled.opacity');
    }

    .pi {
        font-size: dt('icon.size');
    }

    .p-icon {
        width: dt('icon.size');
        height: dt('icon.size');
    }

    .p-overlay-mask {
        background: dt('mask.background');
        color: dt('mask.color');
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }

    .p-overlay-mask-enter {
        animation: p-overlay-mask-enter-animation dt('mask.transition.duration') forwards;
    }

    .p-overlay-mask-leave {
        animation: p-overlay-mask-leave-animation dt('mask.transition.duration') forwards;
    }

    @keyframes p-overlay-mask-enter-animation {
        from {
            background: transparent;
        }
        to {
            background: dt('mask.background');
        }
    }
    @keyframes p-overlay-mask-leave-animation {
        from {
            background: dt('mask.background');
        }
        to {
            background: transparent;
        }
    }
`;
var style$q = css`
    .p-tooltip {
        position: absolute;
        display: none;
        max-width: dt('tooltip.max.width');
    }

    .p-tooltip-right,
    .p-tooltip-left {
        padding: 0 dt('tooltip.gutter');
    }

    .p-tooltip-top,
    .p-tooltip-bottom {
        padding: dt('tooltip.gutter') 0;
    }

    .p-tooltip-text {
        white-space: pre-line;
        word-break: break-word;
        background: dt('tooltip.background');
        color: dt('tooltip.color');
        padding: dt('tooltip.padding');
        box-shadow: dt('tooltip.shadow');
        border-radius: dt('tooltip.border.radius');
    }

    .p-tooltip-arrow {
        position: absolute;
        width: 0;
        height: 0;
        border-color: transparent;
        border-style: solid;
    }

    .p-tooltip-right .p-tooltip-arrow {
        margin-top: calc(-1 * dt('tooltip.gutter'));
        border-width: dt('tooltip.gutter') dt('tooltip.gutter') dt('tooltip.gutter') 0;
        border-right-color: dt('tooltip.background');
    }

    .p-tooltip-left .p-tooltip-arrow {
        margin-top: calc(-1 * dt('tooltip.gutter'));
        border-width: dt('tooltip.gutter') 0 dt('tooltip.gutter') dt('tooltip.gutter');
        border-left-color: dt('tooltip.background');
    }

    .p-tooltip-top .p-tooltip-arrow {
        margin-left: calc(-1 * dt('tooltip.gutter'));
        border-width: dt('tooltip.gutter') dt('tooltip.gutter') 0 dt('tooltip.gutter');
        border-top-color: dt('tooltip.background');
        border-bottom-color: dt('tooltip.background');
    }

    .p-tooltip-bottom .p-tooltip-arrow {
        margin-left: calc(-1 * dt('tooltip.gutter'));
        border-width: 0 dt('tooltip.gutter') dt('tooltip.gutter') dt('tooltip.gutter');
        border-top-color: dt('tooltip.background');
        border-bottom-color: dt('tooltip.background');
    }
`;
var style$p = css`
    .p-badge {
        display: inline-flex;
        border-radius: dt('badge.border.radius');
        align-items: center;
        justify-content: center;
        padding: dt('badge.padding');
        background: dt('badge.primary.background');
        color: dt('badge.primary.color');
        font-size: dt('badge.font.size');
        font-weight: dt('badge.font.weight');
        min-width: dt('badge.min.width');
        height: dt('badge.height');
    }

    .p-badge-dot {
        width: dt('badge.dot.size');
        min-width: dt('badge.dot.size');
        height: dt('badge.dot.size');
        border-radius: 50%;
        padding: 0;
    }

    .p-badge-circle {
        padding: 0;
        border-radius: 50%;
    }

    .p-badge-secondary {
        background: dt('badge.secondary.background');
        color: dt('badge.secondary.color');
    }

    .p-badge-success {
        background: dt('badge.success.background');
        color: dt('badge.success.color');
    }

    .p-badge-info {
        background: dt('badge.info.background');
        color: dt('badge.info.color');
    }

    .p-badge-warn {
        background: dt('badge.warn.background');
        color: dt('badge.warn.color');
    }

    .p-badge-danger {
        background: dt('badge.danger.background');
        color: dt('badge.danger.color');
    }

    .p-badge-contrast {
        background: dt('badge.contrast.background');
        color: dt('badge.contrast.color');
    }

    .p-badge-sm {
        font-size: dt('badge.sm.font.size');
        min-width: dt('badge.sm.min.width');
        height: dt('badge.sm.height');
    }

    .p-badge-lg {
        font-size: dt('badge.lg.font.size');
        min-width: dt('badge.lg.min.width');
        height: dt('badge.lg.height');
    }

    .p-badge-xl {
        font-size: dt('badge.xl.font.size');
        min-width: dt('badge.xl.min.width');
        height: dt('badge.xl.height');
    }
`;
var style$o = css`
    .p-ink {
        display: block;
        position: absolute;
        background: dt('ripple.background');
        border-radius: 100%;
        transform: scale(0);
        pointer-events: none;
    }

    .p-ink-active {
        animation: ripple 0.4s linear;
    }

    @keyframes ripple {
        100% {
            opacity: 0;
            transform: scale(2.5);
        }
    }
`;
var style$n = css`
    .p-button {
        display: inline-flex;
        cursor: pointer;
        user-select: none;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
        color: dt('button.primary.color');
        background: dt('button.primary.background');
        border: 1px solid dt('button.primary.border.color');
        padding: dt('button.padding.y') dt('button.padding.x');
        font-size: 1rem;
        font-family: inherit;
        font-feature-settings: inherit;
        transition:
            background dt('button.transition.duration'),
            color dt('button.transition.duration'),
            border-color dt('button.transition.duration'),
            outline-color dt('button.transition.duration'),
            box-shadow dt('button.transition.duration');
        border-radius: dt('button.border.radius');
        outline-color: transparent;
        gap: dt('button.gap');
    }

    .p-button:disabled {
        cursor: default;
    }

    .p-button-icon-right {
        order: 1;
    }

    .p-button-icon-right:dir(rtl) {
        order: -1;
    }

    .p-button:not(.p-button-vertical) .p-button-icon:not(.p-button-icon-right):dir(rtl) {
        order: 1;
    }

    .p-button-icon-bottom {
        order: 2;
    }

    .p-button-icon-only {
        width: dt('button.icon.only.width');
        padding-inline-start: 0;
        padding-inline-end: 0;
        gap: 0;
    }

    .p-button-icon-only.p-button-rounded {
        border-radius: 50%;
        height: dt('button.icon.only.width');
    }

    .p-button-icon-only .p-button-label {
        visibility: hidden;
        width: 0;
    }

    .p-button-sm {
        font-size: dt('button.sm.font.size');
        padding: dt('button.sm.padding.y') dt('button.sm.padding.x');
    }

    .p-button-sm .p-button-icon {
        font-size: dt('button.sm.font.size');
    }

    .p-button-sm.p-button-icon-only {
        width: dt('button.sm.icon.only.width');
    }

    .p-button-sm.p-button-icon-only.p-button-rounded {
        height: dt('button.sm.icon.only.width');
    }

    .p-button-lg {
        font-size: dt('button.lg.font.size');
        padding: dt('button.lg.padding.y') dt('button.lg.padding.x');
    }

    .p-button-lg .p-button-icon {
        font-size: dt('button.lg.font.size');
    }

    .p-button-lg.p-button-icon-only {
        width: dt('button.lg.icon.only.width');
    }

    .p-button-lg.p-button-icon-only.p-button-rounded {
        height: dt('button.lg.icon.only.width');
    }

    .p-button-vertical {
        flex-direction: column;
    }

    .p-button-label {
        font-weight: dt('button.label.font.weight');
    }

    .p-button-fluid {
        width: 100%;
    }

    .p-button-fluid.p-button-icon-only {
        width: dt('button.icon.only.width');
    }

    .p-button:not(:disabled):hover {
        background: dt('button.primary.hover.background');
        border: 1px solid dt('button.primary.hover.border.color');
        color: dt('button.primary.hover.color');
    }

    .p-button:not(:disabled):active {
        background: dt('button.primary.active.background');
        border: 1px solid dt('button.primary.active.border.color');
        color: dt('button.primary.active.color');
    }

    .p-button:focus-visible {
        box-shadow: dt('button.primary.focus.ring.shadow');
        outline: dt('button.focus.ring.width') dt('button.focus.ring.style') dt('button.primary.focus.ring.color');
        outline-offset: dt('button.focus.ring.offset');
    }

    .p-button .p-badge {
        min-width: dt('button.badge.size');
        height: dt('button.badge.size');
        line-height: dt('button.badge.size');
    }

    .p-button-raised {
        box-shadow: dt('button.raised.shadow');
    }

    .p-button-rounded {
        border-radius: dt('button.rounded.border.radius');
    }

    .p-button-secondary {
        background: dt('button.secondary.background');
        border: 1px solid dt('button.secondary.border.color');
        color: dt('button.secondary.color');
    }

    .p-button-secondary:not(:disabled):hover {
        background: dt('button.secondary.hover.background');
        border: 1px solid dt('button.secondary.hover.border.color');
        color: dt('button.secondary.hover.color');
    }

    .p-button-secondary:not(:disabled):active {
        background: dt('button.secondary.active.background');
        border: 1px solid dt('button.secondary.active.border.color');
        color: dt('button.secondary.active.color');
    }

    .p-button-secondary:focus-visible {
        outline-color: dt('button.secondary.focus.ring.color');
        box-shadow: dt('button.secondary.focus.ring.shadow');
    }

    .p-button-success {
        background: dt('button.success.background');
        border: 1px solid dt('button.success.border.color');
        color: dt('button.success.color');
    }

    .p-button-success:not(:disabled):hover {
        background: dt('button.success.hover.background');
        border: 1px solid dt('button.success.hover.border.color');
        color: dt('button.success.hover.color');
    }

    .p-button-success:not(:disabled):active {
        background: dt('button.success.active.background');
        border: 1px solid dt('button.success.active.border.color');
        color: dt('button.success.active.color');
    }

    .p-button-success:focus-visible {
        outline-color: dt('button.success.focus.ring.color');
        box-shadow: dt('button.success.focus.ring.shadow');
    }

    .p-button-info {
        background: dt('button.info.background');
        border: 1px solid dt('button.info.border.color');
        color: dt('button.info.color');
    }

    .p-button-info:not(:disabled):hover {
        background: dt('button.info.hover.background');
        border: 1px solid dt('button.info.hover.border.color');
        color: dt('button.info.hover.color');
    }

    .p-button-info:not(:disabled):active {
        background: dt('button.info.active.background');
        border: 1px solid dt('button.info.active.border.color');
        color: dt('button.info.active.color');
    }

    .p-button-info:focus-visible {
        outline-color: dt('button.info.focus.ring.color');
        box-shadow: dt('button.info.focus.ring.shadow');
    }

    .p-button-warn {
        background: dt('button.warn.background');
        border: 1px solid dt('button.warn.border.color');
        color: dt('button.warn.color');
    }

    .p-button-warn:not(:disabled):hover {
        background: dt('button.warn.hover.background');
        border: 1px solid dt('button.warn.hover.border.color');
        color: dt('button.warn.hover.color');
    }

    .p-button-warn:not(:disabled):active {
        background: dt('button.warn.active.background');
        border: 1px solid dt('button.warn.active.border.color');
        color: dt('button.warn.active.color');
    }

    .p-button-warn:focus-visible {
        outline-color: dt('button.warn.focus.ring.color');
        box-shadow: dt('button.warn.focus.ring.shadow');
    }

    .p-button-help {
        background: dt('button.help.background');
        border: 1px solid dt('button.help.border.color');
        color: dt('button.help.color');
    }

    .p-button-help:not(:disabled):hover {
        background: dt('button.help.hover.background');
        border: 1px solid dt('button.help.hover.border.color');
        color: dt('button.help.hover.color');
    }

    .p-button-help:not(:disabled):active {
        background: dt('button.help.active.background');
        border: 1px solid dt('button.help.active.border.color');
        color: dt('button.help.active.color');
    }

    .p-button-help:focus-visible {
        outline-color: dt('button.help.focus.ring.color');
        box-shadow: dt('button.help.focus.ring.shadow');
    }

    .p-button-danger {
        background: dt('button.danger.background');
        border: 1px solid dt('button.danger.border.color');
        color: dt('button.danger.color');
    }

    .p-button-danger:not(:disabled):hover {
        background: dt('button.danger.hover.background');
        border: 1px solid dt('button.danger.hover.border.color');
        color: dt('button.danger.hover.color');
    }

    .p-button-danger:not(:disabled):active {
        background: dt('button.danger.active.background');
        border: 1px solid dt('button.danger.active.border.color');
        color: dt('button.danger.active.color');
    }

    .p-button-danger:focus-visible {
        outline-color: dt('button.danger.focus.ring.color');
        box-shadow: dt('button.danger.focus.ring.shadow');
    }

    .p-button-contrast {
        background: dt('button.contrast.background');
        border: 1px solid dt('button.contrast.border.color');
        color: dt('button.contrast.color');
    }

    .p-button-contrast:not(:disabled):hover {
        background: dt('button.contrast.hover.background');
        border: 1px solid dt('button.contrast.hover.border.color');
        color: dt('button.contrast.hover.color');
    }

    .p-button-contrast:not(:disabled):active {
        background: dt('button.contrast.active.background');
        border: 1px solid dt('button.contrast.active.border.color');
        color: dt('button.contrast.active.color');
    }

    .p-button-contrast:focus-visible {
        outline-color: dt('button.contrast.focus.ring.color');
        box-shadow: dt('button.contrast.focus.ring.shadow');
    }

    .p-button-outlined {
        background: transparent;
        border-color: dt('button.outlined.primary.border.color');
        color: dt('button.outlined.primary.color');
    }

    .p-button-outlined:not(:disabled):hover {
        background: dt('button.outlined.primary.hover.background');
        border-color: dt('button.outlined.primary.border.color');
        color: dt('button.outlined.primary.color');
    }

    .p-button-outlined:not(:disabled):active {
        background: dt('button.outlined.primary.active.background');
        border-color: dt('button.outlined.primary.border.color');
        color: dt('button.outlined.primary.color');
    }

    .p-button-outlined.p-button-secondary {
        border-color: dt('button.outlined.secondary.border.color');
        color: dt('button.outlined.secondary.color');
    }

    .p-button-outlined.p-button-secondary:not(:disabled):hover {
        background: dt('button.outlined.secondary.hover.background');
        border-color: dt('button.outlined.secondary.border.color');
        color: dt('button.outlined.secondary.color');
    }

    .p-button-outlined.p-button-secondary:not(:disabled):active {
        background: dt('button.outlined.secondary.active.background');
        border-color: dt('button.outlined.secondary.border.color');
        color: dt('button.outlined.secondary.color');
    }

    .p-button-outlined.p-button-success {
        border-color: dt('button.outlined.success.border.color');
        color: dt('button.outlined.success.color');
    }

    .p-button-outlined.p-button-success:not(:disabled):hover {
        background: dt('button.outlined.success.hover.background');
        border-color: dt('button.outlined.success.border.color');
        color: dt('button.outlined.success.color');
    }

    .p-button-outlined.p-button-success:not(:disabled):active {
        background: dt('button.outlined.success.active.background');
        border-color: dt('button.outlined.success.border.color');
        color: dt('button.outlined.success.color');
    }

    .p-button-outlined.p-button-info {
        border-color: dt('button.outlined.info.border.color');
        color: dt('button.outlined.info.color');
    }

    .p-button-outlined.p-button-info:not(:disabled):hover {
        background: dt('button.outlined.info.hover.background');
        border-color: dt('button.outlined.info.border.color');
        color: dt('button.outlined.info.color');
    }

    .p-button-outlined.p-button-info:not(:disabled):active {
        background: dt('button.outlined.info.active.background');
        border-color: dt('button.outlined.info.border.color');
        color: dt('button.outlined.info.color');
    }

    .p-button-outlined.p-button-warn {
        border-color: dt('button.outlined.warn.border.color');
        color: dt('button.outlined.warn.color');
    }

    .p-button-outlined.p-button-warn:not(:disabled):hover {
        background: dt('button.outlined.warn.hover.background');
        border-color: dt('button.outlined.warn.border.color');
        color: dt('button.outlined.warn.color');
    }

    .p-button-outlined.p-button-warn:not(:disabled):active {
        background: dt('button.outlined.warn.active.background');
        border-color: dt('button.outlined.warn.border.color');
        color: dt('button.outlined.warn.color');
    }

    .p-button-outlined.p-button-help {
        border-color: dt('button.outlined.help.border.color');
        color: dt('button.outlined.help.color');
    }

    .p-button-outlined.p-button-help:not(:disabled):hover {
        background: dt('button.outlined.help.hover.background');
        border-color: dt('button.outlined.help.border.color');
        color: dt('button.outlined.help.color');
    }

    .p-button-outlined.p-button-help:not(:disabled):active {
        background: dt('button.outlined.help.active.background');
        border-color: dt('button.outlined.help.border.color');
        color: dt('button.outlined.help.color');
    }

    .p-button-outlined.p-button-danger {
        border-color: dt('button.outlined.danger.border.color');
        color: dt('button.outlined.danger.color');
    }

    .p-button-outlined.p-button-danger:not(:disabled):hover {
        background: dt('button.outlined.danger.hover.background');
        border-color: dt('button.outlined.danger.border.color');
        color: dt('button.outlined.danger.color');
    }

    .p-button-outlined.p-button-danger:not(:disabled):active {
        background: dt('button.outlined.danger.active.background');
        border-color: dt('button.outlined.danger.border.color');
        color: dt('button.outlined.danger.color');
    }

    .p-button-outlined.p-button-contrast {
        border-color: dt('button.outlined.contrast.border.color');
        color: dt('button.outlined.contrast.color');
    }

    .p-button-outlined.p-button-contrast:not(:disabled):hover {
        background: dt('button.outlined.contrast.hover.background');
        border-color: dt('button.outlined.contrast.border.color');
        color: dt('button.outlined.contrast.color');
    }

    .p-button-outlined.p-button-contrast:not(:disabled):active {
        background: dt('button.outlined.contrast.active.background');
        border-color: dt('button.outlined.contrast.border.color');
        color: dt('button.outlined.contrast.color');
    }

    .p-button-outlined.p-button-plain {
        border-color: dt('button.outlined.plain.border.color');
        color: dt('button.outlined.plain.color');
    }

    .p-button-outlined.p-button-plain:not(:disabled):hover {
        background: dt('button.outlined.plain.hover.background');
        border-color: dt('button.outlined.plain.border.color');
        color: dt('button.outlined.plain.color');
    }

    .p-button-outlined.p-button-plain:not(:disabled):active {
        background: dt('button.outlined.plain.active.background');
        border-color: dt('button.outlined.plain.border.color');
        color: dt('button.outlined.plain.color');
    }

    .p-button-text {
        background: transparent;
        border-color: transparent;
        color: dt('button.text.primary.color');
    }

    .p-button-text:not(:disabled):hover {
        background: dt('button.text.primary.hover.background');
        border-color: transparent;
        color: dt('button.text.primary.color');
    }

    .p-button-text:not(:disabled):active {
        background: dt('button.text.primary.active.background');
        border-color: transparent;
        color: dt('button.text.primary.color');
    }

    .p-button-text.p-button-secondary {
        background: transparent;
        border-color: transparent;
        color: dt('button.text.secondary.color');
    }

    .p-button-text.p-button-secondary:not(:disabled):hover {
        background: dt('button.text.secondary.hover.background');
        border-color: transparent;
        color: dt('button.text.secondary.color');
    }

    .p-button-text.p-button-secondary:not(:disabled):active {
        background: dt('button.text.secondary.active.background');
        border-color: transparent;
        color: dt('button.text.secondary.color');
    }

    .p-button-text.p-button-success {
        background: transparent;
        border-color: transparent;
        color: dt('button.text.success.color');
    }

    .p-button-text.p-button-success:not(:disabled):hover {
        background: dt('button.text.success.hover.background');
        border-color: transparent;
        color: dt('button.text.success.color');
    }

    .p-button-text.p-button-success:not(:disabled):active {
        background: dt('button.text.success.active.background');
        border-color: transparent;
        color: dt('button.text.success.color');
    }

    .p-button-text.p-button-info {
        background: transparent;
        border-color: transparent;
        color: dt('button.text.info.color');
    }

    .p-button-text.p-button-info:not(:disabled):hover {
        background: dt('button.text.info.hover.background');
        border-color: transparent;
        color: dt('button.text.info.color');
    }

    .p-button-text.p-button-info:not(:disabled):active {
        background: dt('button.text.info.active.background');
        border-color: transparent;
        color: dt('button.text.info.color');
    }

    .p-button-text.p-button-warn {
        background: transparent;
        border-color: transparent;
        color: dt('button.text.warn.color');
    }

    .p-button-text.p-button-warn:not(:disabled):hover {
        background: dt('button.text.warn.hover.background');
        border-color: transparent;
        color: dt('button.text.warn.color');
    }

    .p-button-text.p-button-warn:not(:disabled):active {
        background: dt('button.text.warn.active.background');
        border-color: transparent;
        color: dt('button.text.warn.color');
    }

    .p-button-text.p-button-help {
        background: transparent;
        border-color: transparent;
        color: dt('button.text.help.color');
    }

    .p-button-text.p-button-help:not(:disabled):hover {
        background: dt('button.text.help.hover.background');
        border-color: transparent;
        color: dt('button.text.help.color');
    }

    .p-button-text.p-button-help:not(:disabled):active {
        background: dt('button.text.help.active.background');
        border-color: transparent;
        color: dt('button.text.help.color');
    }

    .p-button-text.p-button-danger {
        background: transparent;
        border-color: transparent;
        color: dt('button.text.danger.color');
    }

    .p-button-text.p-button-danger:not(:disabled):hover {
        background: dt('button.text.danger.hover.background');
        border-color: transparent;
        color: dt('button.text.danger.color');
    }

    .p-button-text.p-button-danger:not(:disabled):active {
        background: dt('button.text.danger.active.background');
        border-color: transparent;
        color: dt('button.text.danger.color');
    }

    .p-button-text.p-button-contrast {
        background: transparent;
        border-color: transparent;
        color: dt('button.text.contrast.color');
    }

    .p-button-text.p-button-contrast:not(:disabled):hover {
        background: dt('button.text.contrast.hover.background');
        border-color: transparent;
        color: dt('button.text.contrast.color');
    }

    .p-button-text.p-button-contrast:not(:disabled):active {
        background: dt('button.text.contrast.active.background');
        border-color: transparent;
        color: dt('button.text.contrast.color');
    }

    .p-button-text.p-button-plain {
        background: transparent;
        border-color: transparent;
        color: dt('button.text.plain.color');
    }

    .p-button-text.p-button-plain:not(:disabled):hover {
        background: dt('button.text.plain.hover.background');
        border-color: transparent;
        color: dt('button.text.plain.color');
    }

    .p-button-text.p-button-plain:not(:disabled):active {
        background: dt('button.text.plain.active.background');
        border-color: transparent;
        color: dt('button.text.plain.color');
    }

    .p-button-link {
        background: transparent;
        border-color: transparent;
        color: dt('button.link.color');
    }

    .p-button-link:not(:disabled):hover {
        background: transparent;
        border-color: transparent;
        color: dt('button.link.hover.color');
    }

    .p-button-link:not(:disabled):hover .p-button-label {
        text-decoration: underline;
    }

    .p-button-link:not(:disabled):active {
        background: transparent;
        border-color: transparent;
        color: dt('button.link.active.color');
    }
`;
var style$m = css`
    .p-dialog {
        max-height: 90%;
        transform: scale(1);
        border-radius: dt('dialog.border.radius');
        box-shadow: dt('dialog.shadow');
        background: dt('dialog.background');
        border: 1px solid dt('dialog.border.color');
        color: dt('dialog.color');
    }

    .p-dialog-content {
        overflow-y: auto;
        padding: dt('dialog.content.padding');
    }

    .p-dialog-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-shrink: 0;
        padding: dt('dialog.header.padding');
    }

    .p-dialog-title {
        font-weight: dt('dialog.title.font.weight');
        font-size: dt('dialog.title.font.size');
    }

    .p-dialog-footer {
        flex-shrink: 0;
        padding: dt('dialog.footer.padding');
        display: flex;
        justify-content: flex-end;
        gap: dt('dialog.footer.gap');
    }

    .p-dialog-header-actions {
        display: flex;
        align-items: center;
        gap: dt('dialog.header.gap');
    }

    .p-dialog-enter-active {
        transition: all 150ms cubic-bezier(0, 0, 0.2, 1);
    }

    .p-dialog-leave-active {
        transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);
    }

    .p-dialog-enter-from,
    .p-dialog-leave-to {
        opacity: 0;
        transform: scale(0.7);
    }

    .p-dialog-top .p-dialog,
    .p-dialog-bottom .p-dialog,
    .p-dialog-left .p-dialog,
    .p-dialog-right .p-dialog,
    .p-dialog-topleft .p-dialog,
    .p-dialog-topright .p-dialog,
    .p-dialog-bottomleft .p-dialog,
    .p-dialog-bottomright .p-dialog {
        margin: 0.75rem;
        transform: translate3d(0px, 0px, 0px);
    }

    .p-dialog-top .p-dialog-enter-active,
    .p-dialog-top .p-dialog-leave-active,
    .p-dialog-bottom .p-dialog-enter-active,
    .p-dialog-bottom .p-dialog-leave-active,
    .p-dialog-left .p-dialog-enter-active,
    .p-dialog-left .p-dialog-leave-active,
    .p-dialog-right .p-dialog-enter-active,
    .p-dialog-right .p-dialog-leave-active,
    .p-dialog-topleft .p-dialog-enter-active,
    .p-dialog-topleft .p-dialog-leave-active,
    .p-dialog-topright .p-dialog-enter-active,
    .p-dialog-topright .p-dialog-leave-active,
    .p-dialog-bottomleft .p-dialog-enter-active,
    .p-dialog-bottomleft .p-dialog-leave-active,
    .p-dialog-bottomright .p-dialog-enter-active,
    .p-dialog-bottomright .p-dialog-leave-active {
        transition: all 0.3s ease-out;
    }

    .p-dialog-top .p-dialog-enter-from,
    .p-dialog-top .p-dialog-leave-to {
        transform: translate3d(0px, -100%, 0px);
    }

    .p-dialog-bottom .p-dialog-enter-from,
    .p-dialog-bottom .p-dialog-leave-to {
        transform: translate3d(0px, 100%, 0px);
    }

    .p-dialog-left .p-dialog-enter-from,
    .p-dialog-left .p-dialog-leave-to,
    .p-dialog-topleft .p-dialog-enter-from,
    .p-dialog-topleft .p-dialog-leave-to,
    .p-dialog-bottomleft .p-dialog-enter-from,
    .p-dialog-bottomleft .p-dialog-leave-to {
        transform: translate3d(-100%, 0px, 0px);
    }

    .p-dialog-right .p-dialog-enter-from,
    .p-dialog-right .p-dialog-leave-to,
    .p-dialog-topright .p-dialog-enter-from,
    .p-dialog-topright .p-dialog-leave-to,
    .p-dialog-bottomright .p-dialog-enter-from,
    .p-dialog-bottomright .p-dialog-leave-to {
        transform: translate3d(100%, 0px, 0px);
    }

    .p-dialog-left:dir(rtl) .p-dialog-enter-from,
    .p-dialog-left:dir(rtl) .p-dialog-leave-to,
    .p-dialog-topleft:dir(rtl) .p-dialog-enter-from,
    .p-dialog-topleft:dir(rtl) .p-dialog-leave-to,
    .p-dialog-bottomleft:dir(rtl) .p-dialog-enter-from,
    .p-dialog-bottomleft:dir(rtl) .p-dialog-leave-to {
        transform: translate3d(100%, 0px, 0px);
    }

    .p-dialog-right:dir(rtl) .p-dialog-enter-from,
    .p-dialog-right:dir(rtl) .p-dialog-leave-to,
    .p-dialog-topright:dir(rtl) .p-dialog-enter-from,
    .p-dialog-topright:dir(rtl) .p-dialog-leave-to,
    .p-dialog-bottomright:dir(rtl) .p-dialog-enter-from,
    .p-dialog-bottomright:dir(rtl) .p-dialog-leave-to {
        transform: translate3d(-100%, 0px, 0px);
    }

    .p-dialog-maximized {
        width: 100vw !important;
        height: 100vh !important;
        top: 0px !important;
        left: 0px !important;
        max-height: 100%;
        height: 100%;
        border-radius: 0;
    }

    .p-dialog-maximized .p-dialog-content {
        flex-grow: 1;
    }
`;
var style$l = css`
    .p-splitter {
        display: flex;
        flex-wrap: nowrap;
        border: 1px solid dt('splitter.border.color');
        background: dt('splitter.background');
        border-radius: dt('border.radius.md');
        color: dt('splitter.color');
    }

    .p-splitter-vertical {
        flex-direction: column;
    }

    .p-splitter-gutter {
        flex-grow: 0;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1;
        background: dt('splitter.gutter.background');
    }

    .p-splitter-gutter-handle {
        border-radius: dt('splitter.handle.border.radius');
        background: dt('splitter.handle.background');
        transition:
            outline-color dt('splitter.transition.duration'),
            box-shadow dt('splitter.transition.duration');
        outline-color: transparent;
    }

    .p-splitter-gutter-handle:focus-visible {
        box-shadow: dt('splitter.handle.focus.ring.shadow');
        outline: dt('splitter.handle.focus.ring.width') dt('splitter.handle.focus.ring.style') dt('splitter.handle.focus.ring.color');
        outline-offset: dt('splitter.handle.focus.ring.offset');
    }

    .p-splitter-horizontal.p-splitter-resizing {
        cursor: col-resize;
        user-select: none;
    }

    .p-splitter-vertical.p-splitter-resizing {
        cursor: row-resize;
        user-select: none;
    }

    .p-splitter-horizontal > .p-splitter-gutter > .p-splitter-gutter-handle {
        height: dt('splitter.handle.size');
        width: 100%;
    }

    .p-splitter-vertical > .p-splitter-gutter > .p-splitter-gutter-handle {
        width: dt('splitter.handle.size');
        height: 100%;
    }

    .p-splitter-horizontal > .p-splitter-gutter {
        cursor: col-resize;
    }

    .p-splitter-vertical > .p-splitter-gutter {
        cursor: row-resize;
    }

    .p-splitterpanel {
        flex-grow: 1;
        overflow: hidden;
    }

    .p-splitterpanel-nested {
        display: flex;
    }

    .p-splitterpanel .p-splitter {
        flex-grow: 1;
        border: 0 none;
    }
`;
var style$k = css`
    .p-contextmenu {
        background: dt('contextmenu.background');
        color: dt('contextmenu.color');
        border: 1px solid dt('contextmenu.border.color');
        border-radius: dt('contextmenu.border.radius');
        box-shadow: dt('contextmenu.shadow');
        min-width: 12.5rem;
    }

    .p-contextmenu-root-list,
    .p-contextmenu-submenu {
        margin: 0;
        padding: dt('contextmenu.list.padding');
        list-style: none;
        outline: 0 none;
        display: flex;
        flex-direction: column;
        gap: dt('contextmenu.list.gap');
    }

    .p-contextmenu-submenu {
        position: absolute;
        display: flex;
        flex-direction: column;
        min-width: 100%;
        z-index: 1;
        background: dt('contextmenu.background');
        color: dt('contextmenu.color');
        border: 1px solid dt('contextmenu.border.color');
        border-radius: dt('contextmenu.border.radius');
        box-shadow: dt('contextmenu.shadow');
    }

    .p-contextmenu-item {
        position: relative;
    }

    .p-contextmenu-item-content {
        transition:
            background dt('contextmenu.transition.duration'),
            color dt('contextmenu.transition.duration');
        border-radius: dt('contextmenu.item.border.radius');
        color: dt('contextmenu.item.color');
    }

    .p-contextmenu-item-link {
        cursor: pointer;
        display: flex;
        align-items: center;
        text-decoration: none;
        overflow: hidden;
        position: relative;
        color: inherit;
        padding: dt('contextmenu.item.padding');
        gap: dt('contextmenu.item.gap');
        user-select: none;
    }

    .p-contextmenu-item-label {
        line-height: 1;
    }

    .p-contextmenu-item-icon {
        color: dt('contextmenu.item.icon.color');
    }

    .p-contextmenu-submenu-icon {
        color: dt('contextmenu.submenu.icon.color');
        margin-left: auto;
        font-size: dt('contextmenu.submenu.icon.size');
        width: dt('contextmenu.submenu.icon.size');
        height: dt('contextmenu.submenu.icon.size');
    }

    .p-contextmenu-submenu-icon:dir(rtl) {
        margin-left: 0;
        margin-right: auto;
    }

    .p-contextmenu-item.p-focus > .p-contextmenu-item-content {
        color: dt('contextmenu.item.focus.color');
        background: dt('contextmenu.item.focus.background');
    }

    .p-contextmenu-item.p-focus > .p-contextmenu-item-content .p-contextmenu-item-icon {
        color: dt('contextmenu.item.icon.focus.color');
    }

    .p-contextmenu-item.p-focus > .p-contextmenu-item-content .p-contextmenu-submenu-icon {
        color: dt('contextmenu.submenu.icon.focus.color');
    }

    .p-contextmenu-item:not(.p-disabled) > .p-contextmenu-item-content:hover {
        color: dt('contextmenu.item.focus.color');
        background: dt('contextmenu.item.focus.background');
    }

    .p-contextmenu-item:not(.p-disabled) > .p-contextmenu-item-content:hover .p-contextmenu-item-icon {
        color: dt('contextmenu.item.icon.focus.color');
    }

    .p-contextmenu-item:not(.p-disabled) > .p-contextmenu-item-content:hover .p-contextmenu-submenu-icon {
        color: dt('contextmenu.submenu.icon.focus.color');
    }

    .p-contextmenu-item-active > .p-contextmenu-item-content {
        color: dt('contextmenu.item.active.color');
        background: dt('contextmenu.item.active.background');
    }

    .p-contextmenu-item-active > .p-contextmenu-item-content .p-contextmenu-item-icon {
        color: dt('contextmenu.item.icon.active.color');
    }

    .p-contextmenu-item-active > .p-contextmenu-item-content .p-contextmenu-submenu-icon {
        color: dt('contextmenu.submenu.icon.active.color');
    }

    .p-contextmenu-separator {
        border-block-start: 1px solid dt('contextmenu.separator.border.color');
    }

    .p-contextmenu-enter-from,
    .p-contextmenu-leave-active {
        opacity: 0;
    }

    .p-contextmenu-enter-active {
        transition: opacity 250ms;
    }

    .p-contextmenu-mobile .p-contextmenu-submenu {
        position: static;
        box-shadow: none;
        border: 0 none;
        padding-inline-start: dt('tieredmenu.submenu.mobile.indent');
        padding-inline-end: 0;
    }

    .p-contextmenu-mobile .p-contextmenu-submenu-icon {
        transition: transform 0.2s;
        transform: rotate(90deg);
    }

    .p-contextmenu-mobile .p-contextmenu-item-active > .p-contextmenu-item-content .p-contextmenu-submenu-icon {
        transform: rotate(-90deg);
    }
`;
var style$j = css`
    .p-toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        padding: dt('toolbar.padding');
        background: dt('toolbar.background');
        border: 1px solid dt('toolbar.border.color');
        color: dt('toolbar.color');
        border-radius: dt('toolbar.border.radius');
        gap: dt('toolbar.gap');
    }

    .p-toolbar-start,
    .p-toolbar-center,
    .p-toolbar-end {
        display: flex;
        align-items: center;
    }
`;
var style$i = css`
    .p-confirmdialog .p-dialog-content {
        display: flex;
        align-items: center;
        gap: dt('confirmdialog.content.gap');
    }

    .p-confirmdialog-icon {
        color: dt('confirmdialog.icon.color');
        font-size: dt('confirmdialog.icon.size');
        width: dt('confirmdialog.icon.size');
        height: dt('confirmdialog.icon.size');
    }
`;
var style$h = css`
    .p-iconfield {
        position: relative;
    }

    .p-inputicon {
        position: absolute;
        top: 50%;
        margin-top: calc(-1 * (dt('icon.size') / 2));
        color: dt('iconfield.icon.color');
        line-height: 1;
        z-index: 1;
    }

    .p-iconfield .p-inputicon:first-child {
        inset-inline-start: dt('form.field.padding.x');
    }

    .p-iconfield .p-inputicon:last-child {
        inset-inline-end: dt('form.field.padding.x');
    }

    .p-iconfield .p-inputtext:not(:first-child),
    .p-iconfield .p-inputwrapper:not(:first-child) .p-inputtext {
        padding-inline-start: calc((dt('form.field.padding.x') * 2) + dt('icon.size'));
    }

    .p-iconfield .p-inputtext:not(:last-child) {
        padding-inline-end: calc((dt('form.field.padding.x') * 2) + dt('icon.size'));
    }

    .p-iconfield:has(.p-inputfield-sm) .p-inputicon {
        font-size: dt('form.field.sm.font.size');
        width: dt('form.field.sm.font.size');
        height: dt('form.field.sm.font.size');
        margin-top: calc(-1 * (dt('form.field.sm.font.size') / 2));
    }

    .p-iconfield:has(.p-inputfield-lg) .p-inputicon {
        font-size: dt('form.field.lg.font.size');
        width: dt('form.field.lg.font.size');
        height: dt('form.field.lg.font.size');
        margin-top: calc(-1 * (dt('form.field.lg.font.size') / 2));
    }
`;
var style$g = css`
    .p-inputtext {
        font-family: inherit;
        font-feature-settings: inherit;
        font-size: 1rem;
        color: dt('inputtext.color');
        background: dt('inputtext.background');
        padding-block: dt('inputtext.padding.y');
        padding-inline: dt('inputtext.padding.x');
        border: 1px solid dt('inputtext.border.color');
        transition:
            background dt('inputtext.transition.duration'),
            color dt('inputtext.transition.duration'),
            border-color dt('inputtext.transition.duration'),
            outline-color dt('inputtext.transition.duration'),
            box-shadow dt('inputtext.transition.duration');
        appearance: none;
        border-radius: dt('inputtext.border.radius');
        outline-color: transparent;
        box-shadow: dt('inputtext.shadow');
    }

    .p-inputtext:enabled:hover {
        border-color: dt('inputtext.hover.border.color');
    }

    .p-inputtext:enabled:focus {
        border-color: dt('inputtext.focus.border.color');
        box-shadow: dt('inputtext.focus.ring.shadow');
        outline: dt('inputtext.focus.ring.width') dt('inputtext.focus.ring.style') dt('inputtext.focus.ring.color');
        outline-offset: dt('inputtext.focus.ring.offset');
    }

    .p-inputtext.p-invalid {
        border-color: dt('inputtext.invalid.border.color');
    }

    .p-inputtext.p-variant-filled {
        background: dt('inputtext.filled.background');
    }

    .p-inputtext.p-variant-filled:enabled:hover {
        background: dt('inputtext.filled.hover.background');
    }

    .p-inputtext.p-variant-filled:enabled:focus {
        background: dt('inputtext.filled.focus.background');
    }

    .p-inputtext:disabled {
        opacity: 1;
        background: dt('inputtext.disabled.background');
        color: dt('inputtext.disabled.color');
    }

    .p-inputtext::placeholder {
        color: dt('inputtext.placeholder.color');
    }

    .p-inputtext.p-invalid::placeholder {
        color: dt('inputtext.invalid.placeholder.color');
    }

    .p-inputtext-sm {
        font-size: dt('inputtext.sm.font.size');
        padding-block: dt('inputtext.sm.padding.y');
        padding-inline: dt('inputtext.sm.padding.x');
    }

    .p-inputtext-lg {
        font-size: dt('inputtext.lg.font.size');
        padding-block: dt('inputtext.lg.padding.y');
        padding-inline: dt('inputtext.lg.padding.x');
    }

    .p-inputtext-fluid {
        width: 100%;
    }
`;
var style$f = css`
    .p-tree {
        background: dt('tree.background');
        color: dt('tree.color');
        padding: dt('tree.padding');
    }

    .p-tree-root-children,
    .p-tree-node-children {
        display: flex;
        list-style-type: none;
        flex-direction: column;
        margin: 0;
        gap: dt('tree.gap');
    }

    .p-tree-root-children {
        padding: 0;
        padding-block-start: dt('tree.gap');
    }

    .p-tree-node-children {
        padding: 0;
        padding-block-start: dt('tree.gap');
        padding-inline-start: dt('tree.indent');
    }

    .p-tree-node {
        padding: 0;
        outline: 0 none;
    }

    .p-tree-node-content {
        border-radius: dt('tree.node.border.radius');
        padding: dt('tree.node.padding');
        display: flex;
        align-items: center;
        outline-color: transparent;
        color: dt('tree.node.color');
        gap: dt('tree.node.gap');
        transition:
            background dt('tree.transition.duration'),
            color dt('tree.transition.duration'),
            outline-color dt('tree.transition.duration'),
            box-shadow dt('tree.transition.duration');
    }

    .p-tree-node:focus-visible > .p-tree-node-content {
        box-shadow: dt('tree.node.focus.ring.shadow');
        outline: dt('tree.node.focus.ring.width') dt('tree.node.focus.ring.style') dt('tree.node.focus.ring.color');
        outline-offset: dt('tree.node.focus.ring.offset');
    }

    .p-tree-node-content.p-tree-node-selectable:not(.p-tree-node-selected):hover {
        background: dt('tree.node.hover.background');
        color: dt('tree.node.hover.color');
    }

    .p-tree-node-content.p-tree-node-selectable:not(.p-tree-node-selected):hover .p-tree-node-icon {
        color: dt('tree.node.icon.hover.color');
    }

    .p-tree-node-content.p-tree-node-selected {
        background: dt('tree.node.selected.background');
        color: dt('tree.node.selected.color');
    }

    .p-tree-node-content.p-tree-node-selected .p-tree-node-toggle-button {
        color: inherit;
    }

    .p-tree-node-toggle-button {
        cursor: pointer;
        user-select: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
        flex-shrink: 0;
        width: dt('tree.node.toggle.button.size');
        height: dt('tree.node.toggle.button.size');
        color: dt('tree.node.toggle.button.color');
        border: 0 none;
        background: transparent;
        border-radius: dt('tree.node.toggle.button.border.radius');
        transition:
            background dt('tree.transition.duration'),
            color dt('tree.transition.duration'),
            border-color dt('tree.transition.duration'),
            outline-color dt('tree.transition.duration'),
            box-shadow dt('tree.transition.duration');
        outline-color: transparent;
        padding: 0;
    }

    .p-tree-node-toggle-button:enabled:hover {
        background: dt('tree.node.toggle.button.hover.background');
        color: dt('tree.node.toggle.button.hover.color');
    }

    .p-tree-node-content.p-tree-node-selected .p-tree-node-toggle-button:hover {
        background: dt('tree.node.toggle.button.selected.hover.background');
        color: dt('tree.node.toggle.button.selected.hover.color');
    }

    .p-tree-root {
        overflow: auto;
    }

    .p-tree-node-selectable {
        cursor: pointer;
        user-select: none;
    }

    .p-tree-node-leaf > .p-tree-node-content .p-tree-node-toggle-button {
        visibility: hidden;
    }

    .p-tree-node-icon {
        color: dt('tree.node.icon.color');
        transition: color dt('tree.transition.duration');
    }

    .p-tree-node-content.p-tree-node-selected .p-tree-node-icon {
        color: dt('tree.node.icon.selected.color');
    }

    .p-tree-filter {
        margin: dt('tree.filter.margin');
    }

    .p-tree-filter-input {
        width: 100%;
    }

    .p-tree-loading {
        position: relative;
        height: 100%;
    }

    .p-tree-loading-icon {
        font-size: dt('tree.loading.icon.size');
        width: dt('tree.loading.icon.size');
        height: dt('tree.loading.icon.size');
    }

    .p-tree .p-tree-mask {
        position: absolute;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .p-tree-flex-scrollable {
        display: flex;
        flex: 1;
        height: 100%;
        flex-direction: column;
    }

    .p-tree-flex-scrollable .p-tree-root {
        flex: 1;
    }
`;
var style$e = css`
    .p-checkbox {
        position: relative;
        display: inline-flex;
        user-select: none;
        vertical-align: bottom;
        width: dt('checkbox.width');
        height: dt('checkbox.height');
    }

    .p-checkbox-input {
        cursor: pointer;
        appearance: none;
        position: absolute;
        inset-block-start: 0;
        inset-inline-start: 0;
        width: 100%;
        height: 100%;
        padding: 0;
        margin: 0;
        opacity: 0;
        z-index: 1;
        outline: 0 none;
        border: 1px solid transparent;
        border-radius: dt('checkbox.border.radius');
    }

    .p-checkbox-box {
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: dt('checkbox.border.radius');
        border: 1px solid dt('checkbox.border.color');
        background: dt('checkbox.background');
        width: dt('checkbox.width');
        height: dt('checkbox.height');
        transition:
            background dt('checkbox.transition.duration'),
            color dt('checkbox.transition.duration'),
            border-color dt('checkbox.transition.duration'),
            box-shadow dt('checkbox.transition.duration'),
            outline-color dt('checkbox.transition.duration');
        outline-color: transparent;
        box-shadow: dt('checkbox.shadow');
    }

    .p-checkbox-icon {
        transition-duration: dt('checkbox.transition.duration');
        color: dt('checkbox.icon.color');
        font-size: dt('checkbox.icon.size');
        width: dt('checkbox.icon.size');
        height: dt('checkbox.icon.size');
    }

    .p-checkbox:not(.p-disabled):has(.p-checkbox-input:hover) .p-checkbox-box {
        border-color: dt('checkbox.hover.border.color');
    }

    .p-checkbox-checked .p-checkbox-box {
        border-color: dt('checkbox.checked.border.color');
        background: dt('checkbox.checked.background');
    }

    .p-checkbox-checked .p-checkbox-icon {
        color: dt('checkbox.icon.checked.color');
    }

    .p-checkbox-checked:not(.p-disabled):has(.p-checkbox-input:hover) .p-checkbox-box {
        background: dt('checkbox.checked.hover.background');
        border-color: dt('checkbox.checked.hover.border.color');
    }

    .p-checkbox-checked:not(.p-disabled):has(.p-checkbox-input:hover) .p-checkbox-icon {
        color: dt('checkbox.icon.checked.hover.color');
    }

    .p-checkbox:not(.p-disabled):has(.p-checkbox-input:focus-visible) .p-checkbox-box {
        border-color: dt('checkbox.focus.border.color');
        box-shadow: dt('checkbox.focus.ring.shadow');
        outline: dt('checkbox.focus.ring.width') dt('checkbox.focus.ring.style') dt('checkbox.focus.ring.color');
        outline-offset: dt('checkbox.focus.ring.offset');
    }

    .p-checkbox-checked:not(.p-disabled):has(.p-checkbox-input:focus-visible) .p-checkbox-box {
        border-color: dt('checkbox.checked.focus.border.color');
    }

    .p-checkbox.p-invalid > .p-checkbox-box {
        border-color: dt('checkbox.invalid.border.color');
    }

    .p-checkbox.p-variant-filled .p-checkbox-box {
        background: dt('checkbox.filled.background');
    }

    .p-checkbox-checked.p-variant-filled .p-checkbox-box {
        background: dt('checkbox.checked.background');
    }

    .p-checkbox-checked.p-variant-filled:not(.p-disabled):has(.p-checkbox-input:hover) .p-checkbox-box {
        background: dt('checkbox.checked.hover.background');
    }

    .p-checkbox.p-disabled {
        opacity: 1;
    }

    .p-checkbox.p-disabled .p-checkbox-box {
        background: dt('checkbox.disabled.background');
        border-color: dt('checkbox.checked.disabled.border.color');
    }

    .p-checkbox.p-disabled .p-checkbox-box .p-checkbox-icon {
        color: dt('checkbox.icon.disabled.color');
    }

    .p-checkbox-sm,
    .p-checkbox-sm .p-checkbox-box {
        width: dt('checkbox.sm.width');
        height: dt('checkbox.sm.height');
    }

    .p-checkbox-sm .p-checkbox-icon {
        font-size: dt('checkbox.icon.sm.size');
        width: dt('checkbox.icon.sm.size');
        height: dt('checkbox.icon.sm.size');
    }

    .p-checkbox-lg,
    .p-checkbox-lg .p-checkbox-box {
        width: dt('checkbox.lg.width');
        height: dt('checkbox.lg.height');
    }

    .p-checkbox-lg .p-checkbox-icon {
        font-size: dt('checkbox.icon.lg.size');
        width: dt('checkbox.icon.lg.size');
        height: dt('checkbox.icon.lg.size');
    }
`;
var style$d = css`
    .p-message {
        border-radius: dt('message.border.radius');
        outline-width: dt('message.border.width');
        outline-style: solid;
    }

    .p-message-content {
        display: flex;
        align-items: center;
        padding: dt('message.content.padding');
        gap: dt('message.content.gap');
        height: 100%;
    }

    .p-message-icon {
        flex-shrink: 0;
    }

    .p-message-close-button {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-inline-start: auto;
        overflow: hidden;
        position: relative;
        width: dt('message.close.button.width');
        height: dt('message.close.button.height');
        border-radius: dt('message.close.button.border.radius');
        background: transparent;
        transition:
            background dt('message.transition.duration'),
            color dt('message.transition.duration'),
            outline-color dt('message.transition.duration'),
            box-shadow dt('message.transition.duration'),
            opacity 0.3s;
        outline-color: transparent;
        color: inherit;
        padding: 0;
        border: none;
        cursor: pointer;
        user-select: none;
    }

    .p-message-close-icon {
        font-size: dt('message.close.icon.size');
        width: dt('message.close.icon.size');
        height: dt('message.close.icon.size');
    }

    .p-message-close-button:focus-visible {
        outline-width: dt('message.close.button.focus.ring.width');
        outline-style: dt('message.close.button.focus.ring.style');
        outline-offset: dt('message.close.button.focus.ring.offset');
    }

    .p-message-info {
        background: dt('message.info.background');
        outline-color: dt('message.info.border.color');
        color: dt('message.info.color');
        box-shadow: dt('message.info.shadow');
    }

    .p-message-info .p-message-close-button:focus-visible {
        outline-color: dt('message.info.close.button.focus.ring.color');
        box-shadow: dt('message.info.close.button.focus.ring.shadow');
    }

    .p-message-info .p-message-close-button:hover {
        background: dt('message.info.close.button.hover.background');
    }

    .p-message-info.p-message-outlined {
        color: dt('message.info.outlined.color');
        outline-color: dt('message.info.outlined.border.color');
    }

    .p-message-info.p-message-simple {
        color: dt('message.info.simple.color');
    }

    .p-message-success {
        background: dt('message.success.background');
        outline-color: dt('message.success.border.color');
        color: dt('message.success.color');
        box-shadow: dt('message.success.shadow');
    }

    .p-message-success .p-message-close-button:focus-visible {
        outline-color: dt('message.success.close.button.focus.ring.color');
        box-shadow: dt('message.success.close.button.focus.ring.shadow');
    }

    .p-message-success .p-message-close-button:hover {
        background: dt('message.success.close.button.hover.background');
    }

    .p-message-success.p-message-outlined {
        color: dt('message.success.outlined.color');
        outline-color: dt('message.success.outlined.border.color');
    }

    .p-message-success.p-message-simple {
        color: dt('message.success.simple.color');
    }

    .p-message-warn {
        background: dt('message.warn.background');
        outline-color: dt('message.warn.border.color');
        color: dt('message.warn.color');
        box-shadow: dt('message.warn.shadow');
    }

    .p-message-warn .p-message-close-button:focus-visible {
        outline-color: dt('message.warn.close.button.focus.ring.color');
        box-shadow: dt('message.warn.close.button.focus.ring.shadow');
    }

    .p-message-warn .p-message-close-button:hover {
        background: dt('message.warn.close.button.hover.background');
    }

    .p-message-warn.p-message-outlined {
        color: dt('message.warn.outlined.color');
        outline-color: dt('message.warn.outlined.border.color');
    }

    .p-message-warn.p-message-simple {
        color: dt('message.warn.simple.color');
    }

    .p-message-error {
        background: dt('message.error.background');
        outline-color: dt('message.error.border.color');
        color: dt('message.error.color');
        box-shadow: dt('message.error.shadow');
    }

    .p-message-error .p-message-close-button:focus-visible {
        outline-color: dt('message.error.close.button.focus.ring.color');
        box-shadow: dt('message.error.close.button.focus.ring.shadow');
    }

    .p-message-error .p-message-close-button:hover {
        background: dt('message.error.close.button.hover.background');
    }

    .p-message-error.p-message-outlined {
        color: dt('message.error.outlined.color');
        outline-color: dt('message.error.outlined.border.color');
    }

    .p-message-error.p-message-simple {
        color: dt('message.error.simple.color');
    }

    .p-message-secondary {
        background: dt('message.secondary.background');
        outline-color: dt('message.secondary.border.color');
        color: dt('message.secondary.color');
        box-shadow: dt('message.secondary.shadow');
    }

    .p-message-secondary .p-message-close-button:focus-visible {
        outline-color: dt('message.secondary.close.button.focus.ring.color');
        box-shadow: dt('message.secondary.close.button.focus.ring.shadow');
    }

    .p-message-secondary .p-message-close-button:hover {
        background: dt('message.secondary.close.button.hover.background');
    }

    .p-message-secondary.p-message-outlined {
        color: dt('message.secondary.outlined.color');
        outline-color: dt('message.secondary.outlined.border.color');
    }

    .p-message-secondary.p-message-simple {
        color: dt('message.secondary.simple.color');
    }

    .p-message-contrast {
        background: dt('message.contrast.background');
        outline-color: dt('message.contrast.border.color');
        color: dt('message.contrast.color');
        box-shadow: dt('message.contrast.shadow');
    }

    .p-message-contrast .p-message-close-button:focus-visible {
        outline-color: dt('message.contrast.close.button.focus.ring.color');
        box-shadow: dt('message.contrast.close.button.focus.ring.shadow');
    }

    .p-message-contrast .p-message-close-button:hover {
        background: dt('message.contrast.close.button.hover.background');
    }

    .p-message-contrast.p-message-outlined {
        color: dt('message.contrast.outlined.color');
        outline-color: dt('message.contrast.outlined.border.color');
    }

    .p-message-contrast.p-message-simple {
        color: dt('message.contrast.simple.color');
    }

    .p-message-text {
        font-size: dt('message.text.font.size');
        font-weight: dt('message.text.font.weight');
    }

    .p-message-icon {
        font-size: dt('message.icon.size');
        width: dt('message.icon.size');
        height: dt('message.icon.size');
    }

    .p-message-enter-from {
        opacity: 0;
    }

    .p-message-enter-active {
        transition: opacity 0.3s;
    }

    .p-message.p-message-leave-from {
        max-height: 1000px;
    }

    .p-message.p-message-leave-to {
        max-height: 0;
        opacity: 0;
        margin: 0;
    }

    .p-message-leave-active {
        overflow: hidden;
        transition:
            max-height 0.45s cubic-bezier(0, 1, 0, 1),
            opacity 0.3s,
            margin 0.3s;
    }

    .p-message-leave-active .p-message-close-button {
        opacity: 0;
    }

    .p-message-sm .p-message-content {
        padding: dt('message.content.sm.padding');
    }

    .p-message-sm .p-message-text {
        font-size: dt('message.text.sm.font.size');
    }

    .p-message-sm .p-message-icon {
        font-size: dt('message.icon.sm.size');
        width: dt('message.icon.sm.size');
        height: dt('message.icon.sm.size');
    }

    .p-message-sm .p-message-close-icon {
        font-size: dt('message.close.icon.sm.size');
        width: dt('message.close.icon.sm.size');
        height: dt('message.close.icon.sm.size');
    }

    .p-message-lg .p-message-content {
        padding: dt('message.content.lg.padding');
    }

    .p-message-lg .p-message-text {
        font-size: dt('message.text.lg.font.size');
    }

    .p-message-lg .p-message-icon {
        font-size: dt('message.icon.lg.size');
        width: dt('message.icon.lg.size');
        height: dt('message.icon.lg.size');
    }

    .p-message-lg .p-message-close-icon {
        font-size: dt('message.close.icon.lg.size');
        width: dt('message.close.icon.lg.size');
        height: dt('message.close.icon.lg.size');
    }

    .p-message-outlined {
        background: transparent;
        outline-width: dt('message.outlined.border.width');
    }

    .p-message-simple {
        background: transparent;
        outline-color: transparent;
        box-shadow: none;
    }

    .p-message-simple .p-message-content {
        padding: dt('message.simple.content.padding');
    }

    .p-message-outlined .p-message-close-button:hover,
    .p-message-simple .p-message-close-button:hover {
        background: transparent;
    }
`;
function isEmpty(value) {
  return value === null || value === void 0 || value === "" || Array.isArray(value) && value.length === 0 || !(value instanceof Date) && typeof value === "object" && Object.keys(value).length === 0;
}
function isNotEmpty(value) {
  return !isEmpty(value);
}
function isObject(value, empty = true) {
  return value instanceof Object && value.constructor === Object && (empty || Object.keys(value).length !== 0);
}
var toValues = (value, name) => {
  if (isObject(value) && value.hasOwnProperty(name)) {
    return value;
  }
  return name ? { [name]: value } : value;
};
var zodResolver = (schema, schemaOptions, resolverOptions) => async ({ values, name }) => {
  const { sync = false, raw = false } = {};
  try {
    const result = await schema[sync ? "parse" : "parseAsync"](values, schemaOptions);
    return {
      values: toValues(raw ? values : result, name),
      errors: {}
    };
  } catch (e) {
    if (Array.isArray(e == null ? void 0 : e.errors)) {
      return {
        values: toValues(raw ? values : void 0, name),
        errors: e.errors.reduce((acc, error) => {
          const pathKey = isNotEmpty(error.path) ? error.path[0] : name;
          if (pathKey) {
            acc[pathKey] || (acc[pathKey] = []);
            acc[pathKey].push(error);
          }
          return acc;
        }, {})
      };
    }
    throw e;
  }
};
var style$c = css`
    .p-virtualscroller-loader {
        background: dt('virtualscroller.loader.mask.background');
        color: dt('virtualscroller.loader.mask.color');
    }

    .p-virtualscroller-loading-icon {
        font-size: dt('virtualscroller.loader.icon.size');
        width: dt('virtualscroller.loader.icon.size');
        height: dt('virtualscroller.loader.icon.size');
    }
`;
var style$b = css`
    .p-select {
        display: inline-flex;
        cursor: pointer;
        position: relative;
        user-select: none;
        background: dt('select.background');
        border: 1px solid dt('select.border.color');
        transition:
            background dt('select.transition.duration'),
            color dt('select.transition.duration'),
            border-color dt('select.transition.duration'),
            outline-color dt('select.transition.duration'),
            box-shadow dt('select.transition.duration');
        border-radius: dt('select.border.radius');
        outline-color: transparent;
        box-shadow: dt('select.shadow');
    }

    .p-select:not(.p-disabled):hover {
        border-color: dt('select.hover.border.color');
    }

    .p-select:not(.p-disabled).p-focus {
        border-color: dt('select.focus.border.color');
        box-shadow: dt('select.focus.ring.shadow');
        outline: dt('select.focus.ring.width') dt('select.focus.ring.style') dt('select.focus.ring.color');
        outline-offset: dt('select.focus.ring.offset');
    }

    .p-select.p-variant-filled {
        background: dt('select.filled.background');
    }

    .p-select.p-variant-filled:not(.p-disabled):hover {
        background: dt('select.filled.hover.background');
    }

    .p-select.p-variant-filled:not(.p-disabled).p-focus {
        background: dt('select.filled.focus.background');
    }

    .p-select.p-invalid {
        border-color: dt('select.invalid.border.color');
    }

    .p-select.p-disabled {
        opacity: 1;
        background: dt('select.disabled.background');
    }

    .p-select-clear-icon {
        position: absolute;
        top: 50%;
        margin-top: -0.5rem;
        color: dt('select.clear.icon.color');
        inset-inline-end: dt('select.dropdown.width');
    }

    .p-select-dropdown {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        background: transparent;
        color: dt('select.dropdown.color');
        width: dt('select.dropdown.width');
        border-start-end-radius: dt('select.border.radius');
        border-end-end-radius: dt('select.border.radius');
    }

    .p-select-label {
        display: block;
        white-space: nowrap;
        overflow: hidden;
        flex: 1 1 auto;
        width: 1%;
        padding: dt('select.padding.y') dt('select.padding.x');
        text-overflow: ellipsis;
        cursor: pointer;
        color: dt('select.color');
        background: transparent;
        border: 0 none;
        outline: 0 none;
    }

    .p-select-label.p-placeholder {
        color: dt('select.placeholder.color');
    }

    .p-select.p-invalid .p-select-label.p-placeholder {
        color: dt('select.invalid.placeholder.color');
    }

    .p-select:has(.p-select-clear-icon) .p-select-label {
        padding-inline-end: calc(1rem + dt('select.padding.x'));
    }

    .p-select.p-disabled .p-select-label {
        color: dt('select.disabled.color');
    }

    .p-select-label-empty {
        overflow: hidden;
        opacity: 0;
    }

    input.p-select-label {
        cursor: default;
    }

    .p-select .p-select-overlay {
        min-width: 100%;
    }

    .p-select-overlay {
        position: absolute;
        top: 0;
        left: 0;
        background: dt('select.overlay.background');
        color: dt('select.overlay.color');
        border: 1px solid dt('select.overlay.border.color');
        border-radius: dt('select.overlay.border.radius');
        box-shadow: dt('select.overlay.shadow');
    }

    .p-select-header {
        padding: dt('select.list.header.padding');
    }

    .p-select-filter {
        width: 100%;
    }

    .p-select-list-container {
        overflow: auto;
    }

    .p-select-option-group {
        cursor: auto;
        margin: 0;
        padding: dt('select.option.group.padding');
        background: dt('select.option.group.background');
        color: dt('select.option.group.color');
        font-weight: dt('select.option.group.font.weight');
    }

    .p-select-list {
        margin: 0;
        padding: 0;
        list-style-type: none;
        padding: dt('select.list.padding');
        gap: dt('select.list.gap');
        display: flex;
        flex-direction: column;
    }

    .p-select-option {
        cursor: pointer;
        font-weight: normal;
        white-space: nowrap;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        padding: dt('select.option.padding');
        border: 0 none;
        color: dt('select.option.color');
        background: transparent;
        transition:
            background dt('select.transition.duration'),
            color dt('select.transition.duration'),
            border-color dt('select.transition.duration'),
            box-shadow dt('select.transition.duration'),
            outline-color dt('select.transition.duration');
        border-radius: dt('select.option.border.radius');
    }

    .p-select-option:not(.p-select-option-selected):not(.p-disabled).p-focus {
        background: dt('select.option.focus.background');
        color: dt('select.option.focus.color');
    }

    .p-select-option.p-select-option-selected {
        background: dt('select.option.selected.background');
        color: dt('select.option.selected.color');
    }

    .p-select-option.p-select-option-selected.p-focus {
        background: dt('select.option.selected.focus.background');
        color: dt('select.option.selected.focus.color');
    }

    .p-select-option-blank-icon {
        flex-shrink: 0;
    }

    .p-select-option-check-icon {
        position: relative;
        flex-shrink: 0;
        margin-inline-start: dt('select.checkmark.gutter.start');
        margin-inline-end: dt('select.checkmark.gutter.end');
        color: dt('select.checkmark.color');
    }

    .p-select-empty-message {
        padding: dt('select.empty.message.padding');
    }

    .p-select-fluid {
        display: flex;
        width: 100%;
    }

    .p-select-sm .p-select-label {
        font-size: dt('select.sm.font.size');
        padding-block: dt('select.sm.padding.y');
        padding-inline: dt('select.sm.padding.x');
    }

    .p-select-sm .p-select-dropdown .p-icon {
        font-size: dt('select.sm.font.size');
        width: dt('select.sm.font.size');
        height: dt('select.sm.font.size');
    }

    .p-select-lg .p-select-label {
        font-size: dt('select.lg.font.size');
        padding-block: dt('select.lg.padding.y');
        padding-inline: dt('select.lg.padding.x');
    }

    .p-select-lg .p-select-dropdown .p-icon {
        font-size: dt('select.lg.font.size');
        width: dt('select.lg.font.size');
        height: dt('select.lg.font.size');
    }
`;
var style$a = css`
    .p-togglebutton {
        display: inline-flex;
        cursor: pointer;
        user-select: none;
        overflow: hidden;
        position: relative;
        color: dt('togglebutton.color');
        background: dt('togglebutton.background');
        border: 1px solid dt('togglebutton.border.color');
        padding: dt('togglebutton.padding');
        font-size: 1rem;
        font-family: inherit;
        font-feature-settings: inherit;
        transition:
            background dt('togglebutton.transition.duration'),
            color dt('togglebutton.transition.duration'),
            border-color dt('togglebutton.transition.duration'),
            outline-color dt('togglebutton.transition.duration'),
            box-shadow dt('togglebutton.transition.duration');
        border-radius: dt('togglebutton.border.radius');
        outline-color: transparent;
        font-weight: dt('togglebutton.font.weight');
    }

    .p-togglebutton-content {
        display: inline-flex;
        flex: 1 1 auto;
        align-items: center;
        justify-content: center;
        gap: dt('togglebutton.gap');
        padding: dt('togglebutton.content.padding');
        background: transparent;
        border-radius: dt('togglebutton.content.border.radius');
        transition:
            background dt('togglebutton.transition.duration'),
            color dt('togglebutton.transition.duration'),
            border-color dt('togglebutton.transition.duration'),
            outline-color dt('togglebutton.transition.duration'),
            box-shadow dt('togglebutton.transition.duration');
    }

    .p-togglebutton:not(:disabled):not(.p-togglebutton-checked):hover {
        background: dt('togglebutton.hover.background');
        color: dt('togglebutton.hover.color');
    }

    .p-togglebutton.p-togglebutton-checked {
        background: dt('togglebutton.checked.background');
        border-color: dt('togglebutton.checked.border.color');
        color: dt('togglebutton.checked.color');
    }

    .p-togglebutton-checked .p-togglebutton-content {
        background: dt('togglebutton.content.checked.background');
        box-shadow: dt('togglebutton.content.checked.shadow');
    }

    .p-togglebutton:focus-visible {
        box-shadow: dt('togglebutton.focus.ring.shadow');
        outline: dt('togglebutton.focus.ring.width') dt('togglebutton.focus.ring.style') dt('togglebutton.focus.ring.color');
        outline-offset: dt('togglebutton.focus.ring.offset');
    }

    .p-togglebutton.p-invalid {
        border-color: dt('togglebutton.invalid.border.color');
    }

    .p-togglebutton:disabled {
        opacity: 1;
        cursor: default;
        background: dt('togglebutton.disabled.background');
        border-color: dt('togglebutton.disabled.border.color');
        color: dt('togglebutton.disabled.color');
    }

    .p-togglebutton-label,
    .p-togglebutton-icon {
        position: relative;
        transition: none;
    }

    .p-togglebutton-icon {
        color: dt('togglebutton.icon.color');
    }

    .p-togglebutton:not(:disabled):not(.p-togglebutton-checked):hover .p-togglebutton-icon {
        color: dt('togglebutton.icon.hover.color');
    }

    .p-togglebutton.p-togglebutton-checked .p-togglebutton-icon {
        color: dt('togglebutton.icon.checked.color');
    }

    .p-togglebutton:disabled .p-togglebutton-icon {
        color: dt('togglebutton.icon.disabled.color');
    }

    .p-togglebutton-sm {
        padding: dt('togglebutton.sm.padding');
        font-size: dt('togglebutton.sm.font.size');
    }

    .p-togglebutton-sm .p-togglebutton-content {
        padding: dt('togglebutton.content.sm.padding');
    }

    .p-togglebutton-lg {
        padding: dt('togglebutton.lg.padding');
        font-size: dt('togglebutton.lg.font.size');
    }

    .p-togglebutton-lg .p-togglebutton-content {
        padding: dt('togglebutton.content.lg.padding');
    }
`;
var style$9 = css`
    .p-tabs {
        display: flex;
        flex-direction: column;
    }

    .p-tablist {
        display: flex;
        position: relative;
    }

    .p-tabs-scrollable > .p-tablist {
        overflow: hidden;
    }

    .p-tablist-viewport {
        overflow-x: auto;
        overflow-y: hidden;
        scroll-behavior: smooth;
        scrollbar-width: none;
        overscroll-behavior: contain auto;
    }

    .p-tablist-viewport::-webkit-scrollbar {
        display: none;
    }

    .p-tablist-tab-list {
        position: relative;
        display: flex;
        background: dt('tabs.tablist.background');
        border-style: solid;
        border-color: dt('tabs.tablist.border.color');
        border-width: dt('tabs.tablist.border.width');
    }

    .p-tablist-content {
        flex-grow: 1;
    }

    .p-tablist-nav-button {
        all: unset;
        position: absolute !important;
        flex-shrink: 0;
        inset-block-start: 0;
        z-index: 2;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: dt('tabs.nav.button.background');
        color: dt('tabs.nav.button.color');
        width: dt('tabs.nav.button.width');
        transition:
            color dt('tabs.transition.duration'),
            outline-color dt('tabs.transition.duration'),
            box-shadow dt('tabs.transition.duration');
        box-shadow: dt('tabs.nav.button.shadow');
        outline-color: transparent;
        cursor: pointer;
    }

    .p-tablist-nav-button:focus-visible {
        z-index: 1;
        box-shadow: dt('tabs.nav.button.focus.ring.shadow');
        outline: dt('tabs.nav.button.focus.ring.width') dt('tabs.nav.button.focus.ring.style') dt('tabs.nav.button.focus.ring.color');
        outline-offset: dt('tabs.nav.button.focus.ring.offset');
    }

    .p-tablist-nav-button:hover {
        color: dt('tabs.nav.button.hover.color');
    }

    .p-tablist-prev-button {
        inset-inline-start: 0;
    }

    .p-tablist-next-button {
        inset-inline-end: 0;
    }

    .p-tablist-prev-button:dir(rtl),
    .p-tablist-next-button:dir(rtl) {
        transform: rotate(180deg);
    }

    .p-tab {
        flex-shrink: 0;
        cursor: pointer;
        user-select: none;
        position: relative;
        border-style: solid;
        white-space: nowrap;
        gap: dt('tabs.tab.gap');
        background: dt('tabs.tab.background');
        border-width: dt('tabs.tab.border.width');
        border-color: dt('tabs.tab.border.color');
        color: dt('tabs.tab.color');
        padding: dt('tabs.tab.padding');
        font-weight: dt('tabs.tab.font.weight');
        transition:
            background dt('tabs.transition.duration'),
            border-color dt('tabs.transition.duration'),
            color dt('tabs.transition.duration'),
            outline-color dt('tabs.transition.duration'),
            box-shadow dt('tabs.transition.duration');
        margin: dt('tabs.tab.margin');
        outline-color: transparent;
    }

    .p-tab:not(.p-disabled):focus-visible {
        z-index: 1;
        box-shadow: dt('tabs.tab.focus.ring.shadow');
        outline: dt('tabs.tab.focus.ring.width') dt('tabs.tab.focus.ring.style') dt('tabs.tab.focus.ring.color');
        outline-offset: dt('tabs.tab.focus.ring.offset');
    }

    .p-tab:not(.p-tab-active):not(.p-disabled):hover {
        background: dt('tabs.tab.hover.background');
        border-color: dt('tabs.tab.hover.border.color');
        color: dt('tabs.tab.hover.color');
    }

    .p-tab-active {
        background: dt('tabs.tab.active.background');
        border-color: dt('tabs.tab.active.border.color');
        color: dt('tabs.tab.active.color');
    }

    .p-tabpanels {
        background: dt('tabs.tabpanel.background');
        color: dt('tabs.tabpanel.color');
        padding: dt('tabs.tabpanel.padding');
        outline: 0 none;
    }

    .p-tabpanel:focus-visible {
        box-shadow: dt('tabs.tabpanel.focus.ring.shadow');
        outline: dt('tabs.tabpanel.focus.ring.width') dt('tabs.tabpanel.focus.ring.style') dt('tabs.tabpanel.focus.ring.color');
        outline-offset: dt('tabs.tabpanel.focus.ring.offset');
    }

    .p-tablist-active-bar {
        z-index: 1;
        display: block;
        position: absolute;
        inset-block-end: dt('tabs.active.bar.bottom');
        height: dt('tabs.active.bar.height');
        background: dt('tabs.active.bar.background');
        transition: 250ms cubic-bezier(0.35, 0, 0.25, 1);
    }
`;
var style$8 = css`
    .p-toast {
        width: dt('toast.width');
        white-space: pre-line;
        word-break: break-word;
    }

    .p-toast-message {
        margin: 0 0 1rem 0;
    }

    .p-toast-message-icon {
        flex-shrink: 0;
        font-size: dt('toast.icon.size');
        width: dt('toast.icon.size');
        height: dt('toast.icon.size');
    }

    .p-toast-message-content {
        display: flex;
        align-items: flex-start;
        padding: dt('toast.content.padding');
        gap: dt('toast.content.gap');
    }

    .p-toast-message-text {
        flex: 1 1 auto;
        display: flex;
        flex-direction: column;
        gap: dt('toast.text.gap');
    }

    .p-toast-summary {
        font-weight: dt('toast.summary.font.weight');
        font-size: dt('toast.summary.font.size');
    }

    .p-toast-detail {
        font-weight: dt('toast.detail.font.weight');
        font-size: dt('toast.detail.font.size');
    }

    .p-toast-close-button {
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
        cursor: pointer;
        background: transparent;
        transition:
            background dt('toast.transition.duration'),
            color dt('toast.transition.duration'),
            outline-color dt('toast.transition.duration'),
            box-shadow dt('toast.transition.duration');
        outline-color: transparent;
        color: inherit;
        width: dt('toast.close.button.width');
        height: dt('toast.close.button.height');
        border-radius: dt('toast.close.button.border.radius');
        margin: -25% 0 0 0;
        right: -25%;
        padding: 0;
        border: none;
        user-select: none;
    }

    .p-toast-close-button:dir(rtl) {
        margin: -25% 0 0 auto;
        left: -25%;
        right: auto;
    }

    .p-toast-message-info,
    .p-toast-message-success,
    .p-toast-message-warn,
    .p-toast-message-error,
    .p-toast-message-secondary,
    .p-toast-message-contrast {
        border-width: dt('toast.border.width');
        border-style: solid;
        backdrop-filter: blur(dt('toast.blur'));
        border-radius: dt('toast.border.radius');
    }

    .p-toast-close-icon {
        font-size: dt('toast.close.icon.size');
        width: dt('toast.close.icon.size');
        height: dt('toast.close.icon.size');
    }

    .p-toast-close-button:focus-visible {
        outline-width: dt('focus.ring.width');
        outline-style: dt('focus.ring.style');
        outline-offset: dt('focus.ring.offset');
    }

    .p-toast-message-info {
        background: dt('toast.info.background');
        border-color: dt('toast.info.border.color');
        color: dt('toast.info.color');
        box-shadow: dt('toast.info.shadow');
    }

    .p-toast-message-info .p-toast-detail {
        color: dt('toast.info.detail.color');
    }

    .p-toast-message-info .p-toast-close-button:focus-visible {
        outline-color: dt('toast.info.close.button.focus.ring.color');
        box-shadow: dt('toast.info.close.button.focus.ring.shadow');
    }

    .p-toast-message-info .p-toast-close-button:hover {
        background: dt('toast.info.close.button.hover.background');
    }

    .p-toast-message-success {
        background: dt('toast.success.background');
        border-color: dt('toast.success.border.color');
        color: dt('toast.success.color');
        box-shadow: dt('toast.success.shadow');
    }

    .p-toast-message-success .p-toast-detail {
        color: dt('toast.success.detail.color');
    }

    .p-toast-message-success .p-toast-close-button:focus-visible {
        outline-color: dt('toast.success.close.button.focus.ring.color');
        box-shadow: dt('toast.success.close.button.focus.ring.shadow');
    }

    .p-toast-message-success .p-toast-close-button:hover {
        background: dt('toast.success.close.button.hover.background');
    }

    .p-toast-message-warn {
        background: dt('toast.warn.background');
        border-color: dt('toast.warn.border.color');
        color: dt('toast.warn.color');
        box-shadow: dt('toast.warn.shadow');
    }

    .p-toast-message-warn .p-toast-detail {
        color: dt('toast.warn.detail.color');
    }

    .p-toast-message-warn .p-toast-close-button:focus-visible {
        outline-color: dt('toast.warn.close.button.focus.ring.color');
        box-shadow: dt('toast.warn.close.button.focus.ring.shadow');
    }

    .p-toast-message-warn .p-toast-close-button:hover {
        background: dt('toast.warn.close.button.hover.background');
    }

    .p-toast-message-error {
        background: dt('toast.error.background');
        border-color: dt('toast.error.border.color');
        color: dt('toast.error.color');
        box-shadow: dt('toast.error.shadow');
    }

    .p-toast-message-error .p-toast-detail {
        color: dt('toast.error.detail.color');
    }

    .p-toast-message-error .p-toast-close-button:focus-visible {
        outline-color: dt('toast.error.close.button.focus.ring.color');
        box-shadow: dt('toast.error.close.button.focus.ring.shadow');
    }

    .p-toast-message-error .p-toast-close-button:hover {
        background: dt('toast.error.close.button.hover.background');
    }

    .p-toast-message-secondary {
        background: dt('toast.secondary.background');
        border-color: dt('toast.secondary.border.color');
        color: dt('toast.secondary.color');
        box-shadow: dt('toast.secondary.shadow');
    }

    .p-toast-message-secondary .p-toast-detail {
        color: dt('toast.secondary.detail.color');
    }

    .p-toast-message-secondary .p-toast-close-button:focus-visible {
        outline-color: dt('toast.secondary.close.button.focus.ring.color');
        box-shadow: dt('toast.secondary.close.button.focus.ring.shadow');
    }

    .p-toast-message-secondary .p-toast-close-button:hover {
        background: dt('toast.secondary.close.button.hover.background');
    }

    .p-toast-message-contrast {
        background: dt('toast.contrast.background');
        border-color: dt('toast.contrast.border.color');
        color: dt('toast.contrast.color');
        box-shadow: dt('toast.contrast.shadow');
    }

    .p-toast-message-contrast .p-toast-detail {
        color: dt('toast.contrast.detail.color');
    }

    .p-toast-message-contrast .p-toast-close-button:focus-visible {
        outline-color: dt('toast.contrast.close.button.focus.ring.color');
        box-shadow: dt('toast.contrast.close.button.focus.ring.shadow');
    }

    .p-toast-message-contrast .p-toast-close-button:hover {
        background: dt('toast.contrast.close.button.hover.background');
    }

    .p-toast-top-center {
        transform: translateX(-50%);
    }

    .p-toast-bottom-center {
        transform: translateX(-50%);
    }

    .p-toast-center {
        min-width: 20vw;
        transform: translate(-50%, -50%);
    }

    .p-toast-message-enter-from {
        opacity: 0;
        transform: translateY(50%);
    }

    .p-toast-message-leave-from {
        max-height: 1000px;
    }

    .p-toast .p-toast-message.p-toast-message-leave-to {
        max-height: 0;
        opacity: 0;
        margin-bottom: 0;
        overflow: hidden;
    }

    .p-toast-message-enter-active {
        transition:
            transform 0.3s,
            opacity 0.3s;
    }

    .p-toast-message-leave-active {
        transition:
            max-height 0.45s cubic-bezier(0, 1, 0, 1),
            opacity 0.3s,
            margin-bottom 0.3s;
    }
`;
var style$7 = css`
    .p-progressbar {
        position: relative;
        overflow: hidden;
        height: dt('progressbar.height');
        background: dt('progressbar.background');
        border-radius: dt('progressbar.border.radius');
    }

    .p-progressbar-value {
        margin: 0;
        background: dt('progressbar.value.background');
    }

    .p-progressbar-label {
        color: dt('progressbar.label.color');
        font-size: dt('progressbar.label.font.size');
        font-weight: dt('progressbar.label.font.weight');
    }

    .p-progressbar-determinate .p-progressbar-value {
        height: 100%;
        width: 0%;
        position: absolute;
        display: none;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        transition: width 1s ease-in-out;
    }

    .p-progressbar-determinate .p-progressbar-label {
        display: inline-flex;
    }

    .p-progressbar-indeterminate .p-progressbar-value::before {
        content: '';
        position: absolute;
        background: inherit;
        inset-block-start: 0;
        inset-inline-start: 0;
        inset-block-end: 0;
        will-change: inset-inline-start, inset-inline-end;
        animation: p-progressbar-indeterminate-anim 2.1s cubic-bezier(0.65, 0.815, 0.735, 0.395) infinite;
    }

    .p-progressbar-indeterminate .p-progressbar-value::after {
        content: '';
        position: absolute;
        background: inherit;
        inset-block-start: 0;
        inset-inline-start: 0;
        inset-block-end: 0;
        will-change: inset-inline-start, inset-inline-end;
        animation: p-progressbar-indeterminate-anim-short 2.1s cubic-bezier(0.165, 0.84, 0.44, 1) infinite;
        animation-delay: 1.15s;
    }

    @keyframes p-progressbar-indeterminate-anim {
        0% {
            inset-inline-start: -35%;
            inset-inline-end: 100%;
        }
        60% {
            inset-inline-start: 100%;
            inset-inline-end: -90%;
        }
        100% {
            inset-inline-start: 100%;
            inset-inline-end: -90%;
        }
    }
    @-webkit-keyframes p-progressbar-indeterminate-anim {
        0% {
            inset-inline-start: -35%;
            inset-inline-end: 100%;
        }
        60% {
            inset-inline-start: 100%;
            inset-inline-end: -90%;
        }
        100% {
            inset-inline-start: 100%;
            inset-inline-end: -90%;
        }
    }

    @keyframes p-progressbar-indeterminate-anim-short {
        0% {
            inset-inline-start: -200%;
            inset-inline-end: 100%;
        }
        60% {
            inset-inline-start: 107%;
            inset-inline-end: -8%;
        }
        100% {
            inset-inline-start: 107%;
            inset-inline-end: -8%;
        }
    }
    @-webkit-keyframes p-progressbar-indeterminate-anim-short {
        0% {
            inset-inline-start: -200%;
            inset-inline-end: 100%;
        }
        60% {
            inset-inline-start: 107%;
            inset-inline-end: -8%;
        }
        100% {
            inset-inline-start: 107%;
            inset-inline-end: -8%;
        }
    }
`;
var style$6 = css`
    .p-fileupload input[type='file'] {
        display: none;
    }

    .p-fileupload-advanced {
        border: 1px solid dt('fileupload.border.color');
        border-radius: dt('fileupload.border.radius');
        background: dt('fileupload.background');
        color: dt('fileupload.color');
    }

    .p-fileupload-header {
        display: flex;
        align-items: center;
        padding: dt('fileupload.header.padding');
        background: dt('fileupload.header.background');
        color: dt('fileupload.header.color');
        border-style: solid;
        border-width: dt('fileupload.header.border.width');
        border-color: dt('fileupload.header.border.color');
        border-radius: dt('fileupload.header.border.radius');
        gap: dt('fileupload.header.gap');
    }

    .p-fileupload-content {
        border: 1px solid transparent;
        display: flex;
        flex-direction: column;
        gap: dt('fileupload.content.gap');
        transition: border-color dt('fileupload.transition.duration');
        padding: dt('fileupload.content.padding');
    }

    .p-fileupload-content .p-progressbar {
        width: 100%;
        height: dt('fileupload.progressbar.height');
    }

    .p-fileupload-file-list {
        display: flex;
        flex-direction: column;
        gap: dt('fileupload.filelist.gap');
    }

    .p-fileupload-file {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        padding: dt('fileupload.file.padding');
        border-block-end: 1px solid dt('fileupload.file.border.color');
        gap: dt('fileupload.file.gap');
    }

    .p-fileupload-file:last-child {
        border-block-end: 0;
    }

    .p-fileupload-file-info {
        display: flex;
        flex-direction: column;
        gap: dt('fileupload.file.info.gap');
    }

    .p-fileupload-file-thumbnail {
        flex-shrink: 0;
    }

    .p-fileupload-file-actions {
        margin-inline-start: auto;
    }

    .p-fileupload-highlight {
        border: 1px dashed dt('fileupload.content.highlight.border.color');
    }

    .p-fileupload-basic {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: center;
        gap: dt('fileupload.basic.gap');
    }
`;
var style$5 = css`
    .p-divider-horizontal {
        display: flex;
        width: 100%;
        position: relative;
        align-items: center;
        margin: dt('divider.horizontal.margin');
        padding: dt('divider.horizontal.padding');
    }

    .p-divider-horizontal:before {
        position: absolute;
        display: block;
        inset-block-start: 50%;
        inset-inline-start: 0;
        width: 100%;
        content: '';
        border-block-start: 1px solid dt('divider.border.color');
    }

    .p-divider-horizontal .p-divider-content {
        padding: dt('divider.horizontal.content.padding');
    }

    .p-divider-vertical {
        min-height: 100%;
        display: flex;
        position: relative;
        justify-content: center;
        margin: dt('divider.vertical.margin');
        padding: dt('divider.vertical.padding');
    }

    .p-divider-vertical:before {
        position: absolute;
        display: block;
        inset-block-start: 0;
        inset-inline-start: 50%;
        height: 100%;
        content: '';
        border-inline-start: 1px solid dt('divider.border.color');
    }

    .p-divider.p-divider-vertical .p-divider-content {
        padding: dt('divider.vertical.content.padding');
    }

    .p-divider-content {
        z-index: 1;
        background: dt('divider.content.background');
        color: dt('divider.content.color');
    }

    .p-divider-solid.p-divider-horizontal:before {
        border-block-start-style: solid;
    }

    .p-divider-solid.p-divider-vertical:before {
        border-inline-start-style: solid;
    }

    .p-divider-dashed.p-divider-horizontal:before {
        border-block-start-style: dashed;
    }

    .p-divider-dashed.p-divider-vertical:before {
        border-inline-start-style: dashed;
    }

    .p-divider-dotted.p-divider-horizontal:before {
        border-block-start-style: dotted;
    }

    .p-divider-dotted.p-divider-vertical:before {
        border-inline-start-style: dotted;
    }

    .p-divider-left:dir(rtl),
    .p-divider-right:dir(rtl) {
        flex-direction: row-reverse;
    }
`;
var style$4 = css`
    .p-scrollpanel-content-container {
        overflow: hidden;
        width: 100%;
        height: 100%;
        position: relative;
        z-index: 1;
        float: left;
    }

    .p-scrollpanel-content {
        height: calc(100% + calc(2 * dt('scrollpanel.bar.size')));
        width: calc(100% + calc(2 * dt('scrollpanel.bar.size')));
        padding-inline: 0 calc(2 * dt('scrollpanel.bar.size'));
        padding-block: 0 calc(2 * dt('scrollpanel.bar.size'));
        position: relative;
        overflow: auto;
        box-sizing: border-box;
        scrollbar-width: none;
    }

    .p-scrollpanel-content::-webkit-scrollbar {
        display: none;
    }

    .p-scrollpanel-bar {
        position: relative;
        border-radius: dt('scrollpanel.bar.border.radius');
        z-index: 2;
        cursor: pointer;
        opacity: 0;
        outline-color: transparent;
        background: dt('scrollpanel.bar.background');
        border: 0 none;
        transition:
            outline-color dt('scrollpanel.transition.duration'),
            opacity dt('scrollpanel.transition.duration');
    }

    .p-scrollpanel-bar:focus-visible {
        box-shadow: dt('scrollpanel.bar.focus.ring.shadow');
        outline: dt('scrollpanel.barfocus.ring.width') dt('scrollpanel.bar.focus.ring.style') dt('scrollpanel.bar.focus.ring.color');
        outline-offset: dt('scrollpanel.barfocus.ring.offset');
    }

    .p-scrollpanel-bar-y {
        width: dt('scrollpanel.bar.size');
        inset-block-start: 0;
    }

    .p-scrollpanel-bar-x {
        height: dt('scrollpanel.bar.size');
        inset-block-end: 0;
    }

    .p-scrollpanel-hidden {
        visibility: hidden;
    }

    .p-scrollpanel:hover .p-scrollpanel-bar,
    .p-scrollpanel:active .p-scrollpanel-bar {
        opacity: 1;
    }

    .p-scrollpanel-grabbed {
        user-select: none;
    }
`;
var style$3 = css`
    .p-listbox {
        background: dt('listbox.background');
        color: dt('listbox.color');
        border: 1px solid dt('listbox.border.color');
        border-radius: dt('listbox.border.radius');
        transition:
            background dt('listbox.transition.duration'),
            color dt('listbox.transition.duration'),
            border-color dt('listbox.transition.duration'),
            box-shadow dt('listbox.transition.duration'),
            outline-color dt('listbox.transition.duration');
        outline-color: transparent;
        box-shadow: dt('listbox.shadow');
    }

    .p-listbox.p-disabled {
        opacity: 1;
        background: dt('listbox.disabled.background');
        color: dt('listbox.disabled.color');
    }

    .p-listbox.p-disabled .p-listbox-option {
        color: dt('listbox.disabled.color');
    }

    .p-listbox.p-invalid {
        border-color: dt('listbox.invalid.border.color');
    }

    .p-listbox-header {
        padding: dt('listbox.list.header.padding');
    }

    .p-listbox-filter {
        width: 100%;
    }

    .p-listbox-list-container {
        overflow: auto;
    }

    .p-listbox-list {
        list-style-type: none;
        margin: 0;
        padding: dt('listbox.list.padding');
        outline: 0 none;
        display: flex;
        flex-direction: column;
        gap: dt('listbox.list.gap');
    }

    .p-listbox-option {
        display: flex;
        align-items: center;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        padding: dt('listbox.option.padding');
        border: 0 none;
        border-radius: dt('listbox.option.border.radius');
        color: dt('listbox.option.color');
        transition:
            background dt('listbox.transition.duration'),
            color dt('listbox.transition.duration'),
            border-color dt('listbox.transition.duration'),
            box-shadow dt('listbox.transition.duration'),
            outline-color dt('listbox.transition.duration');
    }

    .p-listbox-striped li:nth-child(even of .p-listbox-option) {
        background: dt('listbox.option.striped.background');
    }

    .p-listbox .p-listbox-list .p-listbox-option.p-listbox-option-selected {
        background: dt('listbox.option.selected.background');
        color: dt('listbox.option.selected.color');
    }

    .p-listbox:not(.p-disabled) .p-listbox-option.p-listbox-option-selected.p-focus {
        background: dt('listbox.option.selected.focus.background');
        color: dt('listbox.option.selected.focus.color');
    }

    .p-listbox:not(.p-disabled) .p-listbox-option:not(.p-listbox-option-selected):not(.p-disabled).p-focus {
        background: dt('listbox.option.focus.background');
        color: dt('listbox.option.focus.color');
    }

    .p-listbox:not(.p-disabled) .p-listbox-option:not(.p-listbox-option-selected):not(.p-disabled):hover {
        background: dt('listbox.option.focus.background');
        color: dt('listbox.option.focus.color');
    }

    .p-listbox-option-blank-icon {
        flex-shrink: 0;
    }

    .p-listbox-option-check-icon {
        position: relative;
        flex-shrink: 0;
        margin-inline-start: dt('listbox.checkmark.gutter.start');
        margin-inline-end: dt('listbox.checkmark.gutter.end');
        color: dt('listbox.checkmark.color');
    }

    .p-listbox-option-group {
        margin: 0;
        padding: dt('listbox.option.group.padding');
        color: dt('listbox.option.group.color');
        background: dt('listbox.option.group.background');
        font-weight: dt('listbox.option.group.font.weight');
    }

    .p-listbox-empty-message {
        padding: dt('listbox.empty.message.padding');
    }
`;
var style$2 = css`
    .p-card {
        background: dt('card.background');
        color: dt('card.color');
        box-shadow: dt('card.shadow');
        border-radius: dt('card.border.radius');
        display: flex;
        flex-direction: column;
    }

    .p-card-caption {
        display: flex;
        flex-direction: column;
        gap: dt('card.caption.gap');
    }

    .p-card-body {
        padding: dt('card.body.padding');
        display: flex;
        flex-direction: column;
        gap: dt('card.body.gap');
    }

    .p-card-title {
        font-size: dt('card.title.font.size');
        font-weight: dt('card.title.font.weight');
    }

    .p-card-subtitle {
        color: dt('card.subtitle.color');
    }
`;
var style$1 = css`
    .p-floatlabel {
        display: block;
        position: relative;
    }

    .p-floatlabel label {
        position: absolute;
        pointer-events: none;
        top: 50%;
        transform: translateY(-50%);
        transition-property: all;
        transition-timing-function: ease;
        line-height: 1;
        font-weight: dt('floatlabel.font.weight');
        inset-inline-start: dt('floatlabel.position.x');
        color: dt('floatlabel.color');
        transition-duration: dt('floatlabel.transition.duration');
    }

    .p-floatlabel:has(.p-textarea) label {
        top: dt('floatlabel.position.y');
        transform: translateY(0);
    }

    .p-floatlabel:has(.p-inputicon:first-child) label {
        inset-inline-start: calc((dt('form.field.padding.x') * 2) + dt('icon.size'));
    }

    .p-floatlabel:has(.p-invalid) label {
        color: dt('floatlabel.invalid.color');
    }

    .p-floatlabel:has(input:focus) label,
    .p-floatlabel:has(input.p-filled) label,
    .p-floatlabel:has(input:-webkit-autofill) label,
    .p-floatlabel:has(textarea:focus) label,
    .p-floatlabel:has(textarea.p-filled) label,
    .p-floatlabel:has(.p-inputwrapper-focus) label,
    .p-floatlabel:has(.p-inputwrapper-filled) label {
        top: dt('floatlabel.over.active.top');
        transform: translateY(0);
        font-size: dt('floatlabel.active.font.size');
        font-weight: dt('floatlabel.active.font.weight');
    }

    .p-floatlabel:has(input.p-filled) label,
    .p-floatlabel:has(textarea.p-filled) label,
    .p-floatlabel:has(.p-inputwrapper-filled) label {
        color: dt('floatlabel.active.color');
    }

    .p-floatlabel:has(input:focus) label,
    .p-floatlabel:has(input:-webkit-autofill) label,
    .p-floatlabel:has(textarea:focus) label,
    .p-floatlabel:has(.p-inputwrapper-focus) label {
        color: dt('floatlabel.focus.color');
    }

    .p-floatlabel-in .p-inputtext,
    .p-floatlabel-in .p-textarea,
    .p-floatlabel-in .p-select-label,
    .p-floatlabel-in .p-multiselect-label,
    .p-floatlabel-in .p-autocomplete-input-multiple,
    .p-floatlabel-in .p-cascadeselect-label,
    .p-floatlabel-in .p-treeselect-label {
        padding-block-start: dt('floatlabel.in.input.padding.top');
        padding-block-end: dt('floatlabel.in.input.padding.bottom');
    }

    .p-floatlabel-in:has(input:focus) label,
    .p-floatlabel-in:has(input.p-filled) label,
    .p-floatlabel-in:has(input:-webkit-autofill) label,
    .p-floatlabel-in:has(textarea:focus) label,
    .p-floatlabel-in:has(textarea.p-filled) label,
    .p-floatlabel-in:has(.p-inputwrapper-focus) label,
    .p-floatlabel-in:has(.p-inputwrapper-filled) label {
        top: dt('floatlabel.in.active.top');
    }

    .p-floatlabel-on:has(input:focus) label,
    .p-floatlabel-on:has(input.p-filled) label,
    .p-floatlabel-on:has(input:-webkit-autofill) label,
    .p-floatlabel-on:has(textarea:focus) label,
    .p-floatlabel-on:has(textarea.p-filled) label,
    .p-floatlabel-on:has(.p-inputwrapper-focus) label,
    .p-floatlabel-on:has(.p-inputwrapper-filled) label {
        top: 0;
        transform: translateY(-50%);
        border-radius: dt('floatlabel.on.border.radius');
        background: dt('floatlabel.on.active.background');
        padding: dt('floatlabel.on.active.padding');
    }
`;
var style = css`
    .p-textarea {
        font-family: inherit;
        font-feature-settings: inherit;
        font-size: 1rem;
        color: dt('textarea.color');
        background: dt('textarea.background');
        padding-block: dt('textarea.padding.y');
        padding-inline: dt('textarea.padding.x');
        border: 1px solid dt('textarea.border.color');
        transition:
            background dt('textarea.transition.duration'),
            color dt('textarea.transition.duration'),
            border-color dt('textarea.transition.duration'),
            outline-color dt('textarea.transition.duration'),
            box-shadow dt('textarea.transition.duration');
        appearance: none;
        border-radius: dt('textarea.border.radius');
        outline-color: transparent;
        box-shadow: dt('textarea.shadow');
    }

    .p-textarea:enabled:hover {
        border-color: dt('textarea.hover.border.color');
    }

    .p-textarea:enabled:focus {
        border-color: dt('textarea.focus.border.color');
        box-shadow: dt('textarea.focus.ring.shadow');
        outline: dt('textarea.focus.ring.width') dt('textarea.focus.ring.style') dt('textarea.focus.ring.color');
        outline-offset: dt('textarea.focus.ring.offset');
    }

    .p-textarea.p-invalid {
        border-color: dt('textarea.invalid.border.color');
    }

    .p-textarea.p-variant-filled {
        background: dt('textarea.filled.background');
    }

    .p-textarea.p-variant-filled:enabled:hover {
        background: dt('textarea.filled.hover.background');
    }

    .p-textarea.p-variant-filled:enabled:focus {
        background: dt('textarea.filled.focus.background');
    }

    .p-textarea:disabled {
        opacity: 1;
        background: dt('textarea.disabled.background');
        color: dt('textarea.disabled.color');
    }

    .p-textarea::placeholder {
        color: dt('textarea.placeholder.color');
    }

    .p-textarea.p-invalid::placeholder {
        color: dt('textarea.invalid.placeholder.color');
    }

    .p-textarea-fluid {
        width: 100%;
    }

    .p-textarea-resizable {
        overflow: hidden;
        resize: none;
    }

    .p-textarea-sm {
        font-size: dt('textarea.sm.font.size');
        padding-block: dt('textarea.sm.padding.y');
        padding-inline: dt('textarea.sm.padding.x');
    }

    .p-textarea-lg {
        font-size: dt('textarea.lg.font.size');
        padding-block: dt('textarea.lg.padding.y');
        padding-inline: dt('textarea.lg.padding.x');
    }
`;
export {
  blockBodyScroll as $,
  mergeKeys as A,
  style$q as B,
  getAttribute as C,
  isTouchDevice as D,
  EventBus as E,
  fadeIn as F,
  createElement as G,
  getWindowScrollLeft as H,
  getWindowScrollTop as I,
  getOuterWidth as J,
  getOuterHeight as K,
  getViewport as L,
  removeClass as M,
  addClass as N,
  hasClass as O,
  style$p as P,
  cn as Q,
  style$o as R,
  getHeight as S,
  getWidth as T,
  getOffset as U,
  style$n as V,
  focus as W,
  getFirstFocusableElement as X,
  getLastFocusableElement as Y,
  ZIndex as Z,
  isFocusableElement as _,
  setAttribute as a,
  $dt as a0,
  unblockBodyScroll as a1,
  style$m as a2,
  addStyle as a3,
  style$l as a4,
  isRTL as a5,
  style$k as a6,
  isPrintableCharacter as a7,
  getHiddenElementOuterWidth as a8,
  getHiddenElementOuterHeight as a9,
  style$2 as aA,
  style$1 as aB,
  style as aC,
  zodResolver as aD,
  findLastIndex as aa,
  nestedPosition as ab,
  style$j as ac,
  style$i as ad,
  style$h as ae,
  style$g as af,
  style$f as ag,
  style$e as ah,
  contains as ai,
  find as aj,
  style$d as ak,
  style$c as al,
  isVisible as am,
  style$b as an,
  isAndroid as ao,
  relativePosition as ap,
  absolutePosition as aq,
  getFocusableElements as ar,
  style$a as as,
  style$9 as at,
  style$8 as au,
  style$7 as av,
  style$6 as aw,
  style$5 as ax,
  style$4 as ay,
  style$3 as az,
  isClient as b,
  style$r as c,
  isNotEmpty$1 as d,
  config_default as e,
  dt as f,
  getScrollableParents as g,
  isObject$1 as h,
  isExist as i,
  getKeyValue as j,
  isString as k,
  service_default as l,
  minifyCSS as m,
  toCapitalCase as n,
  isFunction as o,
  isArray as p,
  isEmpty$1 as q,
  resolve as r,
  setAttributes as s,
  toFlatCase as t,
  uuid as u,
  resolveFieldData as v,
  removeAccents as w,
  equals as x,
  findSingle as y,
  isElement as z
};
