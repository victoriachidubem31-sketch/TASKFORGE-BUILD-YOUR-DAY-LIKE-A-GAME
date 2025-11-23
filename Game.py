# =========================================
# Author: Okafor Chidubem Victoria (Vicky)
# Programiz November Challenge
# Theme: Everyday Tools - Code That Gets Things Done 🧰
# Project: TaskForge: Your Smart Daily Command Center
# Description:
# A shippable Python productivity tool: create/edit/track tasks, use Pomodoro timers,
# earn XP, unlock badges, view stats & streaks. Saves progress to taskforge_save.json (if allowed).
# =========================================

import time
import json
import random
import os
from datetime import datetime, date

SAVE_FILE = "taskforge_save.json"

# -------------------------
# Helper utilities
# -------------------------
def safe_print(s=""):
    print(s)

def delay_print(text, speed=0.01):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(speed)
    print()

def print_line(char="=", length=60):
    print(char * length)

# -------------------------
# Data structures / defaults
# -------------------------
default_state = {
    "player": {
        "name": "Vicky",
        "xp": 0,
        "level": 1,
        "badges": [],
        "streak": 0,
        "last_active_date": None
    },
    "tasks": [],  # list of {id, title, xp, priority, tags, notes, done, created_at, completed_at}
    "history": []  # list of completed task records
}

motivations = [
    "Keep focused — progress compounds over time. 📈",
    "Each completed task brings you closer to your goals. 🎯",
    "Prioritize smartly and execute efficiently. ⚡",
    "Consistency and discipline create results. 🏆",
    "Reflect, learn, and improve with every action. 💡",
    "High-quality work beats busywork every time. ✅",
    "Plan, act, review — repeat for excellence. 🔄",
    "Focus on impact, not just activity. 🚀",
    "Your efforts today define your success tomorrow. 🔑",
    "Small, consistent wins lead to major achievements. 🌟"
]

feedbacks = [
    "Well done — that was executed with focus.",
    "Nice job — momentum is on your side.",
    "Great execution — persistence pays off.",
    "Good work — progress is being built consistently.",
    "Solid finish — your workflow is improving."
]

badge_pool = [
    {"id": "focus_warrior", "name": "Focus Warrior"},
    {"id": "deadline_crusher", "name": "Deadline Crusher"},
    {"id": "consistency_pro", "name": "Consistency Pro"},
    {"id": "task_master", "name": "Task Master"},
    {"id": "productivity_ninja", "name": "Productivity Ninja"}
]

# -------------------------
# Persistence (load/save)
# -------------------------
def load_state():
    if not os.path.exists(SAVE_FILE):
        return default_state.copy()
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        # simple migration safety
        for k in default_state:
            if k not in state:
                state[k] = default_state[k]
        return state
    except Exception as e:
        safe_print(f"[Warning] Could not load save file: {e}")
        return default_state.copy()

def save_state(state):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        safe_print(f"[Warning] Saving disabled or not permitted here: {e}")
        return False

# -------------------------
# Core logic
# -------------------------
state = load_state()
player = state["player"]
tasks = state["tasks"]
history = state["history"]

def next_task_id():
    return max([t.get("id", 0) for t in tasks], default=0) + 1

def add_task(title, xp=20, priority="medium", tags=None, notes=""):
    if tags is None:
        tags = []
    task = {
        "id": next_task_id(),
        "title": title,
        "xp": xp,
        "priority": priority,
        "tags": tags,
        "notes": notes,
        "done": False,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    tasks.append(task)
    save_state(state)
    delay_print(f"Task added: [{task['id']}] {task['title']} (XP: {task['xp']})")

def edit_task(task_id, **fields):
    t = next((x for x in tasks if x["id"] == task_id), None)
    if not t:
        delay_print("Task not found.")
        return
    for k, v in fields.items():
        if k in t and v is not None:
            t[k] = v
    save_state(state)
    delay_print(f"Task [{task_id}] updated.")

def delete_task(task_id):
    global tasks
    before = len(tasks)
    tasks[:] = [x for x in tasks if x["id"] != task_id]
    save_state(state)
    delay_print(f"Deleted {before - len(tasks)} tasks.")

def list_tasks(show_all=True):
    print_line()
    delay_print("📋 TaskForge - Current Tasks")
    if not tasks:
        delay_print("No tasks found. Add one to get started.")
        print_line()
        return
    for t in tasks:
        status = "✅ Done" if t["done"] else "❌ Pending"
        delay_print(f"[{t['id']}] {t['title']} (XP:{t['xp']}) [{t['priority']}] {status}")
        if t.get("notes"):
            delay_print(f"    Notes: {t['notes']}")
    print_line()

def complete_task_by_id(task_id):
    t = next((x for x in tasks if x["id"] == task_id), None)
    if not t:
        delay_print("Task not found.")
        return
    if t["done"]:
        delay_print("Task already completed.")
        return
    t["done"] = True
    t["completed_at"] = datetime.now().isoformat()
    player["xp"] += t["xp"]
    history.append({"id": t["id"], "title": t["title"], "xp": t["xp"], "when": t["completed_at"]})
    # streak handling (increase if last_active_date is yesterday or today)
    today_str = date.today().isoformat()
    last = player.get("last_active_date")
    if last is None:
        player["streak"] = 1
    else:
        try:
            last_date = datetime.fromisoformat(last).date()
            if (date.today() - last_date).days == 0:
                # same day, do not double-increment
                pass
            elif (date.today() - last_date).days == 1:
                player["streak"] = player.get("streak", 0) + 1
            else:
                player["streak"] = 1
        except:
            player["streak"] = 1
    player["last_active_date"] = datetime.now().isoformat()
    # feedback & motivational message
    delay_print(f"✅ Completed: {t['title']} (+{t['xp']} XP)")
    delay_print(f"💬 {random.choice(feedbacks)}")
    delay_print(f"💡 {random.choice(motivations)}")
    # random badge chance
    if random.randint(1, 4) == 1:
        badge = random.choice(badge_pool)
        if badge["id"] not in player["badges"]:
            player["badges"].append(badge["id"])
            delay_print(f"🏅 Badge earned: {badge['name']}")
    check_level_up()
    save_state(state)

def check_level_up():
    required = player["level"] * 150  # slightly larger thresholds for real use
    while player["xp"] >= required:
        player["xp"] -= required
        player["level"] += 1
        delay_print(f"⚡ Level up! You are now Level {player['level']}")
        required = player["level"] * 150

def show_stats():
    print_line()
    delay_print(f"Player: {player.get('name','Player')}  |  Level: {player.get('level',1)}  |  XP: {player.get('xp',0)}")
    delay_print(f"Completed tasks: {len(history)}  |  Current Streak: {player.get('streak',0)} days")
    if player.get('badges'):
        badge_names = [b['name'] for b in badge_pool if b['id'] in player['badges']]
        delay_print(f"Badges: {', '.join(badge_names)}")
    else:
        delay_print("Badges: None yet")
    # last 5 history
    if history:
        delay_print("\nRecent completions:")
        for h in history[-5:]:
            when = h.get("when","")
            delay_print(f" - {h['title']} (+{h['xp']} XP) at {when}")
    print_line()

# -------------------------
# Pomodoro / Focus Timer
# -------------------------
def countdown(minutes):
    seconds = minutes * 60
    try:
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            timer = f"{mins:02d}:{secs:02d}"
            print(f"\rTimer: {timer}", end="", flush=True)
            time.sleep(1)
            seconds -= 1
        print()
    except KeyboardInterrupt:
        print()
        delay_print("Timer stopped.")

def start_pomodoro(work_minutes=25, break_minutes=5, cycles=1):
    delay_print(f"Starting Pomodoro: {work_minutes}m work, {break_minutes}m break, {cycles} cycles.")
    for c in range(cycles):
        delay_print(f"Work session {c+1} — focus.")
        countdown(work_minutes)
        delay_print("Work session complete. Time for a break.")
        countdown(break_minutes)
    delay_print("Pomodoro completed. Nice focus session!")

# -------------------------
# Quick import sample tasks
# -------------------------
def load_sample_tasks():
    sample = [
        {"title": "Analyze data or prepare a report", "xp": 60, "priority": "high", "tags": ["work"], "notes": ""},
        {"title": "Complete a coding or software project", "xp": 80, "priority": "high", "tags": ["dev"], "notes": ""},
        {"title": "Draft an article or presentation", "xp": 40, "priority": "medium", "tags": ["writing"], "notes": ""},
        {"title": "Study a new technical concept", "xp": 30, "priority": "medium", "tags": ["learning"], "notes": ""},
        {"title": "Organize digital workspace (files/emails)", "xp": 25, "priority": "low", "tags": ["org"], "notes": ""},
    ]
    for s in sample:
        add_task(s["title"], xp=s["xp"], priority=s["priority"], tags=s["tags"], notes=s["notes"])

# -------------------------
# Interactive menu
# -------------------------
def prompt_add_task():
    title = input("Task title: ").strip()
    if not title:
        delay_print("Task title cannot be empty.")
        return
    xp_in = input("XP value (default 30): ").strip()
    xp = int(xp_in) if xp_in.isdigit() else 30
    priority = input("Priority (low/medium/high) [medium]: ").strip() or "medium"
    tags = input("Tags (comma separated) [none]: ").strip()
    tags_list = [t.strip() for t in tags.split(",")] if tags else []
    notes = input("Short notes (optional): ").strip()
    add_task(title, xp=xp, priority=priority, tags=tags_list, notes=notes)

def prompt_edit_task():
    list_tasks()
    tid = input("Enter task id to edit: ").strip()
    if not tid.isdigit():
        delay_print("Invalid id.")
        return
    tid = int(tid)
    t = next((x for x in tasks if x["id"] == tid), None)
    if not t:
        delay_print("Task not found.")
        return
    delay_print(f"Editing [{t['id']}] {t['title']}. Leave blank to keep current.")
    title = input(f"Title [{t['title']}]: ").strip() or t['title']
    xp_in = input(f"XP [{t['xp']}]: ").strip()
    xp = int(xp_in) if xp_in.isdigit() else t['xp']
    priority = input(f"Priority [{t['priority']}]: ").strip() or t['priority']
    notes = input(f"Notes [{t.get('notes','')}]: ").strip() or t.get('notes','')
    edit_task(tid, title=title, xp=xp, priority=priority, notes=notes)

def prompt_complete_task():
    list_tasks()
    tid = input("Enter task id to mark complete: ").strip()
    if not tid.isdigit():
        delay_print("Invalid id.")
        return
    complete_task_by_id(int(tid))

def prompt_delete_task():
    list_tasks()
    tid = input("Enter task id to delete: ").strip()
    if not tid.isdigit():
        delay_print("Invalid id.")
        return
    confirm = input("Type 'yes' to confirm deletion: ").strip().lower()
    if confirm == "yes":
        delete_task(int(tid))
    else:
        delay_print("Deletion cancelled.")

def menu_loop():
    delay_print(f"🔥 Welcome to TaskForge, {player.get('name','User')}! Forge your day. 🔥", 0.02)
    while True:
        print_line()
        safe_print("Options:")
        safe_print("[1] List tasks")
        safe_print("[2] Add task")
        safe_print("[3] Edit task")
        safe_print("[4] Complete task")
        safe_print("[5] Delete task")
        safe_print("[6] Challenge mode (3 quick tasks)")
        safe_print("[7] Start Pomodoro")
        safe_print("[8] Show stats")
        safe_print("[9] Load sample tasks")
        safe_print("[0] Save & Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            list_tasks()
        elif choice == "2":
            prompt_add_task()
        elif choice == "3":
            prompt_edit_task()
        elif choice == "4":
            prompt_complete_task()
        elif choice == "5":
            prompt_delete_task()
        elif choice == "6":
            challenge_mode()
        elif choice == "7":
            try:
                w = int(input("Work minutes [25]: ").strip() or 25)
                b = int(input("Break minutes [5]: ").strip() or 5)
                c = int(input("Cycles [1]: ").strip() or 1)
            except:
                delay_print("Invalid input. Using defaults 25/5/1.")
                w, b, c = 25, 5, 1
            start_pomodoro(w, b, c)
        elif choice == "8":
            show_stats()
        elif choice == "9":
            load_sample_tasks()
        elif choice == "0":
            saved = save_state(state)
            if saved:
                delay_print("State saved. Goodbye!")
            else:
                delay_print("Could not save here, but your session will end. Goodbye!")
            break
        else:
            delay_print("Invalid choice. Try again.")

# -------------------------
# Start
# -------------------------
if __name__ == "__main__":
    # Ensure created_at times are present on loaded tasks (backwards compatibility)
    for t in tasks:
        t.setdefault("created_at", datetime.now().isoformat())
    # Try initial save to detect permissions
    if not save_state(state):
        delay_print("[Info] Save failed — this environment may not allow writing files.")
    menu_loop()
