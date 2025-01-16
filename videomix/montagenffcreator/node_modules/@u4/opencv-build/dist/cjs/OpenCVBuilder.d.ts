import { getLibsFactory } from './getLibsFactory.js';
import { Constant } from './constants.js';
import OpenCVBuildEnv from './OpenCVBuildEnv.js';
import { OpenCVBuildEnvParams } from './misc.js';
export declare class OpenCVBuilder {
    readonly constant: Constant;
    readonly getLibs: getLibsFactory;
    readonly env: OpenCVBuildEnv;
    constructor(opts?: OpenCVBuildEnv | OpenCVBuildEnvParams | string[]);
    private checkInstalledLibs;
    install(): Promise<void>;
}
export default OpenCVBuilder;
