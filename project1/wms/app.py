"""智能仓储管理系统 — 公司级多项目地版"""

import sqlite3, os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "wms2026"
DB_PATH = os.path.join(os.path.dirname(__file__), "warehouse.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            location TEXT DEFAULT '',
            contact TEXT DEFAULT '',
            created TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            spec TEXT DEFAULT '',
            unit TEXT DEFAULT '个'
        );
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 0,
            UNIQUE(site_id, material_id),
            FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            operator TEXT DEFAULT '',
            note TEXT DEFAULT '',
            time TEXT NOT NULL,
            FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════
#  首页 — 项目地总览
# ═══════════════════════════════════════════

@app.route("/")
def index():
    conn = get_db()
    sites = conn.execute("""
        SELECT s.*,
               COALESCE(SUM(i.quantity),0) AS total_items,
               COUNT(DISTINCT i.material_id) AS total_types
        FROM sites s
        LEFT JOIN inventory i ON i.site_id = s.id
        GROUP BY s.id
        ORDER BY s.id
    """).fetchall()
    conn.close()
    return render_template("index.html", sites=sites)


# ═══════════════════════════════════════════
#  项目地管理
# ═══════════════════════════════════════════

@app.route("/site/add", methods=["GET", "POST"])
def site_add():
    if request.method == "POST":
        name = request.form["name"].strip()
        if not name:
            flash("项目地名不能为空", "error")
            return redirect(url_for("site_add"))
        conn = get_db()
        try:
            conn.execute("INSERT INTO sites (name, location, contact, created) VALUES (?, ?, ?, ?)",
                         (name, request.form.get("location", "").strip(),
                          request.form.get("contact", "").strip(),
                          datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            flash(f"项目地「{name}」已添加", "success")
        except sqlite3.IntegrityError:
            flash(f"项目地「{name}」已存在", "error")
        conn.close()
        return redirect(url_for("index"))
    return render_template("site_form.html", site=None)


@app.route("/site/<int:id>/edit", methods=["GET", "POST"])
def site_edit(id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id=?", (id,)).fetchone()
    if not site:
        flash("项目地不存在", "error")
        conn.close()
        return redirect(url_for("index"))
    if request.method == "POST":
        name = request.form["name"].strip()
        if not name:
            flash("项目地名不能为空", "error")
            conn.close()
            return redirect(url_for("site_edit", id=id))
        try:
            conn.execute("UPDATE sites SET name=?, location=?, contact=? WHERE id=?",
                         (name, request.form.get("location", "").strip(),
                          request.form.get("contact", "").strip(), id))
            conn.commit()
            flash("项目地信息已更新", "success")
        except sqlite3.IntegrityError:
            flash(f"项目地「{name}」已存在", "error")
        conn.close()
        return redirect(url_for("index"))
    conn.close()
    return render_template("site_form.html", site=site)


@app.route("/site/<int:id>/delete")
def site_delete(id):
    conn = get_db()
    site = conn.execute("SELECT name FROM sites WHERE id=?", (id,)).fetchone()
    if site:
        conn.execute("DELETE FROM transactions WHERE site_id=?", (id,))
        conn.execute("DELETE FROM inventory WHERE site_id=?", (id,))
        conn.execute("DELETE FROM sites WHERE id=?", (id,))
        conn.commit()
        flash(f"项目地「{site['name']}」已删除", "success")
    conn.close()
    return redirect(url_for("index"))


# ═══════════════════════════════════════════
#  项目地详情 — 库存清单
# ═══════════════════════════════════════════

@app.route("/site/<int:id>")
def site_detail(id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id=?", (id,)).fetchone()
    if not site:
        flash("项目地不存在", "error")
        conn.close()
        return redirect(url_for("index"))
    inventory = conn.execute("""
        SELECT i.*, m.code, m.name, m.spec, m.unit
        FROM inventory i
        JOIN materials m ON m.id = i.material_id
        WHERE i.site_id = ? AND i.quantity > 0
        ORDER BY m.code
    """, (id,)).fetchall()
    conn.close()
    return render_template("site_detail.html", site=site, inventory=inventory)


# ═══════════════════════════════════════════
#  物资目录管理
# ═══════════════════════════════════════════

@app.route("/materials")
def material_list():
    conn = get_db()
    materials = conn.execute("SELECT * FROM materials ORDER BY code").fetchall()
    conn.close()
    return render_template("materials.html", materials=materials)


@app.route("/material/add", methods=["POST"])
def material_add():
    code = request.form["code"].strip()
    name = request.form["name"].strip()
    if not code or not name:
        flash("编码和名称不能为空", "error")
        return redirect(url_for("material_list"))
    conn = get_db()
    try:
        conn.execute("INSERT INTO materials (code, name, spec, unit) VALUES (?, ?, ?, ?)",
                     (code, name, request.form.get("spec", "").strip(),
                      request.form.get("unit", "个").strip()))
        conn.commit()
        flash(f"物资「{name}」已添加", "success")
    except sqlite3.IntegrityError:
        flash(f"编码「{code}」已存在", "error")
    conn.close()
    return redirect(url_for("material_list"))


@app.route("/material/<int:id>/delete")
def material_delete(id):
    conn = get_db()
    conn.execute("DELETE FROM materials WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("物资已删除", "success")
    return redirect(url_for("material_list"))


# ═══════════════════════════════════════════
#  入库
# ═══════════════════════════════════════════

@app.route("/site/<int:site_id>/inbound", methods=["GET", "POST"])
def inbound(site_id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id=?", (site_id,)).fetchone()
    materials = conn.execute("SELECT * FROM materials ORDER BY code").fetchall()
    if not site:
        flash("项目地不存在", "error")
        conn.close()
        return redirect(url_for("index"))

    if request.method == "POST":
        material_id = int(request.form["material_id"])
        qty = int(request.form["quantity"])
        operator = request.form.get("operator", "").strip()
        note = request.form.get("note", "").strip()
        if qty <= 0:
            flash("数量必须大于0", "error")
            conn.close()
            return redirect(url_for("inbound", site_id=site_id))

        existing = conn.execute("SELECT * FROM inventory WHERE site_id=? AND material_id=?",
                                (site_id, material_id)).fetchone()
        if existing:
            conn.execute("UPDATE inventory SET quantity=quantity+? WHERE site_id=? AND material_id=?",
                         (qty, site_id, material_id))
        else:
            conn.execute("INSERT INTO inventory (site_id, material_id, quantity) VALUES (?, ?, ?)",
                         (site_id, material_id, qty))

        conn.execute("INSERT INTO transactions (site_id, material_id, type, quantity, operator, note, time) VALUES (?,?,?,?,?,?,?)",
                     (site_id, material_id, "入库", qty, operator, note,
                      datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        mat = conn.execute("SELECT name FROM materials WHERE id=?", (material_id,)).fetchone()
        flash(f"【{site['name']}】{mat['name']} × {qty} 入库成功", "success")
        conn.close()
        return redirect(url_for("site_detail", id=site_id))

    conn.close()
    return render_template("inbound.html", site=site, materials=materials)


# ═══════════════════════════════════════════
#  出库
# ═══════════════════════════════════════════

@app.route("/site/<int:site_id>/outbound", methods=["GET", "POST"])
def outbound(site_id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id=?", (site_id,)).fetchone()
    if not site:
        flash("项目地不存在", "error")
        conn.close()
        return redirect(url_for("index"))

    inventory = conn.execute("""
        SELECT i.*, m.code, m.name, m.spec, m.unit
        FROM inventory i JOIN materials m ON m.id = i.material_id
        WHERE i.site_id = ? AND i.quantity > 0
        ORDER BY m.code
    """, (site_id,)).fetchall()

    if request.method == "POST":
        material_id = int(request.form["material_id"])
        qty = int(request.form["quantity"])
        operator = request.form.get("operator", "").strip()
        note = request.form.get("note", "").strip()
        if qty <= 0:
            flash("数量必须大于0", "error")
            conn.close()
            return redirect(url_for("outbound", site_id=site_id))

        inv = conn.execute("SELECT * FROM inventory WHERE site_id=? AND material_id=?",
                           (site_id, material_id)).fetchone()
        if not inv or inv["quantity"] < qty:
            flash(f"库存不足（当前库存：{inv['quantity'] if inv else 0}）", "error")
            conn.close()
            return redirect(url_for("outbound", site_id=site_id))

        conn.execute("UPDATE inventory SET quantity=quantity-? WHERE site_id=? AND material_id=?",
                     (qty, site_id, material_id))
        conn.execute("INSERT INTO transactions (site_id, material_id, type, quantity, operator, note, time) VALUES (?,?,?,?,?,?,?)",
                     (site_id, material_id, "出库", qty, operator, note,
                      datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        mat = conn.execute("SELECT name FROM materials WHERE id=?", (material_id,)).fetchone()
        flash(f"【{site['name']}】{mat['name']} × {qty} 出库成功", "success")
        conn.close()
        return redirect(url_for("site_detail", id=site_id))

    conn.close()
    return render_template("outbound.html", site=site, inventory=inventory)


# ═══════════════════════════════════════════
#  出入库记录
# ═══════════════════════════════════════════

@app.route("/site/<int:site_id>/records")
def site_records(site_id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id=?", (site_id,)).fetchone()
    if not site:
        flash("项目地不存在", "error")
        conn.close()
        return redirect(url_for("index"))
    records = conn.execute("""
        SELECT t.*, m.code, m.name, m.unit
        FROM transactions t
        JOIN materials m ON m.id = t.material_id
        WHERE t.site_id = ?
        ORDER BY t.id DESC LIMIT 200
    """, (site_id,)).fetchall()
    conn.close()
    return render_template("records.html", site=site, records=records)


# ═══════════════════════════════════════════
#  全部记录（跨项目地）
# ═══════════════════════════════════════════

@app.route("/records")
def all_records():
    conn = get_db()
    records = conn.execute("""
        SELECT t.*, m.code, m.name, m.unit, s.name AS site_name
        FROM transactions t
        JOIN materials m ON m.id = t.material_id
        JOIN sites s ON s.id = t.site_id
        ORDER BY t.id DESC LIMIT 300
    """).fetchall()
    conn.close()
    return render_template("all_records.html", records=records)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
