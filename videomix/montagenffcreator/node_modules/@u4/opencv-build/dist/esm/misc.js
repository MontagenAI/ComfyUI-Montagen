/**
 * list of variables needed to link and use openCV
 */
export const OPENCV_PATHS_ENV = ['OPENCV_BIN_DIR', 'OPENCV_INCLUDE_DIR', 'OPENCV_LIB_DIR'];
/**
 * arguments data
 * key must be === arg
 */
export const ALLARGS = {
    version: { arg: 'version', conf: 'autoBuildOpencvVersion', env: 'OPENCV4NODEJS_AUTOBUILD_OPENCV_VERSION', isBool: false, doc: 'OpenCV version' },
    flags: { arg: 'flags', conf: 'autoBuildFlags', env: 'OPENCV4NODEJS_AUTOBUILD_FLAGS', isBool: false, doc: 'OpenCV cMake Build flags' },
    root: { arg: 'root', conf: 'rootcwd', env: 'INIT_CWD', isBool: false, doc: 'OpenCV-build root directory (deprecated)' },
    buildRoot: { arg: 'buildRoot', conf: 'buildRoot', env: 'OPENCV_BUILD_ROOT', isBool: false, doc: 'OpenCV build directory' },
    cuda: { arg: 'cuda', conf: 'autoBuildBuildCuda', env: 'OPENCV4NODEJS_BUILD_CUDA', isBool: true, doc: 'Enable cuda in OpenCV build' },
    // add on 28/12/2022
    cudaArch: { arg: 'cudaArch', conf: 'cudaArch', env: 'OPENCV4NODEJS_BUILD_CUDA_ARCH', isBool: false, doc: 'Specify the cuda arch will drasticly reduce build time, see https://en.wikipedia.org/wiki/CUDA, ex if you have a RTX 3080 use --cudaArch=8.6, if you have also a RTX 2080 --cudaArch=7.5,8.6' },
    nocontrib: { arg: 'nocontrib', conf: 'autoBuildWithoutContrib', env: 'OPENCV4NODEJS_AUTOBUILD_WITHOUT_CONTRIB', isBool: true, doc: 'Do not compile Contrib modules' },
    nobuild: { arg: 'nobuild', conf: 'disableAutoBuild', env: 'OPENCV4NODEJS_DISABLE_AUTOBUILD', isBool: true, doc: 'Do build OpenCV' },
    incDir: { arg: 'incDir', conf: 'opencvIncludeDir', env: 'OPENCV_INCLUDE_DIR', isBool: false, doc: 'OpenCV include directory' },
    libDir: { arg: 'libDir', conf: 'opencvLibDir', env: 'OPENCV_LIB_DIR', isBool: false, doc: 'OpenCV library directory' },
    binDir: { arg: 'binDir', conf: 'opencvBinDir', env: 'OPENCV_BIN_DIR', isBool: false, doc: 'OpenCV bin directory' },
    keepsources: { arg: 'keepsources', conf: 'keepsources', isBool: true, doc: 'Keepsources OpenCV source after build' },
    'dry-run': { arg: 'dry-run', conf: 'dry-run', isBool: true, doc: 'Display command line use to build library' },
    'git-cache': { arg: 'git-cache', conf: 'git-cache', env: 'OPENCV_GIT_CACHE', isBool: true, doc: 'Reduce Bandwide usage, by keeping a local git souce un the buildRoot' },
};
/**
 * generate help message
 * @returns help message as text with colors
 */
export const genHelp = () => {
    return Object.values(ALLARGS).map(a => {
        const name = `--${a.arg}${!a.isBool ? ' <value>' : ''}`;
        const envWay = a.env ? ` (${a.env} env variable)` : '';
        return `   ${name.padEnd(20)} ${a.doc.padEnd(40)}${envWay}`;
    }).join('\n');
};
/**
 * A basic args parser
 * @param args cmd lines args
 * @returns and openCVBuildEnvParams object containing an extra object with all unknown args
 */
export const args2Option = (args) => {
    const out = { extra: {} };
    for (let i = 0; i < args.length; i++) {
        let arg = args[i];
        if (arg.startsWith('--')) {
            arg = arg.substring(2);
        }
        else if (arg.startsWith('-')) {
            arg = arg.substring(1);
        }
        else {
            continue;
        }
        const p = arg.indexOf('=');
        const name = ((p === -1) ? arg : arg.substring(0, p));
        const info = ALLARGS[name];
        if (!info) {
            // keep unknown args in extras
            const val = (p > 0) ? arg.substring(p + 1) : (i + 1 < args.length) ? args[i + 1] : '1';
            if (out.extra)
                out.extra[name] = val;
            continue;
        }
        if (info.isBool) {
            out[info.conf] = true;
            continue;
        }
        const val = (p > 0) ? arg.substring(p + 1) : args[++i];
        if (val)
            out[info.conf] = val;
    }
    // encvIncludeDir?: string;
    return out;
};
/**
 * from https://docs.opencv.org/4.x/
 */
export const MODEULES_MAP = {
    // not a real module
    // apps: true,
    // not a real module
    world: false,
    // was enabled in previous version.
    python_tests: true,
    /**
     * Core functionality
     * https://docs.opencv.org/4.x/d0/de1/group__core.html
     */
    core: true,
    /**
     * Image Processing
     * https://docs.opencv.org/4.x/d7/dbd/group__imgproc.html
     */
    imgproc: true,
    /**
     * Image file reading and writing
     * https://docs.opencv.org/4.x/d4/da8/group__imgcodecs.html
     */
    imgcodecs: true,
    /**
     * Video I/O
     * https://docs.opencv.org/4.x/dd/de7/group__videoio.html
     */
    videoio: true,
    /**
     * High-level GUI
     * https://docs.opencv.org/4.x/d7/dfc/group__highgui.html
     */
    highgui: true,
    /**
     * Video Analysis
     * https://docs.opencv.org/4.x/d7/de9/group__video.html
     */
    video: true,
    /**
     * Camera Calibration and 3D Reconstruction
     * https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
     */
    calib3d: true,
    /**
     * 2D Features Framework
     * https://docs.opencv.org/4.x/da/d9b/group__features2d.html
     */
    features2d: true,
    /**
     * Object Detection
     * https://docs.opencv.org/4.x/d5/d54/group__objdetect.html
     */
    objdetect: true,
    /**
     * Deep Neural Network module
     * https://docs.opencv.org/4.x/d6/d0f/group__dnn.html
     */
    dnn: true,
    /**
     * Machine Learning
     * https://docs.opencv.org/4.x/dd/ded/group__ml.html
     */
    ml: true,
    /**
     * Clustering and Search in Multi-Dimensional Spaces
     * https://docs.opencv.org/4.x/dc/de5/group__flann.html
     */
    flann: true,
    /**
     * Computational Photography
     * https://docs.opencv.org/4.x/d1/d0d/group__photo.html
     */
    photo: true,
    /**
     * Images stitching
     * https://docs.opencv.org/4.x/d1/d46/group__stitching.html
     */
    stitching: false,
    /**
     * Graph API
     * https://docs.opencv.org/4.x/d0/d1e/gapi.html
     */
    gapi: true,
    /**
     * Extra modules
     */
    /**
     * Alpha Matting
     * https://docs.opencv.org/4.x/d4/d40/group__alphamat.html
     */
    alphamat: null,
    /**
     * Aruco markers, module functionality was moved to objdetect module
     * https://docs.opencv.org/4.x/d9/d6a/group__aruco.html
     */
    aruco: false,
    /**
     * Barcode detecting and decoding methods
     * https://docs.opencv.org/4.x/d2/dea/group__barcode.html
     */
    barcode: null,
    /**
     * Improved Background-Foreground Segmentation Methods
     * https://docs.opencv.org/4.x/d2/d55/group__bgsegm.html
     */
    bgsegm: false,
    /**
     * Biologically inspired vision models and derivated tools
     * https://docs.opencv.org/4.x/dd/deb/group__bioinspired.html
     */
    bioinspired: false,
    /**
     * Custom Calibration Pattern for 3D reconstruction
     * https://docs.opencv.org/4.x/d3/ddc/group__ccalib.html
     */
    ccalib: false,
    /**
     * Operations on Matrices
     * https://docs.opencv.org/4.x/d5/d8e/group__cudaarithm.html
     */
    cudaarithm: null,
    /**
     * Background Segmentation
     * https://docs.opencv.org/4.x/d6/d17/group__cudabgsegm.html
     */
    cudabgsegm: null,
    /**
     * Video Encoding/Decoding
     * https://docs.opencv.org/4.x/d0/d61/group__cudacodec.html
     */
    cudacodec: null,
    /**
     * Feature Detection and Description
     * https://docs.opencv.org/4.x/d6/d1d/group__cudafeatures2d.html
     */
    cudafeatures2d: null,
    /**
     * Image Filtering
     * https://docs.opencv.org/4.x/dc/d66/group__cudafilters.html
     */
    cudafilters: null,
    /**
     * Image Processing
     * https://docs.opencv.org/4.x/d0/d05/group__cudaimgproc.html
     */
    cudaimgproc: null,
    /**
     * Legacy support
     * https://docs.opencv.org/4.x/d5/dc3/group__cudalegacy.html
     */
    cudalegacy: null,
    /**
     * Object Detection
     * https://docs.opencv.org/4.x/d9/d3f/group__cudaobjdetect.html
     */
    cudaobjdetect: null,
    /**
     * Optical Flow
     * https://docs.opencv.org/4.x/d7/d3f/group__cudaoptflow.html
     */
    cudaoptflow: null,
    /**
     * Stereo Correspondence
     * https://docs.opencv.org/4.x/dd/d47/group__cudastereo.html
     */
    cudastereo: null,
    /**
     * Image Warping
     * https://docs.opencv.org/4.x/db/d29/group__cudawarping.html
     */
    cudawarping: null,
    /**
     * Device layer
     * https://docs.opencv.org/4.x/df/dfc/group__cudev.html
     */
    cudev: null,
    /**
     * GUI for Interactive Visual Debugging of Computer Vision Programs
     * https://docs.opencv.org/4.x/df/dff/group__cvv.html
     */
    cvv: null,
    /**
     * Framework for working with different datasets
     * https://docs.opencv.org/4.x/d8/d00/group__datasets.html
     */
    datasets: false,
    /**
     * DNN used for object detection
     * https://docs.opencv.org/4.x/d5/df6/group__dnn__objdetect.html
     */
    dnn_objdetect: false,
    /**
     * DNN used for super resolution
     * https://docs.opencv.org/4.x/d9/de0/group__dnn__superres.html
     */
    dnn_superres: null,
    /**
     * Deformable Part-based Models
     * https://docs.opencv.org/4.x/d9/d12/group__dpm.html
     */
    dpm: false,
    /**
     * Face Analysis
     * https://docs.opencv.org/4.x/db/d7c/group__face.html
     */
    face: true,
    /**
     * Drawing UTF-8 strings with freetype/harfbuzz
     * https://docs.opencv.org/4.x/d4/dfc/group__freetype.html
     */
    freetype: null,
    /**
     * Image processing based on fuzzy mathematics
     * https://docs.opencv.org/4.x/df/d5b/group__fuzzy.html
     */
    fuzzy: false,
    /**
     * Hierarchical Data Format I/O routines
     * https://docs.opencv.org/4.x/db/d77/group__hdf.html
     */
    hdf: null,
    /**
     * Hierarchical Feature Selection for Efficient Image Segmentation
     * https://docs.opencv.org/4.x/dc/d29/group__hfs.html
     */
    hfs: false,
    /**
     * The module brings implementations of different image hashing algorithms.
     * https://docs.opencv.org/4.x/d4/d93/group__img__hash.html
     */
    img_hash: true,
    /**
     * The module brings implementations of intensity transformation algorithms to adjust image contrast.
     * https://docs.opencv.org/4.x/dc/dfe/group__intensity__transform.html
     */
    intensity_transform: null,
    /**
     * Julia bindings for OpenCV
     * https://docs.opencv.org/4.x/d7/d44/group__julia.html
     */
    julia: null,
    /**
     * Binary descriptors for lines extracted from an image
     * https://docs.opencv.org/4.x/dc/ddd/group__line__descriptor.html
     */
    line_descriptor: false,
    /**
     * Macbeth Chart module
     * https://docs.opencv.org/4.x/dd/d19/group__mcc.html
     */
    mcc: null,
    /**
     * Optical Flow Algorithms
     * https://docs.opencv.org/4.x/d2/d84/group__optflow.html
     */
    optflow: false,
    /**
     * OGRE 3D Visualiser
     * https://docs.opencv.org/4.x/d2/d17/group__ovis.html
     */
    ovis: null,
    /**
     * Phase Unwrapping API
     * https://docs.opencv.org/4.x/df/d3a/group__phase__unwrapping.html
     */
    phase_unwrapping: false,
    /**
     * Plot function for Mat data
     * https://docs.opencv.org/4.x/db/dfe/group__plot.html
     */
    plot: null,
    /*
     * Image Quality Analysis (IQA) API
     * https://docs.opencv.org/4.x/dc/d20/group__quality.html
     */
    quality: null,
    /**
     * silhouette based 3D object tracking
     * https://docs.opencv.org/4.x/d4/dc4/group__rapid.html
     */
    rapid: null,
    /**
     * Image Registration
     * https://docs.opencv.org/4.x/db/d61/group__reg.html
     */
    reg: false,
    /**
     * RGB-Depth Processing
     * https://docs.opencv.org/4.x/d2/d3a/group__rgbd.html
     */
    rgbd: false,
    /**
     * Saliency API
     * https://docs.opencv.org/4.x/d8/d65/group__saliency.html
     */
    saliency: false,
    /**
     * Structure From Motion
     * https://docs.opencv.org/4.x/d8/d8c/group__sfm.html
     */
    sfm: null,
    /**
     * Shape Distance and Matching
     * https://docs.opencv.org/4.x/d1/d85/group__shape.html
     */
    shape: false,
    /**
     * Stereo Correspondance Algorithms
     * https://docs.opencv.org/4.x/dd/d86/group__stereo.html
     */
    stereo: false,
    /**
     * Structured Light API
     * https://docs.opencv.org/4.x/d1/d90/group__structured__light.html
     */
    structured_light: false,
    /**
     * Super Resolution
     * https://docs.opencv.org/4.x/d7/d0a/group__superres.html
     */
    superres: false,
    /**
     * Surface Matching
     * https://docs.opencv.org/4.x/d9/d25/group__surface__matching.html
     */
    surface_matching: false,
    /**
     * Scene Text Detection and Recognition
     * https://docs.opencv.org/4.x/d4/d61/group__text.html
     */
    text: true,
    /**
     * Tracking API
     * https://docs.opencv.org/4.x/d9/df8/group__tracking.html
     */
    tracking: true,
    /**
     * Video Stabilization
     * https://docs.opencv.org/4.x/d5/d50/group__videostab.html
     */
    videostab: true,
    /**
     * 3D Visualizer
     * https://docs.opencv.org/4.x/d1/d19/group__viz.html
     */
    viz: null,
    /**
     * WeChat QR code detector for detecting and parsing QR code.
     * https://docs.opencv.org/4.x/dd/d63/group__wechat__qrcode.html
     */
    wechat_qrcode: false,
    /**
     * Extra 2D Features Framework
     * https://docs.opencv.org/4.x/d1/db4/group__xfeatures2d.html
     */
    xfeatures2d: true,
    /**
     * Extended Image Processing
     * https://docs.opencv.org/4.x/df/d2d/group__ximgproc.html
     */
    ximgproc: true,
    /**
     * Extended object detection
     * https://docs.opencv.org/4.x/d4/d54/group__xobjdetect.html
     */
    xobjdetect: false,
    /**
     * Additional photo processing algorithms
     * https://docs.opencv.org/4.x/de/daa/group__xphoto.html
     */
    xphoto: false,
    // olds:
    apps: false,
    java_bindings_generator: false,
    js: false,
    bindings_generator: false,
    objc_bindings_generator: false,
    python3: false,
    python_bindings_generator: false,
    ts: false,
};
/**
 * All available module fron openCV 4.5.5
 */
export const ALL_OPENCV_MODULES = new Set(Object.keys(MODEULES_MAP));
//# sourceMappingURL=misc.js.map