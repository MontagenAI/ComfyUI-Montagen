/// <reference types="node" />
/// <reference types="node" />
import child_process from 'child_process';
/**
 * excape spaces for shell execution
 * @param txt text to escape
 * @returns a shell no spaced parameter
 */
export declare const protect: (txt: string) => string;
export declare function toExecCmd(bin: string, args: string[]): string;
export declare function highlight(text: string): string;
export declare function light(text: string): string;
export declare function formatRed(text: string): string;
export declare function formatNumber(text: string): string;
export declare function exec(cmd: string, options?: child_process.ExecOptions): Promise<string>;
export declare function execSync(cmd: string, options?: child_process.ExecOptions): string;
/**
 * only used by findVs2017
 */
export declare function execFile(cmd: string, args: string[], options?: child_process.ExecOptions): Promise<string>;
export declare function spawn(cmd: string, args: string[], options: child_process.ExecOptions, filters?: {
    err?: (data: Buffer) => Buffer | null;
    out?: (data: Buffer) => Buffer | null;
}): Promise<string>;
export declare function requireGit(): Promise<void>;
export declare function requireCmake(): Promise<void>;
/**
 * looks for cuda lib
 * @returns
 */
export declare function isCudaAvailable(): boolean;
