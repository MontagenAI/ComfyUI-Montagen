export interface PathVersion {
    version: number;
    path: string;
}
/**
 * @returns all MSBuild.exe version in PROGRAM FILES most recent first.
 */
export declare function findMSBuild(): Promise<PathVersion[]>;
