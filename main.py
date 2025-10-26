import os
import subprocess
import pyautogui
import keyboard
import time
import sys
from rich.console import Console
import inquirer
from services.mouse_bind.mouse_handler import MouseHandler

console = Console()

paused = False
current_hotkey = None
mouse_handler = MouseHandler()

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
            mouse_handler.stop_listener()
            powershell_script_path = os.path.join(os.getcwd(), 'MoveCursor.ps1')
            if os.path.exists(powershell_script_path):
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", powershell_script_path], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode != 0:
                    console.print(f"Ошибка PowerShell: {result.stderr}", style="red")
            else:
                console.print("Файл MoveCursor.ps1 не найден", style="red")
                return
            pyautogui.hotkey('ctrl', 'alt', '-')
        except Exception as e:
            console.print(f"Ошибка при выполнении действия: {e}", style="red")
        finally:
            #Перезапускаем слушатель мыши если есть активная привязка
            if current_hotkey and current_hotkey.startswith('mouse_'):
                mouse_handler.setup_mouse_hotkey(current_hotkey, move_cursor_to_center)

def bind_key():
    global current_hotkey
    
    console.clear()
    console.print("Нажмите ОДНУ клавишу или кнопку мыши для привязки:", style="bold yellow")
    console.print("Клавиши: 'p', 'f1', 'space' и т.д.", style="yellow")
    console.print("Кнопки мыши: левая, правая, средняя, кнопка 4, кнопка 5 и т.д.", style="yellow")
    console.print("Нажмите ESC для отмены", style="yellow")
    console.print("\nОжидание нажатия...", style="green")

    keyboard.unhook_all_hotkeys()
    mouse_handler.stop_all()
    
    recorded_key = None
    
    def on_key_event(e):
        nonlocal recorded_key
        if e.event_type == keyboard.KEY_DOWN:
            if e.name in ['ctrl', 'alt', 'shift', 'windows']:
                return
            if e.name == 'esc':
                recorded_key = 'esc'
                return False
            recorded_key = e.name
            return False
    
    def on_mouse_click(button):
        nonlocal recorded_key
        recorded_key = mouse_handler.button_to_key_name(button)
    
    # Запускаем слушатели
    keyboard.hook(on_key_event)
    mouse_handler.start_binding_listener(on_mouse_click)
    
    start_time = time.time()
    while recorded_key is None and (time.time() - start_time) < 10:
        time.sleep(0.1)
    
    keyboard.unhook_all()
    mouse_handler.stop_binding_listener()
    
    if recorded_key is None:
        console.print("Время ожидания истекло", style="red")
        time.sleep(1)
        if current_hotkey:
            setup_hotkey(current_hotkey)
        keyboard.add_hotkey('pause', toggle_pause)
        return
    
    if recorded_key == 'esc':
        console.print("Отмена привязки", style="yellow")
        time.sleep(1)
        if current_hotkey:
            setup_hotkey(current_hotkey)
        keyboard.add_hotkey('pause', toggle_pause)
        return
    
    if current_hotkey:
        remove_hotkey(current_hotkey)
    
    try:
        setup_hotkey(recorded_key)
        current_hotkey = recorded_key
        key_name = mouse_handler.get_key_name(recorded_key)
        console.print(f"✅ Успешная привязка '{key_name}'!", style="bold green")
    except Exception as e:
        console.print(f"Ошибка при создании горячей клавиши: {e}", style="red")
    
    keyboard.add_hotkey('pause', toggle_pause)
    
    console.print("\nНажмите ENTER чтобы вернуться в меню...", style="yellow")
    keyboard.wait('enter')
    time.sleep(0.5)

def setup_hotkey(key):
    """Настройка горячей клавиши"""
    if key.startswith('mouse_'):
        mouse_handler.setup_mouse_hotkey(key, move_cursor_to_center)
    else:
        keyboard.add_hotkey(key, move_cursor_to_center)

def remove_hotkey(key):
    """Удаление горячей клавиши"""
    if key.startswith('mouse_'):
        mouse_handler.stop_listener()
    else:
        try:
            keyboard.remove_hotkey(key)
        except:
            pass

def delete_binding():
    global current_hotkey
    
    console.clear()
    
    if current_hotkey:
        try:
            remove_hotkey(current_hotkey)
            current_hotkey = None
            if os.path.exists('hotkey.txt'):
                os.remove('hotkey.txt')
            console.print("✅ Успешная отвязка!", style="bold green")
        except Exception as e:
            console.print(f"Ошибка при удалении привязки: {e}", style="red")
    else:
        console.print("Нет активных привязок для удаления", style="yellow")
    
    console.print("\nНажмите ENTER чтобы вернуться в меню...", style="yellow")
    keyboard.wait('enter')
    time.sleep(0.5)

def toggle_pause():
    global paused
    paused = not paused
    state = "приостановлен" if paused else "возобновлён"
    console.print(f"\nСкрипт {state}.", style="yellow")
    if not paused and current_hotkey and current_hotkey.startswith('mouse_'):
        mouse_handler.setup_mouse_hotkey(current_hotkey, move_cursor_to_center)

def clear_input_buffer():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except:
        pass

def display_menu():
    while True:
        logo()
        
        if current_hotkey:
            key_name = mouse_handler.get_key_name(current_hotkey)
            console.print(f"Текущая привязка: [green]{key_name}[/green]")
        else:
            console.print("Текущая привязка: [red]нет[/red]")
        clear_input_buffer()
        time.sleep(0.1)
        
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
        
        try:
            answers = inquirer.prompt(questions)
            
            if not answers:
                break
                
            action = answers['action']
            
            if action == "Привязать кнопку":
                bind_key()
                continue
            elif action == "Отвязать кнопку":
                delete_binding()
                continue
            elif action == "Сохранить и выйти":
                console.print("Выход из программы...", style="bold green")
                if current_hotkey:
                    try:
                        with open('hotkey.txt', 'w') as f:
                            f.write(current_hotkey)
                    except:
                        pass
                mouse_handler.stop_all()
                sys.exit()
                
        except KeyboardInterrupt:
            console.print("\nВыход из программы...", style="bold yellow")
            mouse_handler.stop_all()
            sys.exit()
        except Exception as e:
            console.print(f"Ошибка: {e}", style="bold red")

def load_saved_hotkey():
    global current_hotkey
    try:
        if os.path.exists('hotkey.txt'):
            with open('hotkey.txt', 'r') as f:
                saved_key = f.read().strip()
                if saved_key:
                    setup_hotkey(saved_key)
                    current_hotkey = saved_key
                    key_name = mouse_handler.get_key_name(saved_key)
                    console.print(f"✅ Загружена сохраненная привязка: {key_name}", style="green")
    except:
        pass

if __name__ == "__main__":
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
        mouse_handler.stop_all()