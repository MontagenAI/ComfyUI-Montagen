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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.OpenCVBuilder = void 0;
const utils = __importStar(require("./utils.js"));
const fs_1 = __importDefault(require("fs"));
const npmlog_1 = __importDefault(require("npmlog"));
const getLibsFactory_js_1 = require("./getLibsFactory.js");
const setupOpencv_js_1 = require("./setupOpencv.js");
const constants_js_1 = require("./constants.js");
const OpenCVBuildEnv_js_1 = __importDefault(require("./OpenCVBuildEnv.js"));
const misc_js_1 = require("./misc.js");
class OpenCVBuilder {
    constructor(opts) {
        if (Array.isArray(opts)) {
            opts = (0, misc_js_1.args2Option)(opts);
            if (opts.extra && (opts.extra.help || opts.extra.h)) {
                console.log('npm-opencv-build usage:');
                console.log((0, misc_js_1.genHelp)());
                process.exit(1);
            }
        }
        if (opts instanceof OpenCVBuildEnv_js_1.default) {
            this.env = opts;
        }
        else {
            this.env = new OpenCVBuildEnv_js_1.default(opts);
        }
        if (!this.env.prebuild)
            npmlog_1.default.info('init', `${utils.highlight("Workdir")} will be: ${utils.formatNumber("%s")}`, this.env.opencvRoot);
        this.constant = new constants_js_1.Constant(this);
        this.getLibs = new getLibsFactory_js_1.getLibsFactory(this);
    }
    checkInstalledLibs(autoBuildFile) {
        let hasLibs = true;
        npmlog_1.default.info('install', 'checking for opencv libraries');
        if (!fs_1.default.existsSync(this.env.opencvLibDir)) {
            npmlog_1.default.info('install', 'library dir does not exist:', this.env.opencvLibDir);
            return false;
        }
        const installedLibs = this.getLibs.getLibs();
        autoBuildFile.modules.forEach(({ opencvModule, libPath }) => {
            if (!libPath) {
                npmlog_1.default.info('install', '%s: %s', opencvModule, 'ignored');
                return;
            }
            const foundLib = installedLibs.find(lib => lib.opencvModule === opencvModule);
            hasLibs = hasLibs && !!foundLib;
            npmlog_1.default.info('install', `lib ${utils.formatNumber("%s")}: ${utils.light("%s")}`, opencvModule, foundLib ? foundLib.libPath : 'not found');
        });
        return hasLibs;
    }
    async install() {
        let time = Date.now();
        // if project directory has a package.json containing opencv4nodejs variables
        // apply these variables to the process environment
        // this.env.applyEnvsFromPackageJson()
        if (this.env.isAutoBuildDisabled) {
            npmlog_1.default.info('install', `${utils.highlight('OPENCV4NODEJS_DISABLE_AUTOBUILD')} is set skipping auto build...`);
            const setup = new setupOpencv_js_1.SetupOpencv(this);
            setup.writeAutoBuildFile(true);
            setup.linkBuild();
            return;
        }
        npmlog_1.default.info('install', `if you want to use an own OpenCV build set ${utils.highlight('OPENCV4NODEJS_DISABLE_AUTOBUILD')} to 1, and fill ${misc_js_1.OPENCV_PATHS_ENV.map(utils.highlight).join(', ')} environement variables`);
        // prevent rebuild on every install
        const autoBuildFile = this.env.readAutoBuildFile();
        if (autoBuildFile) {
            npmlog_1.default.info('install', `found previous build summery auto-build.json: ${utils.highlight(this.env.autoBuildFile)}`);
            if (autoBuildFile.opencvVersion !== this.env.opencvVersion) {
                // can no longer occure with this version of opencv4nodejs-builder
                npmlog_1.default.info('install', `auto build opencv version is ${autoBuildFile.opencvVersion}, but AUTOBUILD_OPENCV_VERSION=${this.env.opencvVersion}, Will rebuild`);
            }
            else if (autoBuildFile.autoBuildFlags !== this.env.autoBuildFlags) {
                // should no longer occure since -MD5(autoBuildFlags) is append to build path
                npmlog_1.default.info('install', `auto build flags are ${autoBuildFile.autoBuildFlags}, but AUTOBUILD_FLAGS is ${this.env.autoBuildFlags}, Will rebuild`);
            }
            else {
                const hasLibs = this.checkInstalledLibs(autoBuildFile);
                if (hasLibs) {
                    npmlog_1.default.info('install', `all libraries are installed in ${utils.highlight(this.env.opencvLibDir)} => ${utils.highlight('Skip building')}`);
                    return;
                }
                else {
                    npmlog_1.default.info('install', 'missing some libraries');
                }
            }
        }
        else {
            // log.info('install', `failed to find auto-build.json: ${this.env.autoBuildFile}`)
        }
        npmlog_1.default.info('install', '');
        npmlog_1.default.info('install', 'running install script...');
        npmlog_1.default.info('install', '');
        npmlog_1.default.info('install', `opencv version: ${utils.formatNumber('%s')}`, this.env.opencvVersion);
        npmlog_1.default.info('install', `with opencv contrib: ${utils.formatNumber('%s')}`, this.env.isWithoutContrib ? 'no' : 'yes');
        npmlog_1.default.info('install', `custom build flags: ${utils.formatNumber('%s')}`, this.env.autoBuildFlags || '< none >');
        npmlog_1.default.info('install', '');
        try {
            await utils.requireGit();
            await utils.requireCmake();
            const setup = new setupOpencv_js_1.SetupOpencv(this);
            await setup.start();
            time = (Date.now() - time);
            const date = new Date(time);
            const timeString = date.toISOString().substring(11, 19);
            npmlog_1.default.info('install', `Total Build Time: ${utils.formatNumber(timeString)}`);
        }
        catch (err) {
            if (err.toString)
                npmlog_1.default.error('install', err.toString());
            else
                npmlog_1.default.error('install', JSON.stringify(err));
            process.exit(1);
        }
    }
}
exports.OpenCVBuilder = OpenCVBuilder;
exports.default = OpenCVBuilder;
//# sourceMappingURL=OpenCVBuilder.js.map