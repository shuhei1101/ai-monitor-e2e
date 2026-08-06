import { expect, test } from "@playwright/test";
import { createTask, createUser, findTask } from "../../fixtures";
import { loginAs } from "../../helpers/auth";
import { uniqueLabel } from "../../helpers/unique";
import { TaskEditPage, taskEditPath } from "../../pages/task_edit_page";
import { TaskListPage } from "../../pages/task_list_page";

/** 成功トーストが表示され続ける時間（ミリ秒） */
const TOAST_VISIBLE_MS = 3000;

/** トーストの消滅判定に持たせる前後の余裕（ミリ秒） */
const TOAST_CHECK_MARGIN_MS = 500;

test.describe("タスク編集", () => {
  // 一覧から対象タスクを選び、タイトルと本文を編集して保存する（正常系）
  test("test_normal", async ({ page }) => {
    // 準備
    const user = await createUser({ name: "userA" });
    await loginAs({ page, userId: user.id });
    const task = await createTask({
      ownerId: user.id,
      title: "編集前のタイトル",
      body: "編集前の本文",
    });
    const editedTitle = uniqueLabel("編集後のタイトル");
    const editedBody = uniqueLabel("編集後の本文");
    const listPage = new TaskListPage(page);
    const editPage = new TaskEditPage(page);

    // 実行
    await listPage.goto();
    await listPage.openTask(task.title);
    await expect(editPage.titleInput).toHaveValue(task.title);
    await expect(editPage.bodyInput).toHaveValue(task.body);
    await editPage.fillTitle(editedTitle);
    await editPage.fillBody(editedBody);
    await editPage.save();

    // 検証
    await expect(listPage.taskLink(editedTitle)).toBeVisible();
    await expect(listPage.taskBody(editedBody)).toBeVisible();
    await expect(listPage.toast).toBeVisible();
    // 表示時間の直前ではまだ残っており、そこから消えることで「3 秒後に消える」を確認する
    await page.waitForTimeout(TOAST_VISIBLE_MS - TOAST_CHECK_MARGIN_MS);
    await expect(listPage.toast).toBeVisible();
    await expect(listPage.toast).toBeHidden({ timeout: TOAST_CHECK_MARGIN_MS * 2 });
    const savedTask = await findTask({ id: task.id });
    expect(savedTask.title).toBe(editedTitle);
    expect(savedTask.body).toBe(editedBody);
  });

  // タイトルを空にして保存すると、インラインエラーが出て編集画面にとどまる（異常系）
  test("test_error_when_title_empty", async ({ page }) => {
    // 準備
    const user = await createUser({ name: "userA" });
    await loginAs({ page, userId: user.id });
    const task = await createTask({
      ownerId: user.id,
      title: "編集前のタイトル",
      body: "編集前の本文",
    });
    const listPage = new TaskListPage(page);
    const editPage = new TaskEditPage(page);

    // 実行
    await listPage.goto();
    await listPage.openTask(task.title);
    await expect(editPage.titleInput).toHaveValue(task.title);
    await editPage.fillTitle("");
    await editPage.save();

    // 検証
    await expect(editPage.titleError).toBeVisible();
    await expect(page).toHaveURL(new RegExp(`${taskEditPath(task.id)}$`));
    const savedTask = await findTask({ id: task.id });
    expect(savedTask.title).toBe(task.title);
    expect(savedTask.body).toBe(task.body);
  });
});
