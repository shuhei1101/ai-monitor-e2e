// ─── E2E 専用 seed API ───

/** seed API へのリクエスト内容 */
export type SeedApiRequest = {
  method: "GET" | "POST" | "PUT" | "DELETE";
  /** seed API のベース URL からの相対パス */
  path: string;
  body?: unknown;
};

/** seed API のベース URL を環境変数から取得する */
const seedApiBaseUrl = (): string => {
  const baseUrl = process.env.E2E_SEED_API_BASE_URL;
  if (!baseUrl) {
    throw new Error("環境変数 E2E_SEED_API_BASE_URL が未設定です");
  }
  return baseUrl;
};

/** seed API を呼び出し、レスポンス JSON を返す */
export const seedApiRequest = async <T>({ method, path, body }: SeedApiRequest): Promise<T> => {
  const response = await fetch(`${seedApiBaseUrl()}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`seed API の呼び出しに失敗しました: ${method} ${path} -> ${response.status}`);
  }
  return (await response.json()) as T;
};
