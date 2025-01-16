/// <reference types="node" />
import { ImageType, Encoding, Content, ScreenshotParams } from "../types";
export declare class Screenshot {
    output: string;
    content: Content;
    selector: string;
    html: string;
    quality?: number;
    buffer?: Buffer | string;
    type?: ImageType;
    encoding?: Encoding;
    transparent?: boolean;
    constructor(params: ScreenshotParams);
    setHTML(html: string): void;
    setBuffer(buffer: Buffer | string): void;
}
