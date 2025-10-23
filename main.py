import os
import subprocess
import pyautogui
import keyboard
import time
import sys
from rich.console import Console
import inquirer

console = Console()

paused = False

def logo():
    console.clear()
    console.print(
        r"""
        [bold blue]
        LOOPSCRIPT
        [/bold blue]
        """
    )

def move_cursor_to_center():
    if not paused:
        try:
            powershell_script_path = os.path.join(os.getcwd(), 'MoveCursor.ps1')
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", powershell_script_path])
            pyautogui.hotkey('ctrl', 'alt', '-')
        except Exception as e:
            console.print(f"Ошибка при выполнении действия: {e}", style="red")

def bind_key():
    console.clear()
    console.print("Нажмите клавишу для привязки (например, 'p', 'f1', 'mouse5'): ")

    event = keyboard.read_event(suppress=True)
    
    if event.event_type == keyboard.KEY_DOWN:
        key_name = event.name
        
        keyboard.unhook_all_hotkeys()
        
        keyboard.add_hotkey(key_name, move_cursor_to_center)
        keyboard.add_hotkey('pause', toggle_pause)
        
        console.print("✅ Успешная привязка!", style="bold green")
        console.print(f"Теперь нажатие '{key_name}' будет перемещать курсор в центр экрана.", style="blue")
        
    console.print("\nНажмите любую клавишу, чтобы вернуться в меню...")
    keyboard.read_event(suppress=True)

def delete_binding():
    console.clear()
    
    keyboard.unhook_all_hotkeys()
    keyboard.add_hotkey('pause', toggle_pause)
    
    console.print("✅ Успешная отвязка!", style="bold green")
    
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
                          choices=[
                              "Привязать кнопку", 
                              "Отвязать кнопку", 
                              "Сохранить и выйти"
                          ],
                          ),
        ]
        answers = inquirer.prompt(questions)

        action = answers['action']
        
        if action == "Привязать кнопку":
            bind_key()
        elif action == "Отвязать кнопку":
            delete_binding()
        elif action == "Сохранить и выйти":
            console.print("Сохранение и выход из программы...", style="bold green")
            sys.exit()

if __name__ == "__main__":
    keyboard.add_hotkey('pause', toggle_pause)

    try:
        console.print("Скрипт запущен. Используйте меню для управления.", style="bold green")
        display_menu()
    except KeyboardInterrupt:
        console.print("\nПрограмма прервана пользователем.", style="bold red")
    except Exception as e:
        console.print(f"Неожиданная ошибка: {e}", style="bold red")