import type { Locator, Page } from "@playwright/test";

/** タスク一覧画面のパス */
export const TASK_LIST_PATH = "/tasks";

/** タスク一覧画面の UI 操作 */
export class TaskListPage {
  /** 保存結果を知らせるトースト */
  readonly toast: Locator;

  constructor(private readonly page: Page) {
    this.toast = page.getByRole("status");
  }

  /** タスク一覧画面を開く */
  async goto(): Promise<void> {
    await this.page.goto(TASK_LIST_PATH);
  }

  /** 一覧に並ぶタスクのリンク */
  taskLink(title: string): Locator {
    return this.page.getByRole("link", { name: title });
  }

  /** 一覧に表示されるタスクの本文 */
  taskBody(body: string): Locator {
    return this.page.getByText(body);
  }

  /** 対象タスクを選択して編集画面へ遷移する */
  async openTask(title: string): Promise<void> {
    await this.taskLink(title).click();
  }
}
