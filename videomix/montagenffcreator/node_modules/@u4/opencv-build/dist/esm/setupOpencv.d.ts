import { OpenCVBuilder } from './OpenCVBuilder.js';
import type { AutoBuildFile } from './types.js';
export declare class SetupOpencv {
    private readonly builder;
    constructor(builder: OpenCVBuilder);
    private getMsbuildCmd;
    private runBuildCmd;
    private getWinCmakeFlags;
    private getCmakeArgs;
    private getMsbuildIfWin;
    /**
     * Write Build Context to disk, to avoid further rebuild
     * @returns AutoBuildFile
     */
    writeAutoBuildFile(overwrite: boolean, buildLog?: string): AutoBuildFile;
    /**
     * add a sym link named latest to the current build.
     */
    linkBuild(): void;
    private execLog;
    /**
     * clone OpenCV repo
     * build OpenCV
     * delete source files
     */
    start(): Promise<void>;
}
