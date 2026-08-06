import { seedApiRequest } from "../helpers/db";
import { uniqueLabel } from "../helpers/unique";

/** seed API が返すユーザーレコード */
export type UserRow = {
  id: string;
  name: string;
};

/** createUser の引数 */
export type CreateUserInput = {
  name: string;
};

/** ログイン中ユーザーを 1 件作成する */
export const createUser = async ({ name }: CreateUserInput): Promise<UserRow> =>
  seedApiRequest<UserRow>({
    method: "POST",
    path: "/users",
    body: { name: uniqueLabel(name) },
  });
