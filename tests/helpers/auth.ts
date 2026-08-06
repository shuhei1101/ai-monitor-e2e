import type { Page } from "@playwright/test";
import { seedApiRequest } from "./db";

/** seed API が発行するセッション */
type SessionRow = {
  token: string;
};

/** セッショントークンを保持する Cookie 名 */
const SESSION_COOKIE_NAME = "session";

/** loginAs の引数 */
export type LoginAsInput = {
  page: Page;
  /** ログインさせるユーザーの ID */
  userId: string;
};

/** アプリのベース URL を環境変数から取得する */
const appBaseUrl = (): string => {
  const baseUrl = process.env.E2E_BASE_URL;
  if (!baseUrl) {
    throw new Error("環境変数 E2E_BASE_URL が未設定です");
  }
  return baseUrl;
};

/** 指定ユーザーのセッションを発行し、ブラウザをログイン済みにする */
export const loginAs = async ({ page, userId }: LoginAsInput): Promise<void> => {
  const session = await seedApiRequest<SessionRow>({
    method: "POST",
    path: "/sessions",
    body: { userId },
  });
  await page.context().addCookies([
    { name: SESSION_COOKIE_NAME, value: session.token, url: appBaseUrl() },
  ]);
};
