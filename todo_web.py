from flask import Flask, request, redirect, render_template
import os
from datetime import datetime, timedelta

app = Flask(__name__)
TODO_FILE = "tasks.txt"

def parse_date(task):
        try:
            return datetime.strptime(task[1], "%Y-%m-%d")
        except:
            return datetime.max

def show_tasks():
    if not os.path.exists(TODO_FILE):
        return []

    tasks = []
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            parts = line.strip().split(",", maxsplit=4)
            tasks.append(tuple(parts)) # (task, deadline, done, category, priority)

    priority_order = {"高": 0, "中": 1, "低": 2}

    tasks.sort(key=lambda task: (
        parse_date(task),
        priority_order.get(task[4], 3)
    ))
    return tasks

# add_task：task, deadline, False を保存
def add_task(task, deadline, category, priority):
    with open(TODO_FILE, "a") as f:
        f.write(f"{task},{deadline},False,{category},{priority}\n")

# toggle_done：完了状態を切り替え
def toggle_done(index):
    tasks = show_tasks()
    if 0 <= index < len(tasks):
        task, deadline, done, category, priority= tasks[index]
        new_done = "False" if done == "True" else "True"
        tasks[index] = (task, deadline, new_done, category, priority)
        with open(TODO_FILE, "w") as f:
            for t, d, dn, c, p in tasks:
                f.write(f"{t},{d},{dn},{c},{p}\n")

# delete_task：指定タスク削除
def delete_task(index):
    tasks = show_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        with open(TODO_FILE, "w") as f:
            for task, deadline, done, category, priority in tasks:
                f.write(f"{task},{deadline},{done},{category},{priority}\n")

def get_priority_color(priority):
    return {
        "高": "danger", # 赤
        "中": "warning", # 黄
        "低": "secondary" # グレー
    }.get(priority, "secondary")

@app.route("/")
def index():
    CATEGORIES = ["健康", "勉強", "仕事", "趣味", "家事", "その他"]
    query = request.args.get("q", "").strip()
    selected_category = request.args.get("category", "すべて")
    expired_only = request.args.get("expired", "false") == "true"
    date_filter = request.args.get("date_filter", "")
    hide_done = request.args.get("hide_done", "false") == "true"

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

    if date_filter:  # ← インデント修正
        today = datetime.today().date()
        if date_filter == "today":
            all_tasks = [t for t in all_tasks if datetime.strptime(t[1], "%Y-%m-%d").date() == today and t[2] == "False"]
        elif date_filter == "tomorrow":
            tomorrow = today + timedelta(days=1)
            all_tasks = [t for t in all_tasks if datetime.strptime(t[1], "%Y-%m-%d").date() == tomorrow and t[2] == "False"]
        elif date_filter == "week":
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            all_tasks = [t for t in all_tasks if start_of_week <= datetime.strptime(t[1], "%Y-%m-%d").date() <= end_of_week and t[2] == "False"]

    if selected_category !="すべて":
        all_tasks = [t for t in all_tasks if t[3] == selected_category]

    if expired_only:
        today = datetime.today().date()
        all_tasks = [
            t for t in all_tasks
            if datetime.strptime(t[1], "%Y-%m-%d").date() < today and t[2] == "False"
        ]
        
    if query:
        all_tasks = [
            t for t in all_tasks
            if query.lower() in t[0].lower() or query.lower() in t[3].lower()
         ]

    if hide_done:
        all_tasks = [t for t in all_tasks if t[2] != "True"]

    query_params = request.args.to_dict(flat=True)

    return render_template(
        "index.html",
        tasks=all_tasks,
        get_color=get_color,
        get_priority_color=get_priority_color,
        categories=["すべて"] + CATEGORIES,
        selected_category=selected_category,
        days_left=days_left,
        query=query,
        expired_only=expired_only,
        date_filter=date_filter,
        hide_done=hide_done,
        query_params=query_params
    )

@app.route("/add", methods=["POST"])
def add():
    task = request.form["task"]
    deadline = request.form["deadline"]
    category = request.form["category"]
    priority = request.form["priority"]
    add_task(task, deadline, category, priority)
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
        priority = request.form["priority"]
        _, _, done, _, _ = tasks[index]  
        tasks[index] = (task, deadline, done, category, priority)
        with open(TODO_FILE, "w") as f:
            for t, d, dn, c, p in tasks:
                f.write(f"{t},{d},{dn},{c},{p}\n")
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
