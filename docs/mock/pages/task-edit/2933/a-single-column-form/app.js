/**
 * タスク編集（案 a-single-column-form）のモック挙動。
 * 一覧から渡された値をフォームの初期値にし、保存・キャンセルのどちらでも一覧へ戻る。
 */

/** タスク一覧画面の相対パス */
const LIST_PAGE_PATH = "../../../task-list/2933/a-row-edit-button/index.html";

/** 更新日時の表示タイムゾーン */
const DISPLAY_TIME_ZONE = "Asia/Tokyo";

/** 一覧から渡されたタスクの値をフォームへ流し込む */
function applyIncomingTask() {
  const params = new URLSearchParams(window.location.search);
  const taskId = params.get("id");
  // 一覧を経由せず直接開いた場合は、HTML に書いてあるサンプル値をそのまま使う
  if (!taskId) return;

  document.getElementById("task-id").textContent = taskId;
  document.getElementById("title").value = params.get("title");
  document.getElementById("body").value = params.get("body");
}

/** 保存・キャンセルの遷移を組み立てる */
function bindFormActions() {
  document.getElementById("save-btn").addEventListener("click", () => {
    const params = new URLSearchParams({
      saved: document.getElementById("task-id").textContent,
      title: document.getElementById("title").value,
      body: document.getElementById("body").value,
      updatedAt: formatNowInJst(),
    });
    window.location.href = `${LIST_PAGE_PATH}?${params}`;
  });

  document.getElementById("cancel-btn").addEventListener("click", () => {
    window.location.href = LIST_PAGE_PATH;
  });
}

/** 現在時刻を一覧の更新日時列と同じ JST 表記にする */
function formatNowInJst() {
  const parts = new Intl.DateTimeFormat("ja-JP", {
    timeZone: DISPLAY_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).formatToParts(new Date());
  const value = (type) => parts.find((part) => part.type === type).value;
  return `${value("year")}-${value("month")}-${value("day")} ${value("hour")}:${value("minute")} JST`;
}

applyIncomingTask();
bindFormActions();
