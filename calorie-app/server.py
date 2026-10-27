"""Local server (standard library only): serves the pages and a small JSON API backed by SQLite."""
import json, mimetypes, os, sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from calc import calculate
from foods import FOODS
from workouts import plans_for

BASE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(BASE, "static")
DB = os.path.join(BASE, "data.db")
MEALS = ("breakfast", "lunch", "dinner")


def query(sql, args=(), write=False):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        cur = con.execute(sql, args)
        rows = [dict(r) for r in cur.fetchall()]
        if write:
            con.commit()
        return rows, cur.lastrowid
    finally:
        con.close()


def init_db():
    con = sqlite3.connect(DB)
    con.executescript(
        """CREATE TABLE IF NOT EXISTS log(id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, meal TEXT,
           name TEXT, grams REAL, kcal REAL, protein REAL, carbs REAL, fat REAL);
           CREATE TABLE IF NOT EXISTS goal(id INTEGER PRIMARY KEY CHECK(id=1),
           kcal REAL, protein REAL, carbs REAL, fat REAL, water REAL);
           CREATE TABLE IF NOT EXISTS water(id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, ml REAL);"""
    )
    if "water" not in [r[1] for r in con.execute("PRAGMA table_info(goal)")]:
        con.execute("ALTER TABLE goal ADD COLUMN water REAL")
    con.commit()
    con.close()


def num(v, lo, hi, label):
    try:
        v = float(v)
    except (TypeError, ValueError):
        raise ValueError(f"{label} غير صحيح")
    if not lo <= v <= hi:
        raise ValueError(f"{label} غير صحيح")
    return v


def save_goal(d):
    kcal = num(d.get("kcal"), 800, 6000, "السعرات")
    p = num(d["protein"], 0, 500, "البروتين") if d.get("protein") else kcal * 0.30 / 4
    c = num(d["carbs"], 0, 1000, "الكربوهيدرات") if d.get("carbs") else kcal * 0.40 / 4
    f = num(d["fat"], 0, 500, "الدهون") if d.get("fat") else kcal * 0.30 / 9
    old, _ = query("SELECT water FROM goal WHERE id=1")
    water = num(d["water"], 0.5, 10, "الماء") * 1000 if d.get("water") else (old[0]["water"] if old and old[0]["water"] else 2500)
    query("INSERT OR REPLACE INTO goal(id,kcal,protein,carbs,fat,water) VALUES (1,?,?,?,?,?)", (kcal, p, c, f, water), write=True)
    return {"kcal": round(kcal), "protein": round(p), "carbs": round(c), "fat": round(f), "water": round(water)}


def water_total(day):
    rows, _ = query("SELECT COALESCE(SUM(ml),0) AS ml FROM water WHERE day=?", (day,))
    return {"ml": rows[0]["ml"]}


def add_water(d):
    day = str(d.get("day", ""))[:10]
    if len(day) != 10:
        raise ValueError("بيانات غير صحيحة")
    query("INSERT INTO water(day,ml) VALUES (?,?)", (day, num(d.get("ml"), 1, 5000, "كمية الماء")), write=True)
    return water_total(day)


def add_item(d):
    day, meal = str(d.get("day", ""))[:10], d.get("meal")
    if meal not in MEALS or len(day) != 10:
        raise ValueError("بيانات غير صحيحة")
    if d.get("food"):
        food = FOODS.get(int(d["food"]))
        if not food:
            raise ValueError("الطعام غير موجود")
        g = num(d.get("grams"), 1, 5000, "الكمية")
        k = g / 100
        row = (day, meal, food["name"], g, food["kcal"] * k, food["protein"] * k, food["carbs"] * k, food["fat"] * k)
    else:
        name = str(d.get("name", "")).strip()[:60]
        if not name:
            raise ValueError("اكتب اسم الطعام")
        g = num(d.get("grams") or 0, 0, 5000, "الكمية")
        row = (day, meal, name, g, num(d.get("kcal"), 1, 5000, "السعرات"),
               num(d.get("protein") or 0, 0, 500, "البروتين"), num(d.get("carbs") or 0, 0, 1000, "الكربوهيدرات"),
               num(d.get("fat") or 0, 0, 500, "الدهون"))
    _, new_id = query("INSERT INTO log(day,meal,name,grams,kcal,protein,carbs,fat) VALUES (?,?,?,?,?,?,?,?)", row, write=True)
    return {"id": new_id}


class Handler(BaseHTTPRequestHandler):
    def reply(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def handle_api(self, method):
        url = urlparse(self.path)
        qs = parse_qs(url.query)
        try:
            if method == "GET" and url.path == "/api/foods":
                return self.reply(list(FOODS.values()))
            if method == "GET" and url.path == "/api/plans":
                return self.reply(plans_for(int(qs.get("days", ["0"])[0])))
            if method == "GET" and url.path == "/api/goal":
                rows, _ = query("SELECT kcal,protein,carbs,fat,water FROM goal WHERE id=1")
                return self.reply(rows[0] if rows else None)
            if method == "GET" and url.path == "/api/water":
                return self.reply(water_total(qs.get("day", [""])[0]))
            if method == "POST" and url.path == "/api/water":
                return self.reply(add_water(self.body()), 201)
            if method == "DELETE" and url.path == "/api/water":
                query("DELETE FROM water WHERE day=?", (qs.get("day", [""])[0],), write=True)
                return self.reply({"ml": 0})
            if method == "GET" and url.path == "/api/log":
                rows, _ = query("SELECT * FROM log WHERE day=? ORDER BY id", (qs.get("day", [""])[0],))
                return self.reply(rows)
            if method == "POST" and url.path == "/api/calc":
                d = self.body()
                return self.reply(calculate(d.get("sex"), d.get("age"), d.get("height"), d.get("weight"), d.get("act"), d.get("goal")))
            if method == "POST" and url.path == "/api/goal":
                return self.reply(save_goal(self.body()))
            if method == "POST" and url.path == "/api/log":
                return self.reply(add_item(self.body()), 201)
            if method == "DELETE" and url.path.startswith("/api/log/"):
                query("DELETE FROM log WHERE id=?", (int(url.path.rsplit("/", 1)[1]),), write=True)
                return self.reply({"ok": True})
            self.reply({"error": "غير موجود"}, 404)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            self.reply({"error": str(e) or "بيانات غير صحيحة"}, 400)

    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            return self.handle_api("GET")
        full = os.path.realpath(os.path.join(STATIC, "index.html" if path == "/" else path.lstrip("/")))
        if not full.startswith(STATIC + os.sep) or not os.path.isfile(full):
            self.send_error(404)
            return
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        if ctype.startswith("text/") or "javascript" in ctype:
            ctype += "; charset=utf-8"
        with open(full, "rb") as fh:
            data = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        self.handle_api("POST")

    def do_DELETE(self):
        self.handle_api("DELETE")


if __name__ == "__main__":
    init_db()
    print("افتح المتصفح على: http://localhost:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
