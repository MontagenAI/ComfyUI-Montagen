"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.findMSBuild = void 0;
const npmlog_1 = __importDefault(require("npmlog"));
const utils_js_1 = require("./utils.js");
const tiny_glob_1 = __importDefault(require("@u4/tiny-glob"));
const path_1 = __importDefault(require("path"));
/**
 * @returns all MSBuild.exe version in PROGRAM FILES most recent first.
 */
async function findMSBuild() {
    const progFiles = new Set([process.env.programfiles, process.env.ProgramW6432, process.env['programfiles(x86)']]);
    const matches = [];
    for (const progFile of progFiles) {
        if (progFile) {
            const reg = `${progFile.replace(/\\/g, '/')}/Microsoft Visual Studio/*/*/MSBuild/*/Bin/MSBuild.exe`;
            for (const m of await (0, tiny_glob_1.default)(reg, {}))
                matches.push(path_1.default.resolve(m));
        }
    }
    matches.sort();
    if (!matches.length) {
        return Promise.reject('no Microsoft Visual Studio found in program files directorys');
    }
    if (matches.length > 1) {
        npmlog_1.default.warn('find-msbuild', `find ${(0, utils_js_1.formatNumber)('' + matches.length)} MSBuild version: [${matches.map(path => (0, utils_js_1.light)(path)).join(', ')}]`);
    }
    const pbuilds = matches.map(async (selected) => {
        npmlog_1.default.silly('find-msbuild', matches.join(', '));
        // const selected = matches[matches.length - 1];
        const txt = await (0, utils_js_1.execFile)(selected, ['/version']);
        const m = txt.match(/(\d+)\.\d+/);
        if (!m) {
            npmlog_1.default.warn('find-msbuild', `${selected} is not a valid msbuild path, can not find it's versdion`);
            return {
                path: selected,
                version: 0,
            };
        }
        //   return Promise.reject('fail to get MSBuild.exe version number');
        npmlog_1.default.info('find-msbuild', `discover msbuild v${(0, utils_js_1.formatNumber)("%s")} in ${(0, utils_js_1.highlight)("%s")}`, m[1], selected);
        return {
            path: selected,
            version: Number(m[1]),
        };
    });
    const builds = await Promise.all(pbuilds);
    // drop versionnumber = 0;
    return builds.filter(a => a.version).reverse();
}
exports.findMSBuild = findMSBuild;
//# sourceMappingURL=findMsBuild.js.map