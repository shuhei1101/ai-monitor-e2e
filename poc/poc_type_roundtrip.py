"""str / int / None が挿入時と同じ型で取り出せるかを検証する。"""
from __future__ import annotations

from _schema import INSERT_TASK_SQL, build_logger, open_memory_db

# (id, title, content, priority) の組。content と priority に None を混ぜて往復を見る
CASES: tuple[tuple[str, str, str | None, int | None], ...] = (
    ("t1", "買い物", "牛乳", 1),
    ("t2", "本文なし", None, 2),
    ("t3", "優先度なし", "後で決める", None),
)

logger = build_logger(__name__)


def main() -> None:
    """各ケースを挿入し、挿入値と取得値の型名を突き合わせてログへ出す。"""
    conn = open_memory_db()
    conn.executemany(INSERT_TASK_SQL, CASES)

    for case in CASES:
        task_id = case[0]
        fetched = conn.execute(
            "SELECT id, title, content, priority FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        inserted_types = [type(value).__name__ for value in case]
        fetched_types = [type(value).__name__ for value in fetched]
        # 型名の並びが一致していれば往復で型が保たれている
        matched = inserted_types == fetched_types
        logger.info(f"{task_id}: 挿入 {inserted_types} / 取得 {fetched_types} / 一致 {matched}")
        logger.info(f"{task_id}: 取得値 {fetched}")

    conn.close()


if __name__ == "__main__":
    main()
