import type { Locator, Page } from "@playwright/test";

/** タスク編集画面のパスを組み立てる */
export const taskEditPath = (taskId: string): string => `/tasks/${taskId}/edit`;

/** タスク編集画面の UI 操作 */
export class TaskEditPage {
  readonly titleInput: Locator;
  readonly bodyInput: Locator;
  readonly saveButton: Locator;
  /** タイトル入力欄の直下に出るインラインエラー */
  readonly titleError: Locator;

  constructor(private readonly page: Page) {
    this.titleInput = page.getByLabel("タイトル");
    this.bodyInput = page.getByLabel("本文");
    this.saveButton = page.getByRole("button", { name: "保存" });
    // インラインエラーは aria-describedby でタイトル入力欄に紐づく前提
    this.titleError = page.getByRole("alert").filter({ hasText: "タイトル" });
  }

  /** タイトル欄を指定値で置き換える */
  async fillTitle(title: string): Promise<void> {
    await this.titleInput.fill(title);
  }

  /** 本文欄を指定値で置き換える */
  async fillBody(body: string): Promise<void> {
    await this.bodyInput.fill(body);
  }

  /** 保存ボタンを押す */
  async save(): Promise<void> {
    await this.saveButton.click();
  }
}
