"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.makeScreenshot = void 0;
const handlebars_1 = __importStar(require("handlebars"));
function makeScreenshot(page, { screenshot, beforeScreenshot, waitUntil = "networkidle0", timeout, handlebarsHelpers, }) {
    return __awaiter(this, void 0, void 0, function* () {
        page.setDefaultTimeout(timeout);
        const hasHelpers = handlebarsHelpers && typeof handlebarsHelpers === "object";
        if (hasHelpers) {
            if (Object.values(handlebarsHelpers).every((h) => typeof h === "function")) {
                handlebars_1.default.registerHelper(handlebarsHelpers);
            }
            else {
                throw Error("Some helper is not a valid function");
            }
        }
        if ((screenshot === null || screenshot === void 0 ? void 0 : screenshot.content) || hasHelpers) {
            const template = (0, handlebars_1.compile)(screenshot.html);
            screenshot.setHTML(template(screenshot.content));
        }
        yield page.setContent(screenshot.html, { waitUntil });
        const element = yield page.$(screenshot.selector);
        if (!element) {
            throw Error("No element matches selector: " + screenshot.selector);
        }
        if (isFunction(beforeScreenshot)) {
            yield beforeScreenshot(page);
        }
        const buffer = yield element.screenshot({
            path: screenshot.output,
            type: screenshot.type,
            omitBackground: screenshot.transparent,
            encoding: screenshot.encoding,
            quality: screenshot.quality,
        });
        screenshot.setBuffer(buffer);
        return screenshot;
    });
}
exports.makeScreenshot = makeScreenshot;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function isFunction(f) {
    return f && typeof f === "function";
}
