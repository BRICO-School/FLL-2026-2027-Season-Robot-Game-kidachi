# 開発ガイド

## コード自動補正（フォーマット & リント）

- 依存をインストール: `pip install -r requirements.txt`（開発ツール込み）
- まとめて自動補正: `./tools/format.sh`
  - `ruff check --fix` で自動修正をかけつつ静的解析
  - `ruff format` と `black` でコード整形
- 個別で実行する場合
  - リント: `python -m ruff check runs selector.py setup.py utils`
  - フォーマット: `python -m ruff format runs selector.py setup.py utils` または `python -m black runs selector.py setup.py utils`
- Prettier のような JS 向けフォーマッターは現状不要（Python のみのため）。MD の整形も上記で十分です。

### Python バージョン

- 推奨: Python 3.9.6
- pyenv を使う場合

  ```bash
  pyenv install 3.9.6        # 未インストールなら
  pyenv local 3.9.6          # リポジトリ直下で固定
  python -m venv .venv       # 3.9.6 ベースで仮想環境を作成
  ```

## 共通ユーティリティ

- `utils/runtime.py` に実行時ブートストラップを用意。
- `runs/` 配下を単体実行するときは、冒頭でプロジェクトルートを sys.path に追加してから `setup.py` を読み込む。

  ```python
  from pathlib import Path
  import sys

  if __package__ is None:
      sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

  from utils.runtime import ensure_project_root

  ensure_project_root(__file__)
  from setup import initialize_robot
  ```

- 新しい run を作るときは `runs/_template` をコピーして `runs/runXX/` を作り、上記スニペットをそのまま使う。バージョン違いを作る場合は `runs/runXX/` に `mXX_...py` を追加し、`main.py` の `ACTIVE_VARIANT` を切り替える。

- タイムアウト付きの走行やモーター操作は `utils/control.py` の `run_with_timeout()` を使用。
  - `Robot.straight/turn/curve/run_motor` では内部で `run_with_timeout` を利用するため、`timeout=` 引数を指定すればよい。
  - 個別に使う場合:

    ```python
    from utils.control import run_with_timeout

    await run_with_timeout(
        start_fn=lambda: motor.run_angle(200, 180, wait=False),
        done_fn=lambda: motor.control.done(),
        stop_fn=motor.stop,
        timeout_ms=1500,
    )
    ```

- カーブ速度だけを上書きしたい場合は `utils.control.apply_curve_settings` を利用。
  - 例: `apply_curve_settings(robot.settings, speed=200, acceleration=700)`

## ログ出力

- selector 経由で run を実行すると、print 出力がコンソールと `logs/` の両方に保存される。
- ログファイル名: `runXX-YYYYMMDD-HHMMSS.log`（XX は display_number）。
- `logs/` は自動生成され、gitignore 済み。

## ディレクトリと命名

- 競技用コードは `runs/runXX/main.py` を入口とし、`ACTIVE_VARIANT` で `runs/runXX/mXX_...py`（バージョン/作者/日付など）を切り替える。必要に応じて `runs/runXX/variants/` や `runs/runXX/assets/` を作る。
- 旧版は `old/2025-2026/` に保管。現行シーズンの編集は `runs/` 配下のみ。
- 追加の開発メモや手順はこの `docs/` 配下に追記して統一管理する。
