import os
import subprocess
import pyautogui
import keyboard
import time
import sys
import json
from rich.console import Console
import inquirer

console = Console()

key_bindings = {}
paused = False
BINDINGS_FILE = "key_bindings.json"

def logo():
    console.clear()
    console.print(
        r"""
        [bold blue]
        LOOPSCRIPT
        [/bold blue]
        """
    )

def save_bindings_to_file():
    """Сохраняет текущие привязки в JSON файл"""
    try:
        with open(BINDINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(key_bindings.keys()), f, ensure_ascii=False, indent=2)
        console.print(f"Привязки сохранены в файл: {BINDINGS_FILE}", style="green")
    except Exception as e:
        console.print(f"Ошибка при сохранении привязок: {e}", style="red")

def load_bindings_from_file():
    """Загружает привязки из JSON файла и восстанавливает их"""
    global key_bindings
    
    if not os.path.exists(BINDINGS_FILE):
        console.print("Файл с привязками не найден.", style="yellow")
        return
    
    try:
        with open(BINDINGS_FILE, 'r', encoding='utf-8') as f:
            saved_keys = json.load(f)
        
        # Восстанавливаем привязки
        for key_name in saved_keys:
            keyboard.add_hotkey(key_name, move_cursor_to_center)
            key_bindings[key_name] = True  # Просто отмечаем что привязка есть
        
        console.print(f"Загружено {len(saved_keys)} привязок из файла", style="green")
        
    except Exception as e:
        console.print(f"Ошибка при загрузке привязок: {e}", style="red")

def move_cursor_to_center():
    if not paused:
        try:
            powershell_script_path = os.path.join(os.getcwd(), 'MoveCursor.ps1')
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", powershell_script_path], 
                         capture_output=True, text=True)
            pyautogui.hotkey('ctrl', 'alt', '-')
        except Exception as e:
            console.print(f"Ошибка при выполнении действия: {e}", style="red")

def bind_key():
    console.clear()
    console.print("Нажмите клавишу для биндинга (например, 'p', 'f1', 'mouse5'): ")

    # Ждем, пока пользователь нажмет клавишу
    event = keyboard.read_event(suppress=True)
    
    if event.event_type == keyboard.KEY_DOWN:
        key_name = event.name
        console.print(f"Вы назначили клавишу: {key_name}", style="green")

        # Удаляем все старые привязки и создаем новую (как в старой версии)
        keyboard.unhook_all_hotkeys()
        
        # Добавляем привязку для перемещения курсора
        keyboard.add_hotkey(key_name, move_cursor_to_center)
        
        # Добавляем привязку для паузы
        keyboard.add_hotkey('pause', toggle_pause)
        
        # Обновляем словарь привязок
        key_bindings.clear()
        key_bindings[key_name] = True
        
        console.print(f"Теперь нажатие '{key_name}' будет перемещать курсор в центр экрана.", style="blue")
        console.print("Нажатие 'pause' будет приостанавливать/возобновлять скрипт.", style="blue")
        
        # Сохраняем привязки в файл
        save_bindings_to_file()
        
    console.print("\nНажмите любую клавишу, чтобы вернуться в меню...")
    keyboard.read_event(suppress=True)

def delete_binding():
    console.clear()
    if not key_bindings:
        console.print("Нет активных привязок для удаления.", style="yellow")
        console.print("\nНажмите любую клавишу, чтобы вернуться в меню...")
        keyboard.read_event(suppress=True)
        return

    console.print("Нажмите клавишу, привязку которой вы хотите удалить:")
    
    # Показываем текущие привязки
    console.print("\nТекущие привязки:", style="bold")
    for key in key_bindings.keys():
        console.print(f"  - {key}")

    # Ждем, пока пользователь нажмет клавишу
    event = keyboard.read_event(suppress=True)
    
    if event.event_type == keyboard.KEY_DOWN:
        key_name = event.name
        # Удаляем привязку, если она существует
        if key_name in key_bindings:
            # Полностью пересоздаем все привязки кроме удаляемой
            keyboard.unhook_all_hotkeys()
            
            # Добавляем привязку для паузы
            keyboard.add_hotkey('pause', toggle_pause)
            
            # Удаляем из словаря
            del key_bindings[key_name]
            
            # Добавляем оставшиеся привязки
            for key in key_bindings.keys():
                keyboard.add_hotkey(key, move_cursor_to_center)
            
            console.print(f"Привязка клавиши '{key_name}' удалена.", style="green")
            
            # Сохраняем обновленные привязки в файл
            save_bindings_to_file()
        else:
            console.print(f"Привязка для клавиши '{key_name}' не найдена.", style="red")
    
    console.print("\nНажмите любую клавишу, чтобы вернуться в меню...")
    keyboard.read_event(suppress=True)

def clear_all_bindings():
    """Очищает все привязки"""
    global key_bindings
    
    console.clear()
    if not key_bindings:
        console.print("Нет активных привязок для очистки.", style="yellow")
    else:
        # Удаляем все горячие клавиши кроме паузы
        keyboard.unhook_all_hotkeys()
        keyboard.add_hotkey('pause', toggle_pause)
        
        key_bindings.clear()
        console.print("Все привязки очищены.", style="green")
        
        # Сохраняем пустой список в файл
        save_bindings_to_file()
    
    console.print("\nНажмите любую клавишу, чтобы вернуться в меню...")
    keyboard.read_event(suppress=True)

def toggle_pause():
    global paused
    paused = not paused
    state = "приостановлен" if paused else "возобновлён"
    console.print(f"\nСкрипт {state}.", style="yellow")

def display_menu():
    while True:
        logo()
        questions = [
            inquirer.List('action',
                          message="Выберите команду",
                          choices=["Бинд клавишу для перемещения курсора", 
                                   "Удалить привязку клавиши", 
                                   "Показать текущие привязки",
                                   "Очистить все привязки",
                                   "Выход из программы"],
                          ),
        ]
        answers = inquirer.prompt(questions)

        if answers['action'] == "Бинд клавишу для перемещения курсора":
            bind_key()
        elif answers['action'] == "Удалить привязку клавиши":
            delete_binding()
        elif answers['action'] == "Показать текущие привязки":
            console.clear()
            if key_bindings:
                console.print("Текущие привязки:", style="bold green")
                for key in key_bindings.keys():
                    console.print(f"  - {key}")
                
                if os.path.exists(BINDINGS_FILE):
                    file_size = os.path.getsize(BINDINGS_FILE)
                    console.print(f"\nФайл с привязками: {BINDINGS_FILE} ({file_size} байт)")
            else:
                console.print("Нет активных привязок.", style="yellow")
            console.print("\nНажмите любую клавишу, чтобы вернуться в меню...")
            keyboard.read_event(suppress=True)
        elif answers['action'] == "Очистить все привязки":
            clear_all_bindings()
        elif answers['action'] == "Выход из программы":
            console.print("Выход из программы...", style="bold red")
            # Сохраняем привязки перед выходом
            save_bindings_to_file()
            sys.exit()

if __name__ == "__main__":
    # Загружаем привязки из файла при запуске
    load_bindings_from_file()
    
    # Настройка горячих клавиш для приостановки и возобновления
    keyboard.add_hotkey('pause', toggle_pause)

    try:
        console.print("Скрипт запущен. Используйте меню для управления.", style="bold green")
        display_menu()
    except KeyboardInterrupt:
        console.print("\nПрограмма прервана пользователем.", style="bold red")
        # Сохраняем привязки перед выходом
        save_bindings_to_file()