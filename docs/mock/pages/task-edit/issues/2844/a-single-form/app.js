/* ============================================================================
 * タスク編集（案 A: 単一フォーム）固有のモック挙動。
 * 一覧から渡されたタスク ID の表示と、保存・キャンセル時の一覧への復帰を扱う。
 * ============================================================================ */

/* ---------- 定数 ---------- */
const TASK_LIST_PAGE_PATH = "../../../../task-list/issues/2844/a-row-link/index.html";
const TASK_ID_QUERY_KEY = "id";

/** 一覧から渡されたタスク ID を画面に反映する */
function applyTaskIdFromQuery() {
  const taskId = new URLSearchParams(window.location.search).get(TASK_ID_QUERY_KEY);
  if (!taskId) return;
  document.getElementById("task-id").textContent = taskId;
}

/** 保存で一覧へ戻り、キャンセルは保存せずに一覧へ戻る */
function bindTaskEditActions() {
  document.getElementById("task-save-btn").addEventListener("click", () => {
    const taskId = document.getElementById("task-id").textContent;
    window.location.href = `${TASK_LIST_PAGE_PATH}?saved=${taskId}`;
  });
  document.getElementById("task-cancel-btn").addEventListener("click", () => {
    window.location.href = TASK_LIST_PAGE_PATH;
  });
}

applyTaskIdFromQuery();
bindTaskEditActions();
