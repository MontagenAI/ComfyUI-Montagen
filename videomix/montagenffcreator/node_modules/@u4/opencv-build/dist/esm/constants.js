export class Constant {
    constructor(builder) {
        this.builder = builder;
        this.opencvRepoUrl = 'https://github.com/opencv/opencv.git';
        // opencvRepoUrl = 'c:/cache/opencv'
        this.opencvContribRepoUrl = 'https://github.com/opencv/opencv_contrib.git';
        // opencvContribRepoUrl = 'c:/cache/opencv_contrib'
        //   opencvModules = opencvModules;
        this.cmakeVsCompilers = {
            '10': 'Visual Studio 10 2010',
            '11': 'Visual Studio 11 2012',
            '12': 'Visual Studio 12 2013',
            '14': 'Visual Studio 14 2015',
            '15': 'Visual Studio 15 2017',
            '16': 'Visual Studio 16 2019',
            '17': 'Visual Studio 17 2022',
        };
        this.cmakeArchs = { 'x64': ' Win64', 'ia32': '', 'arm': ' ARM' };
    }
}
//# sourceMappingURL=constants.js.map