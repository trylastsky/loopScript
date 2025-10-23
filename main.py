import keyboard
import subprocess
import os
import pyautogui
import time

# Укажите путь к вашему PowerShell-скрипту
powershell_script_path = os.path.join(os.getcwd(), 'MoveCursor.ps1')

def move_cursor_to_center():
    # Перемещение курсора в центр экрана
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", powershell_script_path])

    # Отправка комбинации клавиш Ctrl + Alt + -
    pyautogui.hotkey('ctrl', 'alt', '-')

def bind_key():
    print("Введите клавишу для биндинга (например, 'p' или 'mouse5'):")
    key = keyboard.read_event()  # Ждет ввода клавиши

    # Проверка, является ли нажатие на клавишкрой
    if key.event_type == keyboard.KEY_DOWN:
        key_name = key.name
        print(f"Вы назначили клавишу: {key_name}")
        
        # Удаляем предыдущий биндинг, если он существует
        keyboard.unhook_all_hotkeys()
        
        # Назначьте действие на новую клавишу
        keyboard.add_hotkey(key_name, move_cursor_to_center)
        print(f"Теперь нажатие '{key_name}' будет перемещать курсор в центр экрана.")
    
def main():
    bind_key()
    
    print("Процесс запущен. Нажмите 'Esc' для выхода.")
    keyboard.wait('esc')  # Ждем нажатия клавиши 'Esc' для выхода
    
if __name__ == "__main__":
    main()
