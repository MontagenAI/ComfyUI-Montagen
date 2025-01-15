import type * as openCV from '../..';
export interface TextParams {
    fontType: number;
    fontSize: number;
    thickness: number;
    lineType: number;
}
export interface TextLines {
    text: string;
}
export interface TextDimention {
    width: number;
    height: number;
    baseLine: number;
}
export default function (cv: typeof openCV): void;
//# sourceMappingURL=drawUtils.d.ts.map