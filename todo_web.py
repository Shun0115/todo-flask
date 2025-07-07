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

# HTMLテンプレート（Bootstrap＋カテゴリ表示）
HTML_TEMPLATE = """
<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ToDo App</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body class="bg-light">
  <div class="container py-4">
    <h1 class="mb-4 text-center">📋 ToDoリスト</h1>

    <ul class="list-group mb-4">
  {% for task, deadline, done, category in tasks %}
    <li class="list-group-item d-flex justify-content-between align-items-center" style="color: {{ get_color(deadline, done) }}; {% if done == 'True' %}text-decoration: line-through;{% endif %}">
      <form action="/toggle/{{ loop.index0 }}" method="post" class="me-2">
        <input type="checkbox" name="done" 
               onchange="this.form.submit()" 
               {% if done == 'True' %}checked{% endif %}
               style="transform: scale(1.3); margin-right: 6px;">
      </form>
      <div class="flex-grow-1">
        <div>{{ task }} <small class="text-muted">[{{ category }}]</small></div>
        <div class="text-muted small">
          締切: {{ deadline }}
          {% set left = days_left(deadline) %}
          {% if left is not none %}
            {% if left > 0 %}
              （あと {{ left }} 日）
            {% elif left == 0 %}
              （今日が締切！）
            {% else %}
              （{{ -left }} 日前に締切切れ）
            {% endif %}
      {% endif %}
      </div>

      </div>
      <div class="d-flex">
        <a href="/delete/{{ loop.index0 }}" class="btn btn-sm btn-outline-danger me-1">削除</a>
        <!-- 編集ボタン -->
        <button type="button" class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#editModal{{ loop.index0 }}">
          編集
        </button>
      </div>
    </li>

    <!-- 🔽 ループ内に残す！モーダル -->
    <div class="modal fade" id="editModal{{ loop.index0 }}" tabindex="-1" aria-labelledby="editModalLabel{{ loop.index0 }}" aria-hidden="true">
      <div class="modal-dialog">
        <form action="/update/{{ loop.index0 }}" method="post">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="editModalLabel{{ loop.index0 }}">タスク編集</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="閉じる"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">タスク</label>
                <input type="text" name="task" class="form-control" value="{{ task }}" required>
              </div>
              <div class="mb-3">
                <label class="form-label">締切</label>
                <input type="date" name="deadline" class="form-control" value="{{ deadline }}" required>
              </div>
              <div class="mb-3">
                <label class="form-label">カテゴリ</label>
                <select name="category" class="form-select" required>
                  {% for cat in categories %}
                    <option value="{{ cat }}" {% if cat == category %}selected{% endif %}>{{ cat }}</option>
                  {% endfor %}
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">キャンセル</button>
              <button type="submit" class="btn btn-success">保存</button>
            </div>
          </div>
        </form>
      </div>
    </div>
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
        <select name="category" class="form-select" required>
          {% for cat in categories %}
            <option value="{{ cat }}">{{ cat }}</option>
          {% endfor %}
        </select>
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
    # カテゴリ選択肢をここで定義！
    CATEGORIES = ["健康", "勉強", "仕事", "趣味", "家事", "その他"]

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

    return render_template_string(
        HTML_TEMPLATE,
        tasks=show_tasks(),
        get_color=get_color,
        categories=CATEGORIES,
        days_left=days_left
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
