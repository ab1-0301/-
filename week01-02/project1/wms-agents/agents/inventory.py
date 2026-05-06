"""Inventory Agent — queries warehouse inventory data."""
from __future__ import annotations

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INVENTORY_FILE = DATA_DIR / "inventory.json"


def load_inventory() -> dict:
    """Load inventory data from JSON file."""
    with open(INVENTORY_FILE, encoding="utf-8") as f:
        return json.load(f)


def query_stock(category: str | None = None) -> str:
    """Query stock levels. category: A, B, C, or None for all."""
    data = load_inventory()
    if category and category.upper() in data["categories"]:
        cat = data["categories"][category.upper()]
        items = cat["items"]
        result = f"类别 {category.upper()} ({cat['description']}):\n"
        for code, info in items.items():
            result += f"  {code} {info['name']}: {info['quantity']}{info['unit']} @ {info['location']}\n"
        return result
    elif category:
        return f"错误：未找到类别 '{category}'。可用类别: A, B, C"

    result = "===== 全部库存 =====\n"
    for cat_key, cat_data in data["categories"].items():
        result += f"\n[{cat_key}] {cat_data['description']}:\n"
        for code, info in cat_data["items"].items():
            result += f"  {code} {info['name']}: {info['quantity']}{info['unit']} @ {info['location']}\n"
    return result


def query_alerts() -> str:
    """Query low stock and overstock alerts."""
    data = load_inventory()
    alerts = data["alerts"]
    threshold_low = alerts["low_stock_threshold"]
    threshold_high = alerts["overstock_threshold"]

    all_items = {}
    for cat in data["categories"].values():
        all_items.update(cat["items"])

    result = f"===== 库存预警 =====\n"
    result += f"低库存阈值: < {threshold_low}\n"
    result += f"高库存阈值: > {threshold_high}\n\n"

    low = [all_items[i] for i in alerts["low_stock_items"] if i in all_items]
    if low:
        result += "--- 低库存商品 ---\n"
        for item in low:
            result += f"  {item['name']}: 仅剩 {item['quantity']}{item['unit']}\n"

    over = [all_items[i] for i in alerts["overstock_items"] if i in all_items]
    if over:
        result += "\n--- 高库存商品 ---\n"
        for item in over:
            result += f"  {item['name']}: {item['quantity']}{item['unit']}（库存过多）\n"

    if not low and not over:
        result += "所有库存正常\n"
    return result


def search_product(keyword: str) -> str:
    """Search products by keyword in name."""
    data = load_inventory()
    keyword = keyword.lower()
    results = []
    for cat_key, cat_data in data["categories"].items():
        for code, info in cat_data["items"].items():
            if keyword in info["name"].lower():
                results.append((cat_key, code, info))

    if not results:
        return f"未找到包含 '{keyword}' 的商品"

    result = f"===== 搜索: {keyword} =====\n"
    for cat_key, code, info in results:
        result += f"  [{cat_key}] {code} {info['name']}: {info['quantity']}{info['unit']} @ {info['location']}\n"
    return result
