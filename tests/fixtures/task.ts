import { seedApiRequest } from "../helpers/db";
import { uniqueLabel } from "../helpers/unique";

/** seed API が返すタスクレコード */
export type TaskRow = {
  id: string;
  ownerId: string;
  title: string;
  body: string;
};

/** createTask の引数 */
export type CreateTaskInput = {
  /** 所有者となるユーザーの ID */
  ownerId: string;
  title: string;
  body: string;
};

/** 指定ユーザーが所有するタスクを 1 件作成する */
export const createTask = async ({ ownerId, title, body }: CreateTaskInput): Promise<TaskRow> =>
  seedApiRequest<TaskRow>({
    method: "POST",
    path: "/tasks",
    body: { ownerId, title: uniqueLabel(title), body: uniqueLabel(body) },
  });

/** DB に保存されているタスクレコードを取得する */
export const findTask = async ({ id }: { id: string }): Promise<TaskRow> =>
  seedApiRequest<TaskRow>({ method: "GET", path: `/tasks/${id}` });
