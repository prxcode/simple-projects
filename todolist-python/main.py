# Functions to manage tasks
def add_task():
    task = input("Enter the task: ")
    with open("tasks.txt", "a") as f:
        f.write(task + "\n")
    print("Task added.")

def view_all_tasks():
    try:
        with open("tasks.txt", "r") as f:
            tasks = f.readlines()
            if tasks:
                for i, task in enumerate(tasks, 1):
                    print(f"{i}. {task.strip()}")
            else:
                print("No tasks.")
    except FileNotFoundError:
        print("No tasks found.")

def delete_task():
    try:
        with open("tasks.txt", "r") as f:
            tasks = f.readlines()
        if tasks:
            for i, task in enumerate(tasks, 1):
                print(f"{i}. {task.strip()}")
            task_num = int(input("Enter task number to delete: "))
            tasks.pop(task_num - 1)
            with open("tasks.txt", "w") as f:
                f.writelines(tasks)
            print("Task deleted.")
        else:
            print("No tasks to delete.")
    except FileNotFoundError:
        print("No tasks found.")

def edit_task():
    try:
        with open("tasks.txt", "r") as f:
            tasks = f.readlines()
        if tasks:
            for i, task in enumerate(tasks, 1):
                print(f"{i}. {task.strip()}")
            task_num = int(input("Enter task number to edit: "))
            new_task = input("Enter new task: ")
            tasks[task_num - 1] = new_task + "\n"
            with open("tasks.txt", "w") as f:
                f.writelines(tasks)
            print("Task updated.")
        else:
            print("No tasks to edit.")
    except FileNotFoundError:
        print("No tasks found.")

def main():
    while True:
        print("\n1. Add task\n2. View tasks\n3. Delete task\n4. Edit task\n5. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            add_task()
        elif choice == "2":
            view_all_tasks()
        elif choice == "3":
            delete_task()
        elif choice == "4":
            edit_task()
        elif choice == "5":
            break
        else:
            print("Invalid option.")

main()
