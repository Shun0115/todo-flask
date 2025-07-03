from flask import Flask, request, redirect, render_template_string
import os

app = Flask(__name__)
TODO_FILE = "tasks.txt"

# show_tasks：タスク・期限・完了フラグを読み込む
def show_tasks():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r") as f:
        lines = f.readlines()
        return [tuple(line.strip().split(",", 2)) for line in lines]  # (task, deadline, done)

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
<title>ToDo App</title>
<h1>ToDoリスト</h1>
<ul>
  {% for task, deadline, done in tasks %}
    <li style="color: {{ 'gray' if done == 'True' else 'black' }}">
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
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, tasks=show_tasks())

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
