from flask import Flask, request, redirect, render_template_string
import os

app = Flask(__name__)
TODO_FILE = "tasks.txt"

# show_tasks：タスク・期限・完了フラグを読み込む
# show_tasks() にソート処理を追加
from datetime import datetime

def show_tasks():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r") as f:
        lines = f.readlines()
        tasks = [tuple(line.strip().split(",", 2)) for line in lines]

    def parse_date(task):
        try:
            return datetime.strptime(task[1], "%Y-%m-%d")
        except:
            return datetime.max

    tasks.sort(key=parse_date)
    return tasks

# add_task：task, deadline, False を保存
def add_task(task, deadline):
    with open(TODO_FILE, "a") as f:
        f.write(f"{task},{deadline},False\n")

# toggle_done：完了状態を切り替え
def toggle_done(index):
    tasks = show_tasks()
    if 0 <= index < len(tasks):
        task, deadline, done = tasks[index]
        new_done = "False" if done == "True" else "True"
        tasks[index] = (task, deadline, new_done)
        with open(TODO_FILE, "w") as f:
            for t, d, dn in tasks:
                f.write(f"{t},{d},{dn}\n")

# delete_task：指定タスク削除
def delete_task(index):
    tasks = show_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        with open(TODO_FILE, "w") as f:
            for task, deadline, done in tasks:
                f.write(f"{task},{deadline},{done}\n")

# HTMLテンプレート
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>ToDo App</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 600px;
      margin: 40px auto;
      padding: 20px;
      background-color: #ffffff;
      color: #000000;
    }

    h1 {
      text-align: center;
      margin-bottom: 30px;
    }

    li {
      margin-bottom: 10px;
      line-height: 1.6;
    }

    input[type="text"], input[type="date"] {
      padding: 6px;
      margin-right: 10px;
      border: 1px solid #ccc;
      border-radius: 4px;
    }

    input[type="submit"] {
      padding: 6px 12px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }

    input[type="submit"]:hover {
      background-color: #45a049;
    }

    a {
      margin-left: 10px;
      color: #d11a2a;
      text-decoration: none;
    }

    a:hover {
      text-decoration: underline;
    }

    form {
      margin-bottom: 20px;
    }

    /* チェックボックス少し大きく */
    input[type="checkbox"] {
      transform: scale(1.2);
      margin-right: 5px;
    }

    /* ダークモード */
    @media (prefers-color-scheme: dark) {
      body {
        background-color: #1e1e1e;
        color: #e0e0e0;
      }
      input[type="text"], input[type="date"] {
        background-color: #2b2b2b;
        color: #fff;
        border: 1px solid #555;
      }
      input[type="submit"] {
        background-color: #388e3c;
      }
      a {
        color: #f44336;
      }
    }
  </style>
</head>
<body>
  <h1>ToDoリスト</h1>
  <ul>
    {% for task, deadline, done in tasks %}
      <li style="color: {{ get_color(deadline, done) }}; {% if done == 'True' %}text-decoration: line-through;{% endif %}">
        <form action="/toggle/{{ loop.index0 }}" method="post" style="display:inline;">
          <input type="checkbox" name="done" onchange="this.form.submit()" {% if done == 'True' %}checked{% endif %}>
        </form>
        {{ task }} - 締切: {{ deadline }}
        <a href="/delete/{{ loop.index0 }}">[削除]</a>
      </li>
    {% endfor %}
  </ul>

  <form action="/add" method="post">
    タスク: <input type="text" name="task">
    締切: <input type="date" name="deadline">
    <input type="submit" value="追加">
  </form>
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
    add_task(task, deadline)
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
    app.run(debug=True)
