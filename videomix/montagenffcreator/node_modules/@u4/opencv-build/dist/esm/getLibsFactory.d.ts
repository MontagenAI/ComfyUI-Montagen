import OpenCVBuilder from './OpenCVBuilder.js';
import type { OpencvModule } from './types.js';
import { OpencvModulesType } from './misc.js';
export declare class getLibsFactory {
    private builder;
    libFiles: string[];
    syncPath: boolean;
    constructor(builder: OpenCVBuilder);
    /**
     * list en cache file in lib folder
     * @returns files in lib directory
     */
    private listFiles;
    /**
     * lib files are prefixed differently on Unix / Windows base system.
     * @returns current OS prefix
     */
    get getLibPrefix(): string;
    /**
     * @returns lib extention based on current OS
     */
    get getLibSuffix(): 'lib' | 'dylib' | 'so';
    /**
     * build a regexp matching os lib file
     * @param opencvModuleName
     * @returns
     */
    getLibNameRegex(opencvModuleName: string): RegExp;
    /**
     * find a lib
     */
    resolveLib(opencvModuleName: OpencvModulesType): string;
    /**
     * Match lib file names in a folder, was part of resolveLib, but was splitted for easy testing
     * @param opencvModuleName openCV module name
     * @param libDir library directory
     * @param libFiles files in lib directory
     * @returns full path to looked up lib file
     */
    matchLib(opencvModuleName: string, libDir: string, libFiles: string[]): string;
    getLibs(): OpencvModule[];
}
