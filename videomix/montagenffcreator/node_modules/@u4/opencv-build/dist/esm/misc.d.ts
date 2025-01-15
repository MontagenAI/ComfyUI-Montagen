/**
 * options passed to OpenCVBuildEnv constructor
 * highest priority values
 */
export interface OpenCVBuildEnvParamsBool {
    autoBuildBuildCuda?: boolean;
    autoBuildWithoutContrib?: boolean;
    disableAutoBuild?: boolean;
    keepsources?: boolean;
    'dry-run'?: boolean;
    'git-cache'?: boolean;
}
type boolKey = keyof OpenCVBuildEnvParamsBool;
export interface OpenCVBuildEnvParamsString {
    /**
     * OpenCV-build root directory, deprecated in favor of buildRoot
     */
    rootcwd?: string;
    /**
     * OpenCV build directory, this directory will be populate with a folder per build, permiting to reused previous build.
     */
    buildRoot?: string;
    /**
     * OpenCV version to build
     */
    autoBuildOpencvVersion?: string;
    /**
     * OpenCV cMake Build flags
     */
    autoBuildFlags?: string;
    /**
     * OpenCV include directory
     * looks like: opencv/build/include
     */
    opencvIncludeDir?: string;
    /**
     * OpenCV library directory
     * looks like: opencv/build/.../lib
     */
    opencvLibDir?: string;
    /**
     * OpenCV bin directory
     * looks like: opencv/build/.../bin
     */
    opencvBinDir?: string;
    /**
     * Restrict cuda targeded version to a limited set of version
     * add on 28/12/2022
     */
    cudaArch?: string;
}
type stringKey = keyof OpenCVBuildEnvParamsString;
/**
 * Options as usable in opencv4nodejs section from package.json
 * Middle priority values
 */
export type OpenCVPackageBuildOptions = {
    [key in boolKey | stringKey]?: string;
};
export interface OpenCVBuildEnvParams extends OpenCVBuildEnvParamsBool, OpenCVBuildEnvParamsString {
    /**
     * Allow speedup API usage by allowing direct access to a preexisting build
     */
    prebuild?: 'latestBuild' | 'latestVersion' | 'oldestBuild' | 'oldestVersion';
    extra?: {
        [key: string]: string;
    };
}
/**
 * local args parser model
 */
export interface ArgInfo {
    arg: string;
    conf: keyof OpenCVPackageBuildOptions;
    env: string;
    isBool: boolean;
    doc: string;
}
/**
 * list of variables needed to link and use openCV
 */
export declare const OPENCV_PATHS_ENV: readonly ["OPENCV_BIN_DIR", "OPENCV_INCLUDE_DIR", "OPENCV_LIB_DIR"];
/**
 * arguments data
 * key must be === arg
 */
export declare const ALLARGS: {
    version: ArgInfo;
    flags: ArgInfo;
    root: ArgInfo;
    buildRoot: ArgInfo;
    cuda: ArgInfo;
    cudaArch: ArgInfo;
    nocontrib: ArgInfo;
    nobuild: ArgInfo;
    incDir: ArgInfo;
    libDir: ArgInfo;
    binDir: ArgInfo;
    keepsources: ArgInfo;
    'dry-run': ArgInfo;
    'git-cache': ArgInfo;
};
/**
 * generate help message
 * @returns help message as text with colors
 */
export declare const genHelp: () => string;
/**
 * A basic args parser
 * @param args cmd lines args
 * @returns and openCVBuildEnvParams object containing an extra object with all unknown args
 */
export declare const args2Option: (args: string[]) => OpenCVBuildEnvParams;
/**
 * from https://docs.opencv.org/4.x/
 */
export declare const MODEULES_MAP: {
    readonly world: false;
    readonly python_tests: true;
    /**
     * Core functionality
     * https://docs.opencv.org/4.x/d0/de1/group__core.html
     */
    readonly core: true;
    /**
     * Image Processing
     * https://docs.opencv.org/4.x/d7/dbd/group__imgproc.html
     */
    readonly imgproc: true;
    /**
     * Image file reading and writing
     * https://docs.opencv.org/4.x/d4/da8/group__imgcodecs.html
     */
    readonly imgcodecs: true;
    /**
     * Video I/O
     * https://docs.opencv.org/4.x/dd/de7/group__videoio.html
     */
    readonly videoio: true;
    /**
     * High-level GUI
     * https://docs.opencv.org/4.x/d7/dfc/group__highgui.html
     */
    readonly highgui: true;
    /**
     * Video Analysis
     * https://docs.opencv.org/4.x/d7/de9/group__video.html
     */
    readonly video: true;
    /**
     * Camera Calibration and 3D Reconstruction
     * https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
     */
    readonly calib3d: true;
    /**
     * 2D Features Framework
     * https://docs.opencv.org/4.x/da/d9b/group__features2d.html
     */
    readonly features2d: true;
    /**
     * Object Detection
     * https://docs.opencv.org/4.x/d5/d54/group__objdetect.html
     */
    readonly objdetect: true;
    /**
     * Deep Neural Network module
     * https://docs.opencv.org/4.x/d6/d0f/group__dnn.html
     */
    readonly dnn: true;
    /**
     * Machine Learning
     * https://docs.opencv.org/4.x/dd/ded/group__ml.html
     */
    readonly ml: true;
    /**
     * Clustering and Search in Multi-Dimensional Spaces
     * https://docs.opencv.org/4.x/dc/de5/group__flann.html
     */
    readonly flann: true;
    /**
     * Computational Photography
     * https://docs.opencv.org/4.x/d1/d0d/group__photo.html
     */
    readonly photo: true;
    /**
     * Images stitching
     * https://docs.opencv.org/4.x/d1/d46/group__stitching.html
     */
    readonly stitching: false;
    /**
     * Graph API
     * https://docs.opencv.org/4.x/d0/d1e/gapi.html
     */
    readonly gapi: true;
    /**
     * Extra modules
     */
    /**
     * Alpha Matting
     * https://docs.opencv.org/4.x/d4/d40/group__alphamat.html
     */
    readonly alphamat: null;
    /**
     * Aruco markers, module functionality was moved to objdetect module
     * https://docs.opencv.org/4.x/d9/d6a/group__aruco.html
     */
    readonly aruco: false;
    /**
     * Barcode detecting and decoding methods
     * https://docs.opencv.org/4.x/d2/dea/group__barcode.html
     */
    readonly barcode: null;
    /**
     * Improved Background-Foreground Segmentation Methods
     * https://docs.opencv.org/4.x/d2/d55/group__bgsegm.html
     */
    readonly bgsegm: false;
    /**
     * Biologically inspired vision models and derivated tools
     * https://docs.opencv.org/4.x/dd/deb/group__bioinspired.html
     */
    readonly bioinspired: false;
    /**
     * Custom Calibration Pattern for 3D reconstruction
     * https://docs.opencv.org/4.x/d3/ddc/group__ccalib.html
     */
    readonly ccalib: false;
    /**
     * Operations on Matrices
     * https://docs.opencv.org/4.x/d5/d8e/group__cudaarithm.html
     */
    readonly cudaarithm: null;
    /**
     * Background Segmentation
     * https://docs.opencv.org/4.x/d6/d17/group__cudabgsegm.html
     */
    readonly cudabgsegm: null;
    /**
     * Video Encoding/Decoding
     * https://docs.opencv.org/4.x/d0/d61/group__cudacodec.html
     */
    readonly cudacodec: null;
    /**
     * Feature Detection and Description
     * https://docs.opencv.org/4.x/d6/d1d/group__cudafeatures2d.html
     */
    readonly cudafeatures2d: null;
    /**
     * Image Filtering
     * https://docs.opencv.org/4.x/dc/d66/group__cudafilters.html
     */
    readonly cudafilters: null;
    /**
     * Image Processing
     * https://docs.opencv.org/4.x/d0/d05/group__cudaimgproc.html
     */
    readonly cudaimgproc: null;
    /**
     * Legacy support
     * https://docs.opencv.org/4.x/d5/dc3/group__cudalegacy.html
     */
    readonly cudalegacy: null;
    /**
     * Object Detection
     * https://docs.opencv.org/4.x/d9/d3f/group__cudaobjdetect.html
     */
    readonly cudaobjdetect: null;
    /**
     * Optical Flow
     * https://docs.opencv.org/4.x/d7/d3f/group__cudaoptflow.html
     */
    readonly cudaoptflow: null;
    /**
     * Stereo Correspondence
     * https://docs.opencv.org/4.x/dd/d47/group__cudastereo.html
     */
    readonly cudastereo: null;
    /**
     * Image Warping
     * https://docs.opencv.org/4.x/db/d29/group__cudawarping.html
     */
    readonly cudawarping: null;
    /**
     * Device layer
     * https://docs.opencv.org/4.x/df/dfc/group__cudev.html
     */
    readonly cudev: null;
    /**
     * GUI for Interactive Visual Debugging of Computer Vision Programs
     * https://docs.opencv.org/4.x/df/dff/group__cvv.html
     */
    readonly cvv: null;
    /**
     * Framework for working with different datasets
     * https://docs.opencv.org/4.x/d8/d00/group__datasets.html
     */
    readonly datasets: false;
    /**
     * DNN used for object detection
     * https://docs.opencv.org/4.x/d5/df6/group__dnn__objdetect.html
     */
    readonly dnn_objdetect: false;
    /**
     * DNN used for super resolution
     * https://docs.opencv.org/4.x/d9/de0/group__dnn__superres.html
     */
    readonly dnn_superres: null;
    /**
     * Deformable Part-based Models
     * https://docs.opencv.org/4.x/d9/d12/group__dpm.html
     */
    readonly dpm: false;
    /**
     * Face Analysis
     * https://docs.opencv.org/4.x/db/d7c/group__face.html
     */
    readonly face: true;
    /**
     * Drawing UTF-8 strings with freetype/harfbuzz
     * https://docs.opencv.org/4.x/d4/dfc/group__freetype.html
     */
    readonly freetype: null;
    /**
     * Image processing based on fuzzy mathematics
     * https://docs.opencv.org/4.x/df/d5b/group__fuzzy.html
     */
    readonly fuzzy: false;
    /**
     * Hierarchical Data Format I/O routines
     * https://docs.opencv.org/4.x/db/d77/group__hdf.html
     */
    readonly hdf: null;
    /**
     * Hierarchical Feature Selection for Efficient Image Segmentation
     * https://docs.opencv.org/4.x/dc/d29/group__hfs.html
     */
    readonly hfs: false;
    /**
     * The module brings implementations of different image hashing algorithms.
     * https://docs.opencv.org/4.x/d4/d93/group__img__hash.html
     */
    readonly img_hash: true;
    /**
     * The module brings implementations of intensity transformation algorithms to adjust image contrast.
     * https://docs.opencv.org/4.x/dc/dfe/group__intensity__transform.html
     */
    readonly intensity_transform: null;
    /**
     * Julia bindings for OpenCV
     * https://docs.opencv.org/4.x/d7/d44/group__julia.html
     */
    readonly julia: null;
    /**
     * Binary descriptors for lines extracted from an image
     * https://docs.opencv.org/4.x/dc/ddd/group__line__descriptor.html
     */
    readonly line_descriptor: false;
    /**
     * Macbeth Chart module
     * https://docs.opencv.org/4.x/dd/d19/group__mcc.html
     */
    readonly mcc: null;
    /**
     * Optical Flow Algorithms
     * https://docs.opencv.org/4.x/d2/d84/group__optflow.html
     */
    readonly optflow: false;
    /**
     * OGRE 3D Visualiser
     * https://docs.opencv.org/4.x/d2/d17/group__ovis.html
     */
    readonly ovis: null;
    /**
     * Phase Unwrapping API
     * https://docs.opencv.org/4.x/df/d3a/group__phase__unwrapping.html
     */
    readonly phase_unwrapping: false;
    /**
     * Plot function for Mat data
     * https://docs.opencv.org/4.x/db/dfe/group__plot.html
     */
    readonly plot: null;
    readonly quality: null;
    /**
     * silhouette based 3D object tracking
     * https://docs.opencv.org/4.x/d4/dc4/group__rapid.html
     */
    readonly rapid: null;
    /**
     * Image Registration
     * https://docs.opencv.org/4.x/db/d61/group__reg.html
     */
    readonly reg: false;
    /**
     * RGB-Depth Processing
     * https://docs.opencv.org/4.x/d2/d3a/group__rgbd.html
     */
    readonly rgbd: false;
    /**
     * Saliency API
     * https://docs.opencv.org/4.x/d8/d65/group__saliency.html
     */
    readonly saliency: false;
    /**
     * Structure From Motion
     * https://docs.opencv.org/4.x/d8/d8c/group__sfm.html
     */
    readonly sfm: null;
    /**
     * Shape Distance and Matching
     * https://docs.opencv.org/4.x/d1/d85/group__shape.html
     */
    readonly shape: false;
    /**
     * Stereo Correspondance Algorithms
     * https://docs.opencv.org/4.x/dd/d86/group__stereo.html
     */
    readonly stereo: false;
    /**
     * Structured Light API
     * https://docs.opencv.org/4.x/d1/d90/group__structured__light.html
     */
    readonly structured_light: false;
    /**
     * Super Resolution
     * https://docs.opencv.org/4.x/d7/d0a/group__superres.html
     */
    readonly superres: false;
    /**
     * Surface Matching
     * https://docs.opencv.org/4.x/d9/d25/group__surface__matching.html
     */
    readonly surface_matching: false;
    /**
     * Scene Text Detection and Recognition
     * https://docs.opencv.org/4.x/d4/d61/group__text.html
     */
    readonly text: true;
    /**
     * Tracking API
     * https://docs.opencv.org/4.x/d9/df8/group__tracking.html
     */
    readonly tracking: true;
    /**
     * Video Stabilization
     * https://docs.opencv.org/4.x/d5/d50/group__videostab.html
     */
    readonly videostab: true;
    /**
     * 3D Visualizer
     * https://docs.opencv.org/4.x/d1/d19/group__viz.html
     */
    readonly viz: null;
    /**
     * WeChat QR code detector for detecting and parsing QR code.
     * https://docs.opencv.org/4.x/dd/d63/group__wechat__qrcode.html
     */
    readonly wechat_qrcode: false;
    /**
     * Extra 2D Features Framework
     * https://docs.opencv.org/4.x/d1/db4/group__xfeatures2d.html
     */
    readonly xfeatures2d: true;
    /**
     * Extended Image Processing
     * https://docs.opencv.org/4.x/df/d2d/group__ximgproc.html
     */
    readonly ximgproc: true;
    /**
     * Extended object detection
     * https://docs.opencv.org/4.x/d4/d54/group__xobjdetect.html
     */
    readonly xobjdetect: false;
    /**
     * Additional photo processing algorithms
     * https://docs.opencv.org/4.x/de/daa/group__xphoto.html
     */
    readonly xphoto: false;
    readonly apps: false;
    readonly java_bindings_generator: false;
    readonly js: false;
    readonly bindings_generator: false;
    readonly objc_bindings_generator: false;
    readonly python3: false;
    readonly python_bindings_generator: false;
    readonly ts: false;
};
/**
 * type of valid openCV Modules
 */
export type OpencvModulesType = keyof typeof MODEULES_MAP;
/**
 * All available module fron openCV 4.5.5
 */
export declare const ALL_OPENCV_MODULES: Set<"video" | "text" | "world" | "python_tests" | "core" | "imgproc" | "imgcodecs" | "videoio" | "highgui" | "calib3d" | "features2d" | "objdetect" | "dnn" | "ml" | "flann" | "photo" | "stitching" | "gapi" | "alphamat" | "aruco" | "barcode" | "bgsegm" | "bioinspired" | "ccalib" | "cudaarithm" | "cudabgsegm" | "cudacodec" | "cudafeatures2d" | "cudafilters" | "cudaimgproc" | "cudalegacy" | "cudaobjdetect" | "cudaoptflow" | "cudastereo" | "cudawarping" | "cudev" | "cvv" | "datasets" | "dnn_objdetect" | "dnn_superres" | "dpm" | "face" | "freetype" | "fuzzy" | "hdf" | "hfs" | "img_hash" | "intensity_transform" | "julia" | "line_descriptor" | "mcc" | "optflow" | "ovis" | "phase_unwrapping" | "plot" | "quality" | "rapid" | "reg" | "rgbd" | "saliency" | "sfm" | "shape" | "stereo" | "structured_light" | "superres" | "surface_matching" | "tracking" | "videostab" | "viz" | "wechat_qrcode" | "xfeatures2d" | "ximgproc" | "xobjdetect" | "xphoto" | "apps" | "java_bindings_generator" | "js" | "bindings_generator" | "objc_bindings_generator" | "python3" | "python_bindings_generator" | "ts">;
export {};
