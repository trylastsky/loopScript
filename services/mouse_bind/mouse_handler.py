import json
import os
import threading
from pynput import mouse

class MouseHandler:
    def __init__(self):
        self.mouse_listener = None
        self.binding_listener = None
        self.is_processing = False
        self.load_key_names()
    
    def load_key_names(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, 'key_names.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            self.key_names = json.load(f)
    
    def get_key_name(self, key):
        return self.key_names.get(key, key.upper())
    
    def setup_mouse_hotkey(self, mouse_key, callback):
        """Настройка отслеживания нажатий мыши для горячей клавиши"""
        def on_click(x, y, button, pressed):
            if pressed and not self.is_processing and self.check_button_match(mouse_key, button):
                self.is_processing = True
                try:
                    if self.mouse_listener:
                        self.mouse_listener.stop()
                    def execute_callback():
                        try:
                            callback()
                        finally:
                            self.restart_mouse_listener(mouse_key, callback)
                    
                    thread = threading.Thread(target=execute_callback)
                    thread.daemon = True
                    thread.start()
                    
                except Exception as e:
                    print(f"Ошибка в обработчике мыши: {e}")
                    self.is_processing = False
                    self.restart_mouse_listener(mouse_key, callback)
                
                return False
        
        self.stop_listener()
        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()
    
    def restart_mouse_listener(self, mouse_key, callback):
        """Перезапуск слушателя мыши"""
        self.is_processing = False
        self.setup_mouse_hotkey(mouse_key, callback)
    
    def start_binding_listener(self, callback):
        """Запуск слушателя для привязки кнопок мыши"""
        def on_click(x, y, button, pressed):
            if pressed:
                callback(button)
                return False
        
        self.stop_binding_listener()
        self.binding_listener = mouse.Listener(on_click=on_click)
        self.binding_listener.start()
    
    def stop_binding_listener(self):
        """Остановка слушателя для привязки"""
        if self.binding_listener:
            self.binding_listener.stop()
            self.binding_listener = None
    
    def check_button_match(self, mouse_key, button):
        """Проверяет соответствие нажатой кнопки мыши"""
        button_mapping = {
            'mouse_left': mouse.Button.left,
            'mouse_right': mouse.Button.right,
            'mouse_middle': mouse.Button.middle
        }
        
        if mouse_key in button_mapping and button == button_mapping[mouse_key]:
            return True
        
        if mouse_key == 'mouse_button4':
            return (hasattr(button, 'name') and button.name == 'x1') or str(button) == 'Button.button8'
        
        if mouse_key == 'mouse_button5':
            return (hasattr(button, 'name') and button.name == 'x2') or str(button) == 'Button.button9'
        
        if mouse_key.startswith('mouse_button'):
            try:
                btn_num = int(mouse_key.replace('mouse_button', ''))
                if btn_num >= 6:
                    return str(button) == f'Button.button{btn_num + 2}'
            except:
                pass
        
        return False
    
    def button_to_key_name(self, button):
        """Преобразует объект кнопки мыши в строковый идентификатор"""
        if button == mouse.Button.left:
            return 'mouse_left'
        elif button == mouse.Button.right:
            return 'mouse_right'
        elif button == mouse.Button.middle:
            return 'mouse_middle'
        elif hasattr(button, 'name'):
            if button.name == 'x1':
                return 'mouse_button4'
            elif button.name == 'x2':
                return 'mouse_button5'
            else:
                return f'mouse_{button.name}'
        else:
            try:
                btn_str = str(button)
                if 'button8' in btn_str:
                    return 'mouse_button8'
                elif 'button9' in btn_str:
                    return 'mouse_button9'
                elif 'button10' in btn_str:
                    return 'mouse_button10'
                elif 'button' in btn_str:
                    return f'mouse_{btn_str.split(".")[-1].lower()}'
            except:
                return f'mouse_unknown_{hash(button) % 1000}'
    
    def stop_listener(self):
        """Остановка основного слушателя мыши"""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        self.is_processing = False
    
    def stop_all(self):
        """Остановка всех слушателей"""
        self.stop_listener()
        self.stop_binding_listener()