/// <reference types="node" />
import { AutoBuildFile, EnvSummery } from './types.js';
import { OpenCVBuildEnvParams, OpenCVBuildEnvParamsBool, OpenCVBuildEnvParamsString, OpencvModulesType } from './misc.js';
export default class OpenCVBuildEnv implements OpenCVBuildEnvParamsBool, OpenCVBuildEnvParamsString {
    #private;
    private opts;
    prebuild?: 'latestBuild' | 'latestVersion' | 'oldestBuild' | 'oldestVersion';
    /**
     * set using env OPENCV4NODEJS_AUTOBUILD_OPENCV_VERSION , or --version or autoBuildOpencvVersion option in package.json
     */
    opencvVersion: string;
    /**
     * set using env OPENCV4NODEJS_BUILD_CUDA , or --cuda or autoBuildBuildCuda option in package.json
     */
    buildWithCuda: boolean;
    get cudaArch(): string;
    /**
     * set using env OPENCV4NODEJS_AUTOBUILD_WITHOUT_CONTRIB, or --nocontrib arg, or autoBuildWithoutContrib option in package.json
     */
    isWithoutContrib: boolean;
    /**
     * set using env OPENCV4NODEJS_DISABLE_AUTOBUILD, or --nobuild arg or disableAutoBuild option in package.json
     */
    isAutoBuildDisabled: boolean;
    /**
     * set using --keepsources arg or keepsources option in package.json
     */
    keepsources: boolean;
    /**
     * set using --dry-run arg or dry-run option in package.json
     */
    dryRun: boolean;
    gitCache: boolean;
    autoBuildFlags: string;
    rootcwd: string;
    buildRoot: string;
    packageRoot: string;
    protected _platform: NodeJS.Platform;
    private no_autobuild;
    /**
     * Find the proper root dir, this directory will contains all openCV source code and a subfolder per build
     * @param opts
     * @returns
     */
    static getBuildDir(opts?: OpenCVBuildEnvParams): string;
    /**
     * list existing build in the diven directory
     * @param rootDir build directory
     * @returns builds list
     */
    static listBuild(rootDir: string): Array<{
        autobuild: string;
        buildInfo: AutoBuildFile;
        dir: string;
        hash: string;
        date: Date;
    }>;
    /**
     * Read a parse an existing autoBuildFile
     * @param autoBuildFile file path
     * @returns
     */
    static readAutoBuildFile(autoBuildFile: string, quiet?: boolean): AutoBuildFile | undefined;
    /**
     * autodetect path using common values.
     * @return number of updated env variable from 0 to 3
     */
    static autoLocatePrebuild(): {
        changes: number;
        summery: string[];
    };
    private getExpectedVersion;
    private resolveValue;
    constructor(opts?: OpenCVBuildEnvParams);
    /**
     * complet initialisation.
     */
    private getReady;
    get enabledModules(): OpencvModulesType[];
    enableModule(mod: OpencvModulesType): void;
    disableModule(mod: OpencvModulesType): void;
    /**
     * @returns return cmake flags like: -DBUILD_opencv_modules=ON ...
     */
    getCmakeBuildFlags(): string[];
    getSharedCmakeFlags(): string[];
    private getConfiguredCmakeFlagsOnce;
    getConfiguredCmakeFlags(): string[];
    dumpEnv(): EnvSummery;
    private static getPackageJson;
    /**
     * extract opencv4nodejs section from package.json if available
     */
    private static parsePackageJson;
    numberOfCoresAvailable(): number;
    private static readEnvsFromPackageJsonLog;
    /**
     * get opencv4nodejs section from package.json if available
     * @returns opencv4nodejs customs
     */
    static readEnvsFromPackageJson(): {
        [key: string]: string | boolean | number;
    } | null;
    private hash;
    /**
     * openCV uniq version prostfix, used to avoid build path colision.
     */
    get optHash(): string;
    get platform(): NodeJS.Platform;
    get isWin(): boolean;
    get rootDir(): string;
    get opencvRoot(): string;
    get opencvGitCache(): string;
    get opencvContribGitCache(): string;
    get opencvSrc(): string;
    get opencvContribSrc(): string;
    get opencvContribModules(): string;
    get opencvBuild(): string;
    get opencvInclude(): string;
    get opencv4Include(): string;
    get opencvIncludeDir(): string;
    get opencvLibDir(): string;
    get opencvBinDir(): string;
    get autoBuildFile(): string;
    get autoBuildLog(): string;
    readAutoBuildFile(): AutoBuildFile | undefined;
}
