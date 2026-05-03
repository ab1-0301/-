"""智能仓储管理系统 — Flask Web 版"""

import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "wms2026"
DB_PATH = os.path.join(os.path.dirname(__file__), "warehouse.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            spec TEXT DEFAULT '',
            unit TEXT DEFAULT '个',
            quantity INTEGER DEFAULT 0,
            location TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            material_code TEXT NOT NULL,
            material_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            operator TEXT DEFAULT '',
            note TEXT DEFAULT '',
            time TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


# ── 首页 ──
@app.route("/")
def index():
    conn = get_db()
    materials = conn.execute("SELECT * FROM materials ORDER BY code").fetchall()
    conn.close()
    return render_template("index.html", materials=materials)


# ── 入库 ──
@app.route("/inbound", methods=["GET", "POST"])
def inbound():
    if request.method == "POST":
        code = request.form["code"].strip()
        name = request.form["name"].strip()
        spec = request.form.get("spec", "").strip()
        unit = request.form.get("unit", "个").strip()
        qty = int(request.form["quantity"])
        location = request.form.get("location", "").strip()
        operator = request.form.get("operator", "").strip()

        if qty <= 0:
            flash("数量必须大于0", "error")
            return redirect(url_for("inbound"))

        conn = get_db()
        existing = conn.execute("SELECT * FROM materials WHERE code=?", (code,)).fetchone()
        if existing:
            conn.execute("UPDATE materials SET quantity=quantity+?, location=? WHERE code=?",
                         (qty, location or existing["location"], code))
        else:
            conn.execute("INSERT INTO materials (code, name, spec, unit, quantity, location) VALUES (?, ?, ?, ?, ?, ?)",
                         (code, name, spec, unit, qty, location))

        conn.execute("INSERT INTO transactions (type, material_code, material_name, quantity, operator, time) VALUES (?, ?, ?, ?, ?, ?)",
                     ("入库", code, name, qty, operator, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        conn.close()
        flash(f"{name} × {qty} 入库成功", "success")
        return redirect(url_for("index"))
    return render_template("inbound.html")


# ── 出库 ──
@app.route("/outbound", methods=["GET", "POST"])
def outbound():
    conn = get_db()
    materials = conn.execute("SELECT * FROM materials ORDER BY code").fetchall()
    conn.close()
    if request.method == "POST":
        code = request.form["code"].strip()
        qty = int(request.form["quantity"])
        operator = request.form.get("operator", "").strip()

        if qty <= 0:
            flash("数量必须大于0", "error")
            return redirect(url_for("outbound"))

        conn = get_db()
        mat = conn.execute("SELECT * FROM materials WHERE code=?", (code,)).fetchone()
        if not mat:
            flash("物资编码不存在", "error")
            conn.close()
            return redirect(url_for("outbound"))
        if mat["quantity"] < qty:
            flash(f"库存不足（当前库存：{mat['quantity']}{mat['unit']}）", "error")
            conn.close()
            return redirect(url_for("outbound"))

        conn.execute("UPDATE materials SET quantity=quantity-? WHERE code=?", (qty, code))
        conn.execute("INSERT INTO transactions (type, material_code, material_name, quantity, operator, time) VALUES (?, ?, ?, ?, ?, ?)",
                     ("出库", code, mat["name"], qty, operator, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        conn.close()
        flash(f"{mat['name']} × {qty} 出库成功", "success")
        return redirect(url_for("index"))
    return render_template("outbound.html", materials=materials)


# ── 库存查询 ──
@app.route("/inventory")
def inventory():
    keyword = request.args.get("keyword", "")
    conn = get_db()
    if keyword:
        materials = conn.execute(
            "SELECT * FROM materials WHERE code LIKE ? OR name LIKE ? ORDER BY code",
            (f"%{keyword}%", f"%{keyword}%")
        ).fetchall()
    else:
        materials = conn.execute("SELECT * FROM materials ORDER BY code").fetchall()
    conn.close()
    return render_template("inventory.html", materials=materials, keyword=keyword)


# ── 出入库记录 ──
@app.route("/records")
def records():
    conn = get_db()
    all_records = conn.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 200").fetchall()
    conn.close()
    return render_template("records.html", records=all_records)


# ── 删除物资 ──
@app.route("/delete/<int:material_id>")
def delete_material(material_id):
    conn = get_db()
    conn.execute("DELETE FROM materials WHERE id=?", (material_id,))
    conn.commit()
    conn.close()
    flash("已删除", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
