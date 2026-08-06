/**
 * タスク一覧（案 a-row-edit-button）のモック挙動。
 * 行の編集ボタンからタスク編集画面へ遷移し、保存して戻ってきたときは編集結果を一覧へ反映する。
 */

/** タスク編集画面の相対パス */
const EDIT_PAGE_PATH = "../../../task-edit/2933/a-single-column-form/index.html";

/** トーストの表示時間（ミリ秒） */
const TOAST_DISPLAY_MS = 2400;

/** 保存直後の行を強調表示する時間（ミリ秒） */
const HIGHLIGHT_MS = 2400;

/** 行の編集ボタンに、対象タスク ID 付きで編集画面へ遷移する動きを付ける */
function bindEditButtons() {
  document.querySelectorAll("[data-edit-target]").forEach((button) => {
    button.addEventListener("click", () => {
      const taskId = button.dataset.editTarget;
      const row = document.querySelector(`tr[data-id="${taskId}"]`);
      // 編集画面の初期値として、いま一覧に出ている値をそのまま渡す
      const params = new URLSearchParams({
        id: taskId,
        title: row.querySelector('[data-field="title"]').textContent,
        body: row.querySelector('[data-field="body"]').textContent,
      });
      window.location.href = `${EDIT_PAGE_PATH}?${params}`;
    });
  });
}

/** 編集画面から saved 付きで戻ってきたとき、該当行を編集後の内容に差し替える */
function applySavedResult() {
  const params = new URLSearchParams(window.location.search);
  const savedId = params.get("saved");
  if (!savedId) return;

  const row = document.querySelector(`tr[data-id="${savedId}"]`);
  row.querySelector('[data-field="title"]').textContent = params.get("title");
  row.querySelector('[data-field="body"]').textContent = params.get("body");
  row.querySelector('[data-field="updated-at"]').textContent = params.get("updatedAt");

  // 更新された行が一目で分かるよう、一定時間だけ背景を変える
  row.style.background = "rgba(22, 163, 74, 0.12)";
  window.setTimeout(() => {
    row.style.background = "";
  }, HIGHLIGHT_MS);

  showSavedToast(`${savedId} を保存しました（モック）`);
}

/** 画面下部のトーストを一定時間表示する */
function showSavedToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.hidden = false;
  window.setTimeout(() => {
    toast.hidden = true;
  }, TOAST_DISPLAY_MS);
}

bindEditButtons();
applySavedResult();
