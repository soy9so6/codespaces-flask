import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DATA_FILE = "tasks.json"
tasks = []
next_id = 1

def load_tasks():
    global tasks, next_id
    try:
        with open(DATA_FILE, "r") as f:
            tasks = json.load(f)
            if tasks:
                next_id = max(task["id"] for task in tasks) + 1
    except FileNotFoundError:
        tasks = []

def save_tasks():
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

load_tasks()

# ----------------- REST API -----------------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    global next_id
    data = request.get_json()
    if not data or "title" not in data or not data["title"].strip():
        return jsonify({"error": "Title is required"}), 400
    
    task = {
        "id": next_id,
        "title": data["title"].strip(),
        "completed": False,
        "priority": data.get("priority", "medium"),
        "dueDate": data.get("dueDate"),
        "createdAt": datetime.now().isoformat()
    }
    
    # Validate priority
    if task["priority"] not in ["high", "medium", "low"]:
        task["priority"] = "medium"
    
    tasks.append(task)
    next_id += 1
    save_tasks()
    return jsonify(task), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    
    for task in tasks:
        if task["id"] == task_id:
            if data:
                # Update fields if provided
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
                # Toggle completed if no data provided (for backward compatibility)
                task["completed"] = not task["completed"]
            
            save_tasks()
            return jsonify(task)
    
    return jsonify({"error": "Task not found"}), 404

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    new_tasks = [t for t in tasks if t["id"] != task_id]
    
    if len(new_tasks) == len(tasks):
        return jsonify({"error": "Task not found"}), 404
    
    tasks = new_tasks
    save_tasks()
    return jsonify({"message": "Deleted"})

# ----------------- Frontend -----------------
@app.route("/")
def home():
    return render_template("index.html")

# ----------------- Run -----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)