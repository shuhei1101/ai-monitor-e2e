/* ============================================================================
 * タスク編集 案 A: 下部固定アクション
 *
 * 保存 / 取り消し / 確認ダイアログの見え方を確認するためのモック用スクリプト。
 * 実 API は呼ばず、デモ用スイッチの選択値で成功・失敗を切り替える。
 * トースト表示は共通 assets/app.js の showToast を使う。
 * ============================================================================ */

/* 保存 API の応答待ちを再現する時間 */
const SAVE_PENDING_MS = 900;

/* 変更有無の判定に使う値。保存が成功した時点で現在値に更新する */
const savedValues = { title: "", body: "" };

/** 入力欄の現在値を保存済みの値として記録する */
function captureSavedValues() {
  savedValues.title = document.getElementById("task-title").value;
  savedValues.body = document.getElementById("task-body").value;
}

/** 入力値が保存済みの値から変わっているかを返す */
function hasChanges() {
  return (
    document.getElementById("task-title").value !== savedValues.title ||
    document.getElementById("task-body").value !== savedValues.body
  );
}

/** バナーと項目単位のエラー表示をすべて消す */
function clearErrors() {
  document.getElementById("error-banner").hidden = true;
  document.getElementById("title-error").hidden = true;
  document.getElementById("body-error").hidden = true;
  document.getElementById("task-title").classList.remove("invalid");
  document.getElementById("task-body").classList.remove("invalid");
}

/** API のバリデーションエラーを受け取ったときの表示を出す */
function showValidationError() {
  document.getElementById("error-banner-text").textContent =
    "タイトルの文字数が上限を超えています。内容を修正して再度保存してください。";
  document.getElementById("error-banner").hidden = false;
  document.getElementById("title-error").hidden = false;
  document.getElementById("task-title").classList.add("invalid");
}

/** 保存中の見た目に切り替えて二重送信を防ぐ */
function setSaving(saving) {
  const saveBtn = document.getElementById("save-edit");
  const cancelBtn = document.getElementById("cancel-edit");
  const status = document.getElementById("action-status");

  saveBtn.disabled = saving;
  cancelBtn.disabled = saving;
  saveBtn.textContent = saving ? "保存中..." : "保存";
  status.textContent = saving ? "保存中..." : "";
}

/** 保存ボタンの挙動を紐付ける */
function bindSave() {
  document.getElementById("save-edit").addEventListener("click", () => {
    clearErrors();
    setSaving(true);

    window.setTimeout(() => {
      setSaving(false);
      // デモ用スイッチで API の応答を切り替える
      if (document.getElementById("demo-save-result").value === "error") {
        showValidationError();
        showToast("保存に失敗しました（モック）");
        return;
      }
      captureSavedValues();
      showToast("保存しました。タスク一覧画面へ戻ります（モック）");
    }, SAVE_PENDING_MS);
  });
}

/** 取り消しボタンと確認ダイアログの挙動を紐付ける */
function bindCancel() {
  const modal = document.getElementById("discard-modal");

  document.getElementById("cancel-edit").addEventListener("click", () => {
    // 変更がないときは確認せずそのまま一覧へ戻る
    if (!hasChanges()) {
      showToast("タスク一覧画面へ戻ります（モック）");
      return;
    }
    modal.hidden = false;
  });

  document.getElementById("discard-cancel").addEventListener("click", () => {
    modal.hidden = true;
  });

  document.getElementById("discard-ok").addEventListener("click", () => {
    modal.hidden = true;
    showToast("編集を破棄してタスク一覧画面へ戻ります（モック）");
  });
}

/** 入力し直したタイミングでエラー表示を消す */
function bindErrorReset() {
  document.getElementById("task-title").addEventListener("input", clearErrors);
  document.getElementById("task-body").addEventListener("input", clearErrors);
}

function init() {
  captureSavedValues();
  bindSave();
  bindCancel();
  bindErrorReset();
}

document.addEventListener("DOMContentLoaded", init);
