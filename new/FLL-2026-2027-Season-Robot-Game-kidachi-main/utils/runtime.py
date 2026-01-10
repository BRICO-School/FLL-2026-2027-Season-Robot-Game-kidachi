"""
実行時のブートストラップ用ユーティリティ。

主に次の目的で使用します:
- `runs/` 配下のスクリプトを単体実行する際にプロジェクトルートを sys.path に追加する
- プロジェクトルート Path を取得する
"""

import sys
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def ensure_project_root(current_file: PathLike) -> Path:
    """
    スクリプトの位置からプロジェクトルートを探索し、sys.path に追加して返す。

    探索基準:
    - pyproject.toml または .git があるディレクトリをルートとみなす
    - 見つからない場合は最上位ディレクトリを返す
    """
    path = Path(current_file).resolve()
    candidates = [path.parent, *path.parents]

    project_root = None
    for candidate in candidates:
        if (candidate / "pyproject.toml").exists() or (candidate / ".git").exists():
            project_root = candidate
            break

    if project_root is None:
        project_root = path.parents[-1]

    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    return project_root
