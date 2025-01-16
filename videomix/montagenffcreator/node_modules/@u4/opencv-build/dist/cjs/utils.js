"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.isCudaAvailable = exports.requireCmake = exports.requireGit = exports.spawn = exports.execFile = exports.execSync = exports.exec = exports.formatNumber = exports.formatRed = exports.light = exports.highlight = exports.toExecCmd = exports.protect = void 0;
const child_process_1 = __importDefault(require("child_process"));
const fs_1 = __importDefault(require("fs"));
const os_1 = require("os");
const path_1 = __importDefault(require("path"));
const npmlog_1 = __importDefault(require("npmlog"));
const picocolors_1 = __importDefault(require("picocolors"));
/**
 * excape spaces for shell execution
 * @param txt text to escape
 * @returns a shell no spaced parameter
 */
const protect = (txt) => { if (txt.includes(' ')) {
    return `"${txt}"`;
}
else {
    return txt;
} };
exports.protect = protect;
function toExecCmd(bin, args) {
    return `${(0, exports.protect)(bin)} ${args.map(exports.protect).join(' ')}`;
}
exports.toExecCmd = toExecCmd;
function highlight(text) {
    return picocolors_1.default.bold(picocolors_1.default.yellow(text));
}
exports.highlight = highlight;
function light(text) {
    return picocolors_1.default.yellow(text);
}
exports.light = light;
function formatRed(text) {
    return picocolors_1.default.red(text);
}
exports.formatRed = formatRed;
function formatNumber(text) {
    return picocolors_1.default.bold(picocolors_1.default.green(text));
}
exports.formatNumber = formatNumber;
function exec(cmd, options) {
    npmlog_1.default.silly('install', 'executing: %s', (0, exports.protect)(cmd));
    return new Promise(function (resolve, reject) {
        child_process_1.default.exec(cmd, options, function (err, stdout, stderr) {
            const _err = err || stderr;
            if (_err)
                return reject(_err);
            return resolve(stdout.toString());
        });
    });
}
exports.exec = exec;
function execSync(cmd, options) {
    npmlog_1.default.silly('install', 'executing: %s', (0, exports.protect)(cmd));
    const stdout = child_process_1.default.execSync(cmd, options);
    return stdout.toString();
}
exports.execSync = execSync;
/**
 * only used by findVs2017
 */
function execFile(cmd, args, options) {
    npmlog_1.default.silly('install', 'executing: %s %s', (0, exports.protect)(cmd), args.map(exports.protect).join(' '));
    return new Promise(function (resolve, reject) {
        const child = child_process_1.default.execFile(cmd, args, options, function (err, stdout, stderr) {
            const _err = err || stderr;
            if (_err)
                return reject(_err);
            return resolve(stdout.toString());
        });
        child.stdin && child.stdin.end();
    });
}
exports.execFile = execFile;
function spawn(cmd, args, options, filters) {
    filters = filters || {};
    const filterStdout = (data) => {
        if (filters && filters.out) {
            data = filters.out(data);
            if (!data)
                return;
        }
        process.stdout.write(data);
    };
    const filterStderr = (data) => {
        if (filters && filters.err) {
            data = filters.err(data);
            if (!data)
                return;
        }
        process.stderr.write(data);
    };
    npmlog_1.default.silly('install', 'spawning:', (0, exports.protect)(cmd), args.map(exports.protect).join(' '));
    return new Promise(function (resolve, reject) {
        try {
            const child = child_process_1.default.spawn(cmd, args, { stdio: ['inherit', 'pipe', 'pipe'], ...options });
            child.stderr.on('data', filterStderr);
            child.stdout.on('data', filterStdout);
            child.on('exit', function (code) {
                if (typeof code !== 'number') {
                    code = null;
                }
                const msg = `running: ${(0, exports.protect)(cmd)} ${args.map(exports.protect).join(' ')}${os_1.EOL}in ${options.cwd} exited with code ${code} (for more info, set '--loglevel silly')'`;
                // if (code !== 0)
                //   console.log(`End of spawn ${cmd} ${args.join(' ')} RET:`, code);
                if (code !== 0) {
                    return reject(msg);
                }
                return resolve(msg);
            });
        }
        catch (err) {
            return reject(err);
        }
    });
}
exports.spawn = spawn;
async function requireCmd(cmd, hint) {
    npmlog_1.default.info('install', `executing: ${picocolors_1.default.cyan('%s')}`, cmd);
    try {
        const stdout = await exec(cmd);
        npmlog_1.default.verbose('install', `${cmd}: ${stdout.trim()}`);
        return stdout;
    }
    catch (err) {
        const errMessage = `failed to execute ${cmd}, ${hint}, error is: ${err.toString()}`;
        throw new Error(errMessage);
    }
}
function requireCmdSync(cmd, hint) {
    npmlog_1.default.info('install', `executing: ${picocolors_1.default.cyan('%s')}`, cmd);
    try {
        const stdout = execSync(cmd);
        npmlog_1.default.verbose('install', `${cmd}: ${stdout.trim()}`);
        return stdout;
    }
    catch (err) {
        const errMessage = `failed to execute ${cmd}, ${hint}, error is: ${err.toString()}`;
        throw new Error(errMessage);
    }
}
async function requireGit() {
    const out = await requireCmd('git --version', 'git is required');
    const version = out.match(/version ([\d.\w]+)/);
    if (version) {
        npmlog_1.default.info('install', `git Version ${formatNumber("%s")} found`, version[1]);
    }
}
exports.requireGit = requireGit;
async function requireCmake() {
    const out = await requireCmd('cmake --version', 'cmake is required to build opencv');
    const version = out.match(/version ([\d.\w]+)/);
    if (version) {
        npmlog_1.default.info('install', `cmake Version ${formatNumber("%s")} found`, version[1]);
    }
}
exports.requireCmake = requireCmake;
let cached_cuda = null;
/**
 * looks for cuda lib
 * @returns
 */
function isCudaAvailable() {
    if (cached_cuda != null)
        return cached_cuda;
    npmlog_1.default.info('install', 'Check if CUDA is available & what version...');
    if (process.platform == 'win32') {
        try {
            requireCmdSync('nvcc --version', 'CUDA availability check');
            // return true;
        }
        catch (err) {
            npmlog_1.default.info('install', 'Seems like CUDA is not installed; nvcc --version call failed');
            return false;
        }
    }
    // Because NVCC is not installed by default & requires an extra install step,
    // this is work around that always works
    const { CUDA_PATH } = process.env;
    for (const cudaPath of [CUDA_PATH, '/usr/local/cuda/']) {
        if (!cudaPath)
            continue;
        if (!fs_1.default.existsSync(cudaPath))
            continue;
        for (const file of ['version.txt', 'version.json']) {
            const realpath = path_1.default.resolve(cudaPath, file);
            if (fs_1.default.existsSync(realpath)) {
                const content = fs_1.default.readFileSync(realpath, 'utf8');
                npmlog_1.default.info('install', content);
                cached_cuda = true;
                return true;
            }
        }
    }
    npmlog_1.default.info('install', `CUDA version file could not be found in {/usr/local/cuda/,CUDA_PATH}version.{txt,json}`);
    cached_cuda = false;
    return false;
}
exports.isCudaAvailable = isCudaAvailable;
//# sourceMappingURL=utils.js.map