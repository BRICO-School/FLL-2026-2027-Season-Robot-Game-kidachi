# ファイル／フォルダ構成の方針

結論: **run ごとにディレクトリを切り、入口は `runXX/main.py` で統一する。**  
これにより採用版と試作・作者別・計測データを同じフォルダに束ね、見通しと拡張性を両立します。

---

## 推奨ツリー（デフォルト）

```
project/
  requirements.txt          # ランタイム依存
  docs/
    DEV_GUIDE.md
    STRUCTURE.md
  old/                    # 旧シーズン

  setup.py                  # ロボット初期化
  selector.py               # run を選択・実行
  utils/
    runtime.py              # 単体実行時の sys.path 解決
    control.py              # タイムアウト制御
    logger.py               # ログ出力（tee）

  runs/
    __init__.py
    run01/
      main.py               # 採用バージョンを指定するハブ（ACTIVE_VARIANTを切り替える）
      m08_m06_m05.py        # 具体的な実装（バージョン・作者・日付などで複数置ける）
      __init__.py
      variants/             # 必要に応じて
      assets/               # 計測データやメモを置く場所
    run02/
      main.py
      m09_m07.py
      __init__.py
    run03/
      main.py
      m10_m11.py
      __init__.py
    run04/
      main.py
      m12.py
      __init__.py
    run05/
      main.py
      m01_m02_kanna.py
      __init__.py
    run06/
      main.py
      m13_m03.py
      __init__.py
    _template/              # 新規作成用テンプレート（必要に応じて複製）
      main.py
      __init__.py
```

### この形が強い理由

- run ごとにファイルを束ねるので一覧性が高い
- 試作・作者別・計測データを同じフォルダに置ける
- selector 側は **「入口は run() で統一」**しておけば揺れない

---

## selector / import 周りのベストプラクティス

1) selector は「全 run をベタ import」しない方が安定（重くなったら遅延 import を検討）。  
   - 「表示番号 → モジュールパス」のレジストリだけ置き、必要なときに importlib で読み込む。

2) run の公開インターフェースを統一  
   - 入口関数名を固定（例: `run(hub, robot, ...)`）  
   - 追加情報は定数で管理（例: `TITLE`, `MISSIONS`, `AUTHOR`）  
   - 初期化は selector/setup に寄せ、run 側で初期化しない。

---

## runtime.py（sys.path 解決）について

理想は `python -m selector` のようにモジュール実行に寄せ、`sys.path` いじりを減らすこと。  
競技現場で「run ファイル単体実行」が必要なら、`runtime.py` に閉じ込め、run 側での直接編集を避ける。
