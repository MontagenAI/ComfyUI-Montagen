import { OpenCVBuilder } from "./OpenCVBuilder.js";
export declare class Constant {
    private readonly builder;
    constructor(builder: OpenCVBuilder);
    opencvRepoUrl: string;
    opencvContribRepoUrl: string;
    cmakeVsCompilers: {
        [version: string]: string;
    };
    cmakeArchs: {
        [arch: string]: string;
    };
}
