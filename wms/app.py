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
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            id_card TEXT DEFAULT '',
            created TEXT NOT NULL,
            FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER NOT NULL,
            site_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            check_in TEXT,
            check_out TEXT,
            note TEXT DEFAULT '',
            UNIQUE(worker_id, date),
            FOREIGN KEY (worker_id) REFERENCES workers(id) ON DELETE CASCADE,
            FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
        );
    """)
    # Migration: add columns to existing transactions table
    for col_sql in [
        "ALTER TABLE transactions ADD COLUMN unit_price REAL DEFAULT 0",
        "ALTER TABLE transactions ADD COLUMN worker_id INTEGER DEFAULT NULL",
        "ALTER TABLE attendance ADD COLUMN status TEXT DEFAULT ''",
    ]:
        try:
            conn.execute(col_sql)
        except sqlite3.OperationalError:
            pass
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
               COUNT(DISTINCT i.material_id) AS total_types,
               (SELECT COUNT(*) FROM workers WHERE site_id = s.id) AS total_workers
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
    worker_count = conn.execute("SELECT COUNT(*) AS cnt FROM workers WHERE site_id=?", (id,)).fetchone()["cnt"]
    conn.close()
    return render_template("site_detail.html", site=site, inventory=inventory, worker_count=worker_count)


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
#  工人管理
# ═══════════════════════════════════════════

@app.route("/site/<int:site_id>/workers")
def worker_list(site_id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id=?", (site_id,)).fetchone()
    if not site:
        flash("项目地不存在", "error")
        conn.close()
        return redirect(url_for("index"))
    workers = conn.execute("SELECT * FROM workers WHERE site_id=? ORDER BY id", (site_id,)).fetchall()
    conn.close()
    return render_template("workers.html", site=site, workers=workers)


@app.route("/site/<int:site_id>/worker/add", methods=["GET", "POST"])
def worker_add(site_id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id=?", (site_id,)).fetchone()
    if not site:
        flash("项目地不存在", "error")
        conn.close()
        return redirect(url_for("index"))
    if request.method == "POST":
        name = request.form["name"].strip()
        if not name:
            flash("工人姓名不能为空", "error")
            conn.close()
            return redirect(url_for("worker_add", site_id=site_id))
        conn.execute("INSERT INTO workers (site_id, name, phone, id_card, created) VALUES (?,?,?,?,?)",
                     (site_id, name,
                      request.form.get("phone", "").strip(),
                      request.form.get("id_card", "").strip(),
                      datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        flash(f"工人「{name}」已添加", "success")
        conn.close()
        return redirect(url_for("worker_list", site_id=site_id))
    conn.close()
    return render_template("worker_form.html", site=site, worker=None)


@app.route("/site/<int:site_id>/worker/<int:worker_id>/edit", methods=["GET", "POST"])
def worker_edit(site_id, worker_id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id=?", (site_id,)).fetchone()
    worker = conn.execute("SELECT * FROM workers WHERE id=? AND site_id=?", (worker_id, site_id)).fetchone()
    if not site or not worker:
        flash("工人不存在", "error")
        conn.close()
        return redirect(url_for("worker_list", site_id=site_id))
    if request.method == "POST":
        name = request.form["name"].strip()
        if not name:
            flash("工人姓名不能为空", "error")
            conn.close()
            return redirect(url_for("worker_edit", site_id=site_id, worker_id=worker_id))
        conn.execute("UPDATE workers SET name=?, phone=?, id_card=? WHERE id=?",
                     (name,
                      request.form.get("phone", "").strip(),
                      request.form.get("id_card", "").strip(),
                      worker_id))
        conn.commit()
        flash("工人信息已更新", "success")
        conn.close()
        return redirect(url_for("worker_list", site_id=site_id))
    conn.close()
    return render_template("worker_form.html", site=site, worker=worker)


@app.route("/site/<int:site_id>/worker/<int:worker_id>/delete")
def worker_delete(site_id, worker_id):
    conn = get_db()
    conn.execute("DELETE FROM workers WHERE id=? AND site_id=?", (worker_id, site_id))
    conn.commit()
    conn.close()
    flash("工人已删除", "success")
    return redirect(url_for("worker_list", site_id=site_id))


# ═══════════════════════════════════════════
#  工人打卡
# ═══════════════════════════════════════════

@app.route("/site/<int:site_id>/attendance")
def attendance(site_id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id=?", (site_id,)).fetchone()
    if not site:
        flash("项目地不存在", "error")
        conn.close()
        return redirect(url_for("index"))
    today = datetime.now().strftime("%Y-%m-%d")
    workers = conn.execute("SELECT * FROM workers WHERE site_id=? ORDER BY name", (site_id,)).fetchall()
    today_records = conn.execute("""
        SELECT a.*, w.name AS worker_name
        FROM attendance a
        JOIN workers w ON w.id = a.worker_id
        WHERE a.site_id = ? AND a.date = ?
        ORDER BY w.name
    """, (site_id, today)).fetchall()
    history = conn.execute("""
        SELECT a.*, w.name AS worker_name
        FROM attendance a
        JOIN workers w ON w.id = a.worker_id
        WHERE a.site_id = ?
        ORDER BY a.id DESC LIMIT 50
    """, (site_id,)).fetchall()
    # combine workers with today's attendance record for batch display
    record_map = {r["worker_id"]: r for r in today_records}
    workers_attendance = [{"worker": w, "record": record_map.get(w["id"])} for w in workers]
    conn.close()
    return render_template("attendance.html", site=site, workers_attendance=workers_attendance,
                           workers=workers, history=history, today=today)


@app.route("/site/<int:site_id>/attendance/checkin", methods=["POST"])
def attendance_checkin(site_id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id=?", (site_id,)).fetchone()
    if not site:
        flash("项目地不存在", "error")
        conn.close()
        return redirect(url_for("index"))
    worker_id = int(request.form["worker_id"])
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M")
    existing = conn.execute("SELECT * FROM attendance WHERE worker_id=? AND date=?",
                            (worker_id, today)).fetchone()
    if existing:
        if existing["check_in"]:
            flash("该工人今日已签到", "error")
            conn.close()
            return redirect(url_for("attendance", site_id=site_id))
        conn.execute("UPDATE attendance SET check_in=? WHERE id=?", (now, existing["id"]))
    else:
        conn.execute("INSERT INTO attendance (worker_id, site_id, date, check_in) VALUES (?,?,?,?)",
                     (worker_id, site_id, today, now))
    conn.commit()
    worker = conn.execute("SELECT name FROM workers WHERE id=?", (worker_id,)).fetchone()
    flash(f"{worker['name']} 签到成功 — {now}", "success")
    conn.close()
    return redirect(url_for("attendance", site_id=site_id))


@app.route("/site/<int:site_id>/attendance/batch", methods=["POST"])
def attendance_batch(site_id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id=?", (site_id,)).fetchone()
    if not site:
        flash("项目地不存在", "error")
        conn.close()
        return redirect(url_for("index"))

    action = request.form.get("action")
    worker_ids = request.form.getlist("worker_ids")
    note = request.form.get("note", "").strip()

    if not worker_ids:
        flash("请至少选择一个工人", "error")
        conn.close()
        return redirect(url_for("attendance", site_id=site_id))

    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M")
    count = 0

    for wid_str in worker_ids:
        wid = int(wid_str)
        existing = conn.execute("SELECT * FROM attendance WHERE worker_id=? AND date=?",
                                (wid, today)).fetchone()

        if action == "checkin":
            if existing:
                if not existing["check_in"]:
                    conn.execute("UPDATE attendance SET check_in=?, note=? WHERE id=?",
                                 (now, note, existing["id"]))
                    count += 1
            else:
                conn.execute("INSERT INTO attendance (worker_id, site_id, date, check_in, note) VALUES (?,?,?,?,?)",
                             (wid, site_id, today, now, note))
                count += 1

        elif action == "absent":
            if existing:
                conn.execute("UPDATE attendance SET status='旷工', note=? WHERE id=?",
                             (note, existing["id"]))
            else:
                conn.execute("INSERT INTO attendance (worker_id, site_id, date, status, note) VALUES (?,?,?,?,?)",
                             (wid, site_id, today, '旷工', note))
            count += 1

    conn.commit()
    action_names = {"checkin": "签到", "absent": "标记旷工"}
    flash(f"批量{action_names.get(action, action)}完成：{count} 人", "success")
    conn.close()
    return redirect(url_for("attendance", site_id=site_id))


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
        unit_price = float(request.form.get("unit_price", 0) or 0)
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

        conn.execute("INSERT INTO transactions (site_id, material_id, type, quantity, unit_price, operator, note, time) VALUES (?,?,?,?,?,?,?,?)",
                     (site_id, material_id, "入库", qty, unit_price, operator, note,
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
    workers = conn.execute("SELECT * FROM workers WHERE site_id=? ORDER BY name", (site_id,)).fetchall()

    if request.method == "POST":
        material_id = int(request.form["material_id"])
        qty = int(request.form["quantity"])
        unit_price = float(request.form.get("unit_price", 0) or 0)
        operator = request.form.get("operator", "").strip()
        note = request.form.get("note", "").strip()
        worker_id = request.form.get("worker_id")
        worker_id = int(worker_id) if worker_id else None

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
        conn.execute("INSERT INTO transactions (site_id, material_id, type, quantity, unit_price, worker_id, operator, note, time) VALUES (?,?,?,?,?,?,?,?,?)",
                     (site_id, material_id, "出库", qty, unit_price, worker_id, operator, note,
                      datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        mat = conn.execute("SELECT name FROM materials WHERE id=?", (material_id,)).fetchone()
        flash(f"【{site['name']}】{mat['name']} × {qty} 出库成功", "success")
        conn.close()
        return redirect(url_for("site_detail", id=site_id))

    conn.close()
    return render_template("outbound.html", site=site, inventory=inventory, workers=workers)


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
        SELECT t.*, m.code, m.name, m.unit, w.name AS worker_name
        FROM transactions t
        JOIN materials m ON m.id = t.material_id
        LEFT JOIN workers w ON w.id = t.worker_id
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
    sites = conn.execute("SELECT * FROM sites ORDER BY name").fetchall()
    records_by_site = {}
    for site in sites:
        records = conn.execute("""
            SELECT t.*, m.code, m.name, m.unit, w.name AS worker_name
            FROM transactions t
            JOIN materials m ON m.id = t.material_id
            LEFT JOIN workers w ON w.id = t.worker_id
            WHERE t.site_id = ?
            ORDER BY t.id DESC LIMIT 100
        """, (site["id"],)).fetchall()
        if records:
            records_by_site[site["name"]] = {"site": site, "records": records}
    conn.close()
    return render_template("all_records.html", records_by_site=records_by_site)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
