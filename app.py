import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Файл для хранения задач
DATA_FILE = "tasks.json"
tasks = []  # Список всех задач
next_id = 1  # Следующий доступный ID для новой задачи

def load_tasks():
    """Загрузка задач из файла при запуске приложения"""
    global tasks, next_id
    try:
        with open(DATA_FILE, "r", encoding='utf-8') as f:
            tasks = json.load(f)
            if tasks:
                # Находим максимальный ID и увеличиваем на 1 для следующей задачи
                next_id = max(task["id"] for task in tasks) + 1
    except FileNotFoundError:
        # Если файл не найден, начинаем с пустого списка
        tasks = []

def save_tasks():
    """Сохранение задач в файл с красивым форматированием"""
    with open(DATA_FILE, "w", encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# Загружаем задачи при старте сервера
load_tasks()

# ----------------- REST API -----------------

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Получение всех задач (GET запрос)"""
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    """Добавление новой задачи (POST запрос)"""
    global next_id
    data = request.get_json()
    
    # Проверяем, что название задачи указано
    if not data or "title" not in data or not data["title"].strip():
        return jsonify({"error": "Task title is required"}), 400
    
    # Создаем новую задачу со всеми полями
    task = {
        "id": next_id,
        "title": data["title"].strip(),
        "description": data.get("description"),  # Новое поле для описания
        "completed": False,
        "priority": data.get("priority", "medium"),
        "category": data.get("category", "other"),  # Новое поле для категории
        "dueDate": data.get("dueDate"),
        "createdAt": datetime.now().isoformat()  # Время создания задачи
    }
    
    # Проверяем корректность приоритета
    if task["priority"] not in ["high", "medium", "low"]:
        task["priority"] = "medium"
    
    tasks.append(task)
    next_id += 1
    save_tasks()
    return jsonify(task), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Обновление задачи (PUT запрос) - переключение статуса или редактирование"""
    data = request.get_json()
    
    for task in tasks:
        if task["id"] == task_id:
            if data:
                # Если есть данные - обновляем поля задачи
                if "title" in data:
                    task["title"] = data["title"].strip()
                if "description" in data:
                    task["description"] = data["description"]
                if "completed" in data:
                    task["completed"] = data["completed"]
                if "priority" in data:
                    if data["priority"] in ["high", "medium", "low"]:
                        task["priority"] = data["priority"]
                if "category" in data:
                    task["category"] = data["category"]
                if "dueDate" in data:
                    task["dueDate"] = data["dueDate"]
            else:
                # Если данных нет - просто переключаем статус (для совместимости)
                task["completed"] = not task["completed"]
            
            save_tasks()
            return jsonify(task)
    
    return jsonify({"error": "Task not found"}), 404

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Удаление задачи (DELETE запрос)"""
    global tasks
    # Создаем новый список без удаляемой задачи
    new_tasks = [t for t in tasks if t["id"] != task_id]
    
    if len(new_tasks) == len(tasks):
        # Если длина не изменилась - задача не найдена
        return jsonify({"error": "Task not found"}), 404
    
    tasks = new_tasks
    save_tasks()
    return jsonify({"message": "Task deleted successfully"})

# ----------------- Frontend -----------------

@app.route("/")
def home():
    """Главная страница приложения"""
    return render_template("index.html")

# ----------------- Запуск приложения -----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)