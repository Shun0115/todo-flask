from flask import Flask, request, redirect, render_template_string
import os

app = Flask(__name__)
TODO_FILE = "tasks.txt"

def show_tasks():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def add_task(task):
    with open(TODO_FILE, "a") as f:
        f.write(task + "\n")

def delete_task(index):
    tasks = show_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        with open(TODO_FILE, "w") as f:
            for task in tasks:
                f.write(task + "\n")

HTML_TEMPLATE = """
<!doctype html>
<title>ToDo App</title>
<h1>ToDoリスト</h1>
<ul>
  {% for task in tasks %}
    <li>{{ task }} 
    <a href="/delete/{{ loop.index0 }}">[削除]</a></li>
  {% endfor %}
</ul>
<form action="/add" method="post">
  <input type="text" name="task">
  <input type="submit" value="追加">
</form>
"""
    

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, tasks=show_tasks())

@app.route("/add", methods=["POST"])
def add():
    task = request.form["task"]
    add_task(task)
    return redirect("/")

@app.route("/delete/<int:index>")
def delete(index):
    delete_task(index)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
