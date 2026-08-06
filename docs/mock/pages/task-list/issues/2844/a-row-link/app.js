/* ============================================================================
 * タスク一覧（案 A: 行クリック遷移）固有のモック挙動。
 * 共通の app.js が持つ Mock demo 用ハンドラは #customer-table を対象にしているため、
 * タスク一覧の行遷移はこのファイルで組み立てる。
 * ============================================================================ */

/* ---------- 定数 ---------- */
const TASK_EDIT_PAGE_PATH = "../../../../task-edit/issues/2844/a-single-form/index.html";
const SAVED_TASK_QUERY_KEY = "saved";

/** 行クリックでタスク編集画面へ遷移する */
function bindTaskRowLink() {
  document.querySelectorAll("#task-table tbody tr").forEach((row) => {
    row.addEventListener("click", () => {
      window.location.href = `${TASK_EDIT_PAGE_PATH}?id=${row.dataset.id}`;
    });
  });
}

/** 編集画面から保存で戻ってきたときに保存完了のトーストを出す */
function showSavedTaskToast() {
  const savedId = new URLSearchParams(window.location.search).get(SAVED_TASK_QUERY_KEY);
  if (!savedId) return;
  showToast(`${savedId} の変更を保存しました（モック）`);
}

bindTaskRowLink();
showSavedTaskToast();
