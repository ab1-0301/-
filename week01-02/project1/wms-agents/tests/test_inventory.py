"""Unit tests for inventory agent functions."""
from agents.inventory import query_stock, query_alerts, search_product


def test_query_stock_all():
    result = query_stock()
    assert "全部库存" in result
    assert "笔记本电脑" in result
    assert "A001" in result
    assert "C004" in result


def test_query_stock_category():
    result = query_stock("A")
    assert "类别 A" in result
    assert "笔记本电脑" in result
    assert "显示器" in result
    assert "USB-C" not in result


def test_query_stock_invalid_category():
    result = query_stock("X")
    assert "未找到类别" in result


def test_query_alerts():
    result = query_alerts()
    assert "库存预警" in result
    assert "网络交换机" in result  # low stock item (B004)
    assert "扎带" in result  # overstock item (C002)


def test_search_product_found():
    result = search_product("键盘")
    assert "机械键盘" in result
    assert "A003" in result


def test_search_product_not_found():
    result = search_product("服务器")
    assert "未找到" in result
