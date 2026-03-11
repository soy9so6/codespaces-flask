import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Файл для хранения задач
DATA_FILE = "tasks.json"
tasks = []  # Список всех задач
next_id = 1  # Следующий доступный ID

def load_tasks():
    """Загрузка задач из файла при запуске"""
    global tasks, next_id
    try:
        with open(DATA_FILE, "r", encoding='utf-8') as f:
            tasks = json.load(f)
            if tasks:
                next_id = max(task["id"] for task in tasks) + 1
    except FileNotFoundError:
        tasks = []

def save_tasks():
    """Сохранение задач в файл"""
    with open(DATA_FILE, "w", encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# Загружаем задачи при старте
load_tasks()

# ----------------- REST API -----------------

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Получение всех задач"""
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    """Добавление новой задачи"""
    global next_id
    data = request.get_json()
    
    if not data or "title" not in data or not data["title"].strip():
        return jsonify({"error": "Не указано название задачи"}), 400
    
    task = {
        "id": next_id,
        "title": data["title"].strip(),
        "completed": False,
        "priority": data.get("priority", "medium"),
        "dueDate": data.get("dueDate"),
        "createdAt": datetime.now().isoformat()
    }
    
    if task["priority"] not in ["high", "medium", "low"]:
        task["priority"] = "medium"
    
    tasks.append(task)
    next_id += 1
    save_tasks()
    return jsonify(task), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Обновление задачи"""
    data = request.get_json()
    
    for task in tasks:
        if task["id"] == task_id:
            if data:
                if "title" in data:
                    task["title"] = data["title"].strip()
                if "completed" in data:
                    task["completed"] = data["completed"]
                if "priority" in data:
                    if data["priority"] in ["high", "medium", "low"]:
                        task["priority"] = data["priority"]
                if "dueDate" in data:
                    task["dueDate"] = data["dueDate"]
            else:
                task["completed"] = not task["completed"]
            
            save_tasks()
            return jsonify(task)
    
    return jsonify({"error": "Задача не найдена"}), 404

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Удаление задачи"""
    global tasks
    new_tasks = [t for t in tasks if t["id"] != task_id]
    
    if len(new_tasks) == len(tasks):
        return jsonify({"error": "Задача не найдена"}), 404
    
    tasks = new_tasks
    save_tasks()
    return jsonify({"message": "Задача удалена"})

# ----------------- Frontend -----------------

@app.route("/")
def home():
    """Главная страница"""
    return render_template("index.html")

# ----------------- Run -----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)