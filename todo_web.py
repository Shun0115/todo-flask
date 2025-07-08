from flask import Flask, request, redirect, render_template
import os
from datetime import datetime

app = Flask(__name__)
TODO_FILE = "tasks.txt"

# show_tasks：タスク・期限・完了フラグを読み込む
# show_tasks() にソート処理を追加

def show_tasks():
    if not os.path.exists(TODO_FILE):
        return []

    tasks = []
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            parts = line.strip().split(",", maxsplit=3)
            print(f"[DEBUG] {i+1}行目: {parts}")
            tasks.append(tuple(parts))

    def parse_date(task):
        try:
            return datetime.strptime(task[1], "%Y-%m-%d")
        except:
            return datetime.max

    tasks.sort(key=parse_date)
    return tasks

# add_task：task, deadline, False を保存
def add_task(task, deadline, category):
    with open(TODO_FILE, "a") as f:
        f.write(f"{task},{deadline},False,{category}\n")

# toggle_done：完了状態を切り替え
def toggle_done(index):
    tasks = show_tasks()
    if 0 <= index < len(tasks):
        task, deadline, done, category = tasks[index]
        new_done = "False" if done == "True" else "True"
        tasks[index] = (task, deadline, new_done, category)
        with open(TODO_FILE, "w") as f:
            for t, d, dn, c in tasks:
                f.write(f"{t},{d},{dn},{c}\n")

# delete_task：指定タスク削除
def delete_task(index):
    tasks = show_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        with open(TODO_FILE, "w") as f:
            for task, deadline, done, category in tasks:
                f.write(f"{task},{deadline},{done},{category}\n")

@app.route("/")
def index():
    CATEGORIES = ["健康", "勉強", "仕事", "趣味", "家事", "その他"]
    query = request.args.get("q", "").strip() # ← 検索キーワードを取得
    selected_category = request.args.get("category", "すべて")

    def get_color(deadline, done):
        today = datetime.today().date()
        try:
            due = datetime.strptime(deadline, "%Y-%m-%d").date()
            if done == "True":
                return "gray"
            elif due < today:
                return "red"
            else:
                return "black"
        except:
            return "black"

    def days_left(deadline):
        try:
            due = datetime.strptime(deadline, "%Y-%m-%d").date()
            today = datetime.today().date()
            return (due - today).days
        except:
            return None

    all_tasks = show_tasks()

    if selected_category !="すべて":
        all_tasks = [t for t in all_tasks if t[3] == selected_category]
    if query:
        all_tasks = [
            t for t in all_tasks
            if query.lower() in t[0].lower() or query.lower() in t[3].lower()
         ]

    return render_template(
        "index.html",  # ← ファイル名指定
        tasks=all_tasks,
        get_color=get_color,
        categories=["すべて"] + CATEGORIES,
        selected_category=selected_category,
        days_left=days_left,
        query=query 
    )

@app.route("/add", methods=["POST"])
def add():
    task = request.form["task"]
    deadline = request.form["deadline"]
    category = request.form["category"]
    add_task(task, deadline, category)
    return redirect("/")

@app.route("/delete/<int:index>")
def delete(index):
    delete_task(index)
    return redirect("/")

@app.route("/toggle/<int:index>", methods=["POST"])
def toggle(index):
    toggle_done(index)
    return redirect("/")

@app.route("/update/<int:index>", methods=["POST"])
def update(index):
    tasks = show_tasks()
    if 0 <= index < len(tasks):
        task = request.form["task"]
        deadline = request.form["deadline"]
        category = request.form["category"]
        _, _, done, _ = tasks[index]  # 完了フラグは維持
        tasks[index] = (task, deadline, done, category)
        with open(TODO_FILE, "w") as f:
            for t, d, dn, c in tasks:
                f.write(f"{t},{d},{dn},{c}\n")
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
