#!/usr/bin/env python3
"""
batch_rename.py — 批量重命名文件工具

支持功能：
  - 添加前缀/后缀
  - 替换文本（普通/正则）
  - 按序号重命名（可自定义格式）
  - 修改扩展名
  - 预览模式（不实际执行，只显示改动计划）

用法示例：
  python batch_rename.py /path/to/files --prefix "project_"
  python batch_rename.py /path/to/files --replace "old" "new"
  python batch_rename.py /path/to/files --number --format "image_{:03d}"
  python batch_rename.py /path/to/files --ext ".md"
  python batch_rename.py /path/to/files --regex "(\\d+)" "day\\1" --dry-run
"""

import argparse
import os
import re
import sys
from pathlib import Path


def collect_files(directory: Path, pattern: str, recursive: bool):
    """收集待处理的文件"""
    if recursive:
        files = list(directory.rglob(pattern))
    else:
        files = list(directory.glob(pattern))
    # 只保留文件，排除目录
    return [f for f in files if f.is_file()]


def apply_rename(files: list[Path], new_names: list[str], dry_run: bool):
    """执行或预览重命名"""
    if len(files) != len(new_names):
        print("错误：文件名列表长度不匹配", file=sys.stderr)
        sys.exit(1)

    pairs = []
    for old, new in zip(files, new_names):
        new_path = old.parent / new
        if new_path.exists() and old.name != new:
            print(f"  ⚠ 跳过：{new} 已存在")
            continue
        if old.name == new:
            print(f"  - 不变：{old.name}")
            continue
        pairs.append((old, new_path))

    if not pairs:
        print("没有需要重命名的文件。")
        return

    if dry_run:
        print(f"\n[预览模式] 将重命名 {len(pairs)} 个文件：\n")
        for old, new in pairs:
            print(f"  {old.name}  →  {new.name}")
        print(f"\n共 {len(pairs)} 个文件将被修改。使用 --no-dry-run 实际执行。")
        return

    print(f"\n正在重命名 {len(pairs)} 个文件...\n")
    for old, new in pairs:
        old.rename(new)
        print(f"  ✓ {old.name}  →  {new.name}")
    print(f"\n完成！修改了 {len(pairs)} 个文件。")


def operation_prefix(files: list[Path], args) -> list[str]:
    return [args.prefix + f.name for f in files]


def operation_suffix(files: list[Path], args) -> list[str]:
    stem = f.stem
    ext = f.suffix
    return [stem + args.suffix + ext for f in files]


def operation_replace(files: list[Path], args) -> list[str]:
    return [f.name.replace(args.replace_old, args.replace_new) for f in files]


def operation_regex(files: list[Path], args) -> list[str]:
    return [re.sub(args.regex_pattern, args.regex_repl, f.name) for f in files]


def operation_number(files: list[Path], args) -> list[str]:
    result = []
    for i, f in enumerate(files, start=args.start):
        ext = f.suffix if not args.ext else ("." + args.ext.lstrip("."))
        new_stem = args.format.format(i)
        result.append(new_stem + ext)
    return result


def operation_ext(files: list[Path], args) -> list[str]:
    new_ext = "." + args.ext.lstrip(".")
    return [f.stem + new_ext for f in files]


def main():
    parser = argparse.ArgumentParser(
        description="批量重命名文件工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  %(prog)s . --prefix "backup_"
  %(prog)s . --suffix "_v2" --ext .md
  %(prog)s . --replace "draft" "final"
  %(prog)s . --number --format "img_{:03d}" --start 1
  %(prog)s . --regex "screenshot_(\\d+)" "ss_\\1" --dry-run
  %(prog)s . --ext .txt --recursive
        """,
    )

    # 通用参数
    parser.add_argument("directory", nargs="?", default=".", help="目标目录（默认当前目录）")
    parser.add_argument("--pattern", default="*", help="文件匹配模式（默认 *）")
    parser.add_argument("--recursive", "-r", action="store_true", help="递归子目录")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="预览模式（默认启用）")
    parser.add_argument("--no-dry-run", action="store_false", dest="dry_run",
                        help="实际执行重命名")

    # 操作模式（互斥组）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prefix", help="添加前缀")
    group.add_argument("--suffix", help="添加后缀（扩展名前）")
    group.add_argument("--replace", nargs=2, metavar=("OLD", "NEW"),
                       help="替换文件名中的文本")
    group.add_argument("--regex", nargs=2, metavar=("PATTERN", "REPL"),
                       help="用正则替换文件名")
    group.add_argument("--number", action="store_true",
                       help="按序号重命名（配合 --format / --start / --ext）")
    group.add_argument("--ext", help="修改扩展名")

    # 序号模式专用参数
    parser.add_argument("--format", default="{:03d}", help="序号格式（默认 {:03d}）")
    parser.add_argument("--start", type=int, default=1, help="起始编号（默认 1）")

    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    if not directory.is_dir():
        print(f"错误：目录不存在 {directory}", file=sys.stderr)
        sys.exit(1)

    files = collect_files(directory, args.pattern, args.recursive)
    if not files:
        print(f"在 {directory} 中未匹配到文件（模式：{args.pattern}）")
        return

    files.sort()  # 统一排序，保证顺序可预测

    # 选择操作
    if args.prefix:
        new_names = operation_prefix(files, args)
    elif args.suffix:
        new_names = operation_suffix(files, args)
    elif args.replace:
        new_names = operation_replace(files, args)
    elif args.regex:
        new_names = operation_regex(files, args)
    elif args.number:
        new_names = operation_number(files, args)
    elif args.ext:
        new_names = operation_ext(files, args)
    else:
        print("错误：未指定操作", file=sys.stderr)
        sys.exit(1)

    apply_rename(files, new_names, args.dry_run)


if __name__ == "__main__":
    main()
