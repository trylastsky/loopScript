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
current_hotkey = None

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
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", powershell_script_path], capture_output=True)
            pyautogui.hotkey('ctrl', 'alt', '-')
        except Exception as e:
            console.print(f"Ошибка при выполнении действия: {e}", style="red")

def bind_key():
    global current_hotkey
    
    console.clear()
    console.print("Нажмите ОДНУ клавишу для привязки (например, 'p', 'f1', 'space'): ", style="bold yellow")
    console.print("НЕ используйте Ctrl, Alt, Shift отдельно!", style="red")
    console.print("Нажмите ESC для отмены", style="yellow")
    console.print("\nОжидание нажатия клавиши...", style="green")

    # Временно убираем все горячие клавиши
    keyboard.unhook_all_hotkeys()
    
    recorded_key = None
    
    def on_key_event(e):
        nonlocal recorded_key
        if e.event_type == keyboard.KEY_DOWN:
            # Игнорируем модификаторы (Ctrl, Alt, Shift)
            if e.name in ['ctrl', 'alt', 'shift', 'windows']:
                return
            if e.name == 'esc':  # Отмена при нажатии ESC
                recorded_key = 'esc'
                return False
            recorded_key = e.name
            return False  # Останавливаем запись
    
    # Начинаем запись нажатия
    keyboard.hook(on_key_event)
    
    # Ждем пока пользователь нажмет клавишу (без таймаута)
    while recorded_key is None:
        time.sleep(0.1)
    
    keyboard.unhook_all()  # Останавливаем запись
    
    if recorded_key == 'esc':
        console.print("Отмена привязки", style="yellow")
        time.sleep(1)
        # Восстанавливаем горячие клавиши
        if current_hotkey:
            keyboard.add_hotkey(current_hotkey, move_cursor_to_center)
        keyboard.add_hotkey('pause', toggle_pause)
        return
    
    # Удаляем предыдущую привязку
    if current_hotkey:
        try:
            keyboard.remove_hotkey(current_hotkey)
        except:
            pass
    
    # Создаем новую привязку
    try:
        keyboard.add_hotkey(recorded_key, move_cursor_to_center)
        current_hotkey = recorded_key
        
        console.print(f"✅ Успешная привязка клавиши '{recorded_key}'!", style="bold green")
        
    except Exception as e:
        console.print(f"Ошибка при создании горячей клавиши: {e}", style="red")
    
    # Всегда восстанавливаем паузу
    keyboard.add_hotkey('pause', toggle_pause)
    
    console.print("\nНажмите ENTER чтобы вернуться в меню...", style="yellow")
    
    # Ждем конкретно ENTER для возврата и очищаем буфер
    keyboard.wait('enter')
    time.sleep(0.5)  # Небольшая пауза для стабилизации

def delete_binding():
    global current_hotkey
    
    console.clear()
    
    if current_hotkey:
        try:
            keyboard.remove_hotkey(current_hotkey)
            current_hotkey = None
            console.print("✅ Успешная отвязка!", style="bold green")
        except Exception as e:
            console.print(f"Ошибка при удалении привязки: {e}", style="red")
    else:
        console.print("Нет активных привязок для удаления", style="yellow")
    
    console.print("\nНажмите ENTER чтобы вернуться в меню...", style="yellow")
    
    # Ждем конкретно ENTER для возврата и очищаем буфер
    keyboard.wait('enter')
    time.sleep(0.5)  # Небольшая пауза для стабилизации

def toggle_pause():
    global paused
    paused = not paused
    state = "приостановлен" if paused else "возобновлён"
    console.print(f"\nСкрипт {state}.", style="yellow")

def clear_input_buffer():
    """Очищает буфер ввода"""
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except:
        pass

def display_menu():
    while True:
        logo()
        
        # Показываем текущую привязку
        if current_hotkey:
            console.print(f"Текущая привязка: [green]{current_hotkey}[/green]")
        else:
            console.print("Текущая привязка: [red]нет[/red]")
        
        # Очищаем буфер перед показом меню
        clear_input_buffer()
        time.sleep(0.1)
        
        questions = [
            inquirer.List('action',
                          message="Выберите команду",
                          choices=[
                              "Привязать кнопку", 
                              "Отвязать кнопку", 
                              "Выход"
                          ],
                          ),
        ]
        
        try:
            answers = inquirer.prompt(questions)
            
            if not answers:
                break
                
            action = answers['action']
            
            if action == "Привязать кнопку":
                bind_key()
                # После возврата из bind_key продолжаем цикл меню
                continue
            elif action == "Отвязать кнопку":
                delete_binding()
                # После возврата из delete_binding продолжаем цикл меню
                continue
            elif action == "Выход":
                console.print("Выход из программы...", style="bold green")
                # Сохраняем привязку в файл перед выходом
                if current_hotkey:
                    try:
                        with open('hotkey.txt', 'w') as f:
                            f.write(current_hotkey)
                    except:
                        pass
                sys.exit()
                
        except KeyboardInterrupt:
            console.print("\nВыход из программы...", style="bold yellow")
            sys.exit()
        except Exception as e:
            console.print(f"Ошибка: {e}", style="bold red")

def load_saved_hotkey():
    """Загружает сохраненную привязку из файла"""
    global current_hotkey
    try:
        if os.path.exists('hotkey.txt'):
            with open('hotkey.txt', 'r') as f:
                saved_key = f.read().strip()
                if saved_key:
                    keyboard.add_hotkey(saved_key, move_cursor_to_center)
                    current_hotkey = saved_key
                    console.print(f"✅ Загружена сохраненная привязка: {saved_key}", style="green")
    except:
        pass

if __name__ == "__main__":
    # Загружаем сохраненную привязку при запуске
    load_saved_hotkey()
    
    keyboard.add_hotkey('pause', toggle_pause)

    try:
        console.print("Скрипт запущен. Используйте меню для управления.", style="bold green")
        console.print("PAUSE - приостановка/возобновление", style="yellow")
        display_menu()
    except KeyboardInterrupt:
        console.print("\nПрограмма прервана пользователем.", style="bold red")
    except Exception as e:
        console.print(f"Неожиданная ошибка: {e}", style="bold red")
    finally:
        keyboard.unhook_all()