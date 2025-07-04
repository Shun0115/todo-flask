from flask import Flask, request, redirect, render_template_string
import os
from datetime import datetime

app = Flask(__name__)
TODO_FILE = "tasks.txt"

# show_tasks：タスク・期限・完了フラグを読み込む
# show_tasks() にソート処理を追加

def show_tasks():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r") as f:
        lines = f.readlines()
        tasks = [tuple(line.strip().split(",",  3)) for line in lines]

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

# HTMLテンプレート（Bootstrap＋カテゴリ表示）
HTML_TEMPLATE = """
<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ToDo App</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
  <div class="container py-4">
    <h1 class="mb-4 text-center">📋 ToDoリスト</h1>

    <ul class="list-group mb-4">
      {% for task, deadline, done, category in tasks %}
        <li class="list-group-item d-flex justify-content-between align-items-center" style="color: {{ get_color(deadline, done) }}; {% if done == 'True' %}text-decoration: line-through;{% endif %}">
          <form action="/toggle/{{ loop.index0 }}" method="post" class="me-2">
            <input type="checkbox" name="done" onchange="this.form.submit()" {% if done == 'True' %}checked{% endif %}>
          </form>
          <div class="flex-grow-1">
            <div>{{ task }} <small class="text-muted">[{{ category }}]</small></div>
            <div class="text-muted small">締切: {{ deadline }}</div>
          </div>
          <a href="/delete/{{ loop.index0 }}" class="btn btn-sm btn-outline-danger">削除</a>
        </li>
      {% endfor %}
    </ul>

    <form action="/add" method="post" class="row g-2">
      <div class="col-12 col-md-4">
        <input type="text" name="task" class="form-control" placeholder="タスク" required>
      </div>
      <div class="col-12 col-md-3">
        <input type="date" name="deadline" class="form-control" required>
      </div>
      <div class="col-12 col-md-3">
        <input type="text" name="category" class="form-control" placeholder="カテゴリ" required>
      </div>
      <div class="col-12 col-md-2">
        <input type="submit" value="追加" class="btn btn-primary w-100">
      </div>
    </form>
  </div>
</body>
</html>
"""

@app.route("/")
def index():
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
    return render_template_string(HTML_TEMPLATE, tasks=show_tasks(), get_color=get_color)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
