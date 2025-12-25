import argparse
import os
from pathlib import Path
from typing import List

# ------------------- 配置 -------------------
IGNORE_DIRS: List[str] = [
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    # ".env",
    # ".env.example",
    "dist",
    "build",
    "out",
]
IGNORE_FILES: List[str] = [
    ".DS_Store",
    "Thumbs.db",
]


def should_ignore(path: Path) -> bool:
    """判断路径是否需要被忽略（目录或文件）"""
    parts = set(p.name for p in path.parents) | {path.name}
    if any(ign in parts for ign in IGNORE_DIRS):
        return True
    if path.is_file() and path.name in IGNORE_FILES:
        return True
    return False


def print_tree(root: Path, prefix: str = "") -> None:
    """递归打印目录树"""
    if not root.is_dir():
        return

    entries = sorted([p for p in root.iterdir() if not should_ignore(p)],
                     key=lambda p: (p.is_file(), p.name.lower()))
    for idx, entry in enumerate(entries):
        connector = "└── " if idx == len(entries) - 1 else "├── "
        print(f"{prefix}{connector}{entry.name}")

        if entry.is_dir():
            extension = "    " if idx == len(entries) - 1 else "│   "
            print_tree(entry, prefix + extension)


def main() -> None:
    parser = argparse.ArgumentParser(description="打印项目目录结构")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="要打印的根目录，默认是当前工作目录",
    )
    args = parser.parse_args()
    root_path = Path(args.path).resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"{root_path} 不是有效的目录")
    print(root_path)
    print_tree(root_path)


if __name__ == "__main__":
    main()
