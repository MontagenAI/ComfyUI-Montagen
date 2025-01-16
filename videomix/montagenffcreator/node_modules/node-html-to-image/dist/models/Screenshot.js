"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Screenshot = void 0;
class Screenshot {
    constructor(params) {
        if (!params || !params.html) {
            throw Error("You must provide an html property.");
        }
        const { html, encoding, transparent = false, output, content, selector = "body", quality = 80, type = "png", } = params;
        this.html = html;
        this.encoding = encoding;
        this.transparent = transparent;
        this.type = type;
        this.output = output;
        this.content = isEmpty(content) ? undefined : content;
        this.selector = selector;
        this.quality = type === "jpeg" ? quality : undefined;
    }
    setHTML(html) {
        if (!html) {
            throw Error("You must provide an html property.");
        }
        this.html = html;
    }
    setBuffer(buffer) {
        this.buffer = buffer;
    }
}
exports.Screenshot = Screenshot;
function isEmpty(val) {
    return val == null || !Object.keys(val).length;
}
