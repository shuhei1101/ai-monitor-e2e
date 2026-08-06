import { randomUUID } from "node:crypto";

/** 一意化サフィックスの文字数 */
const SUFFIX_LENGTH = 6;

/** 並列実行しても衝突しないよう、ラベルへ一意なサフィックスを付ける */
export const uniqueLabel = (prefix: string): string =>
  `${prefix}-${randomUUID().replaceAll("-", "").slice(0, SUFFIX_LENGTH)}`;
