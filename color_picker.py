import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pyautogui
import keyboard
import threading
import time
import pyperclip
import json
import os
from tkinter import messagebox
from PIL import Image, ImageTk, ImageGrab
import win32con
import win32gui
import win32api
import customtkinter as ctk
from datetime import datetime
import pystray
from PIL import Image, ImageDraw
import winreg  # Windows kayıt defteri işlemleri için
import sys  # sys modülü için
import ctypes

# DPI ayarları
try:
    windll = ctypes.windll.shcore
    windll.SetProcessDpiAwareness(0)  # PROCESS_DPI_UNAWARE
except:
    try:
        windll = ctypes.windll.user32
        windll.SetProcessDPIAware()
    except:
        pass

# CustomTkinter ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Sabit boyutlar
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800
PREVIEW_SIZE = 200
BUTTON_HEIGHT = 30
PADDING = 10

class ColorHistory:
    def __init__(self):
        self.colors = []
        self.max_colors = 24  # 4x6 grid için
        self.load_history()
        
    def add_color(self, rgb, hex_color):
        # Aynı renk zaten varsa, onu başa al
        for color in self.colors:
            if color['hex'] == hex_color:
                self.colors.remove(color)
                break
                
        color_data = {
            'rgb': rgb,
            'hex': hex_color,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.colors.insert(0, color_data)
        if len(self.colors) > self.max_colors:
            self.colors.pop()
        self.save_history()
        
    def load_history(self):
        try:
            if os.path.exists('color_history.json'):
                with open('color_history.json', 'r') as f:
                    self.colors = json.load(f)
        except:
            self.colors = []
            
    def save_history(self):
        with open('color_history.json', 'w') as f:
            json.dump(self.colors, f)

class ColorAdjuster(ctk.CTkToplevel):
    def __init__(self, parent, color_rgb):
        super().__init__(parent)
        self.title("Renk Düzenleyici")
        self.geometry("400x500")
        
        self.r, self.g, self.b = color_rgb
        
        # Renk önizleme
        self.preview = ctk.CTkCanvas(self, width=150, height=150)
        self.preview.pack(pady=20)
        
        # RGB kaydırıcıları
        self.create_slider("Kırmızı (R)", 0, self.r)
        self.create_slider("Yeşil (G)", 1, self.g)
        self.create_slider("Mavi (B)", 2, self.b)
        
        # Parlaklık ve Doygunluk
        self.create_slider("Parlaklık", 3, 100, 0, 200)
        self.create_slider("Doygunluk", 4, 100, 0, 200)
        
        # Kopyalama butonları
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20, fill=X)
        
        ctk.CTkButton(button_frame, text="RGB Kopyala", 
                     command=self.copy_rgb).pack(side=LEFT, expand=True, padx=5)
        ctk.CTkButton(button_frame, text="HEX Kopyala",
                     command=self.copy_hex).pack(side=LEFT, expand=True, padx=5)
        
        self.update_preview()
        
    def create_slider(self, text, row, default, min_val=0, max_val=255):
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, fill=X, padx=20)
        
        label = ctk.CTkLabel(frame, text=text)
        label.pack(side=LEFT)
        
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, number_of_steps=max_val-min_val)
        slider.pack(side=RIGHT, fill=X, expand=True, padx=10)
        slider.set(default)
        slider.bind("<Motion>", lambda e: self.update_preview())
        
        setattr(self, f"slider_{row}", slider)
        
    def update_preview(self):
        r = int(self.slider_0.get())
        g = int(self.slider_1.get())
        b = int(self.slider_2.get())
        
        brightness = self.slider_3.get() / 100
        saturation = self.slider_4.get() / 100
        
        # Parlaklık ve doygunluk ayarları
        r = min(255, max(0, r * brightness))
        g = min(255, max(0, g * brightness))
        b = min(255, max(0, b * brightness))
        
        # Doygunluk ayarı
        gray = (r + g + b) / 3
        r = r * saturation + gray * (1 - saturation)
        g = g * saturation + gray * (1 - saturation)
        b = b * saturation + gray * (1 - saturation)
        
        self.current_color = (int(r), int(g), int(b))
        hex_color = '#{:02x}{:02x}{:02x}'.format(*self.current_color)
        self.preview.configure(bg=hex_color)
        
    def copy_rgb(self):
        pyperclip.copy(f"rgb{self.current_color}")
        
    def copy_hex(self):
        hex_color = '#{:02x}{:02x}{:02x}'.format(*self.current_color)
        pyperclip.copy(hex_color)

class HotkeyDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, current_key):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.geometry("400x200")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                 parent.winfo_rooty() + 50))
        
        frame = ctk.CTkFrame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        label = ctk.CTkLabel(frame, text=f"Yeni kısayol tuşunu giriniz...\nŞu anki: {current_key}")
        label.pack(pady=10)
        
        self.key_label = ctk.CTkLabel(frame, text="Tuş bekleniyor...")
        self.key_label.pack(pady=5)
        
        hint_label = ctk.CTkLabel(frame, 
                                text="Not: Herhangi bir tuş kombinasyonunu kullanabilirsiniz.\n" +
                                     "Modifiye tuşlar (Alt, Shift, Control) opsiyoneldir.",
                                wraplength=350)
        hint_label.pack(pady=10)
        
        self.bind('<Key>', self.on_key_press)
        
    def on_key_press(self, event):
        key_name = event.keysym.lower()
        if key_name in ['shift_l', 'shift_r', 'alt_l', 'alt_r', 'control_l', 'control_r']:
            return
            
        mods = []
        
        # Shift tuşu kontrolü
        if event.state & 1:
            mods.append('shift')
            
        # Control tuşu kontrolü
        if event.state & 4:
            mods.append('control')
            
        # Alt tuşu kontrolü - sadece gerçekten basılıysa
        if event.state & 88 == 88:
            mods.append('alt')
            
        key_combo = '+'.join(mods + [key_name]) if mods else key_name
        self.result = key_combo
        self.key_label.configure(text=f"Seçilen kısayol: {key_combo}")
        self.after(500, self.destroy)

class NotificationWindow(ctk.CTkToplevel):
    def __init__(self, parent, message):
        super().__init__(parent)
        
        # Pencere özelliklerini ayarla
        self.overrideredirect(True)  # Pencere çerçevesini kaldır
        self.attributes('-topmost', True)  # Her zaman üstte
        
        # Ekran boyutlarını al
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Pencere boyutları
        window_width = 200
        window_height = 50
        
        # Sağ alt köşede konumlandır
        x = screen_width - window_width - 20
        y = screen_height - window_height - 100
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Mesaj etiketi
        label = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=12))
        label.pack(expand=True, fill='both', padx=10, pady=5)
        
        # 2 saniye sonra kapat
        self.after(2000, self.destroy)

class ColorPicker:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Renk Seçici")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        
        # Başlangıçta çalıştırılacaklar listesine ekle
        self.add_to_startup()
        
        # İmleç ayarlarını pencere oluştuktan sonra yap
        self.root.after(100, self.set_cursor_icon)
        
        # Sistem tray ikonu oluştur
        self.setup_system_tray()
        
        # Renk geçmişi
        self.color_history = ColorHistory()
        
        # Varsayılan kısayollar
        self.default_hotkeys = {
            'quit': 'q',
            'copy_rgb': 'r',
            'copy_hex': 'h',
            'copy_both': 'b',
            'screenshot': 's'
        }
        
        self.load_hotkeys()
        
        # Ana frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Başlık
        title_label = ctk.CTkLabel(main_frame, text="Renk Seçici",
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(0, PADDING))
        
        # Renk önizleme ve bilgi bölümü
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill=X, pady=(0, PADDING))
        
        self.color_preview = tk.Canvas(preview_frame, width=PREVIEW_SIZE, height=PREVIEW_SIZE,
                                     bg='white', relief="ridge", bd=2)
        self.color_preview.pack(side=LEFT, padx=PADDING)
        
        info_frame = ctk.CTkFrame(preview_frame)
        info_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=PADDING)
        
        self.rgb_label = ctk.CTkLabel(info_frame, text="RGB: (0, 0, 0)",
                                    font=ctk.CTkFont(size=14))
        self.rgb_label.pack(pady=5)
        
        self.hex_label = ctk.CTkLabel(info_frame, text="HEX: #000000",
                                    font=ctk.CTkFont(size=14))
        self.hex_label.pack(pady=5)
        
        self.status_label = ctk.CTkLabel(info_frame, text="Durum: Aktif",
                                       font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=5)
        
        # Kısayol ayarları
        hotkey_frame = ctk.CTkFrame(main_frame)
        hotkey_frame.pack(fill=X, pady=(PADDING, 0))
        
        ctk.CTkLabel(hotkey_frame, text="Kısayol Tuşları",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=PADDING)
        
        self.create_hotkey_row(hotkey_frame, "RGB Kopyala", 'copy_rgb')
        self.create_hotkey_row(hotkey_frame, "HEX Kopyala", 'copy_hex')
        self.create_hotkey_row(hotkey_frame, "İki Formatı Kopyala", 'copy_both')
        self.create_hotkey_row(hotkey_frame, "Ekran Görüntüsü", 'screenshot')
        self.create_hotkey_row(hotkey_frame, "Çıkış", 'quit')
        
        # Renk geçmişi
        history_frame = ctk.CTkFrame(main_frame)
        history_frame.pack(fill=X, pady=PADDING)
        
        history_header = ctk.CTkFrame(history_frame)
        history_header.pack(fill=X, padx=PADDING, pady=PADDING)
        
        ctk.CTkLabel(history_header, text="Renk Geçmişi",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side=LEFT)
        
        ctk.CTkButton(history_header, text="Geçmişi Temizle",
                     command=self.clear_history).pack(side=RIGHT)
        
        # Grid için frame
        self.history_grid = ctk.CTkFrame(history_frame)
        self.history_grid.pack(fill=BOTH, padx=PADDING, pady=PADDING)
        
        # Renk takibi için thread başlatma
        self.running = True
        self.current_color = None
        self.color_thread = threading.Thread(target=self.track_color)
        self.color_thread.daemon = True
        self.color_thread.start()
        
        # Kısayolları ayarla
        self.setup_hotkeys()
        
        # Renk geçmişini güncelle
        self.update_history_display()
        
        # Pencere kapatma olayını yakala
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_system_tray(self):
        # Sistem tray ikonu için görsel oluştur
        icon_size = 64
        icon_image = Image.new('RGB', (icon_size, icon_size), color='white')
        draw = ImageDraw.Draw(icon_image)
        
        # Renkli daireler çiz
        colors = ['red', 'green', 'blue']
        radius = icon_size // 4
        centers = [(icon_size//3, icon_size//3),
                  (2*icon_size//3, icon_size//3),
                  (icon_size//2, 2*icon_size//3)]
        
        for (x, y), color in zip(centers, colors):
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
        
        # Sistem tray menüsü
        menu = (
            pystray.MenuItem("Göster", self.show_window),
            pystray.MenuItem("Çıkış", self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("color_picker", icon_image, "Renk Seçici", menu)
        
        # Tray ikonunu ayrı bir thread'de başlat
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        
    def show_window(self, icon=None, item=None):
        self.root.deiconify()
        self.root.lift()
        
    def on_closing(self):
        self.root.withdraw()  # Pencereyi gizle
        
    def clear_history(self):
        self.color_history.colors = []
        self.color_history.save_history()
        self.update_history_display()
        
    def update_history_display(self):
        # Mevcut grid'i temizle
        for widget in self.history_grid.winfo_children():
            widget.destroy()
            
        if not self.color_history.colors:
            empty_label = ctk.CTkLabel(self.history_grid, 
                                     text="Henüz renk geçmişi yok",
                                     font=ctk.CTkFont(size=12))
            empty_label.pack(pady=PADDING)
            return
            
        # Grid düzeni (4x6)
        rows, cols = 4, 6
        
        for i, color in enumerate(self.color_history.colors):
            row = i // cols
            col = i % cols
            
            # Her renk için frame
            color_frame = ctk.CTkFrame(self.history_grid)
            color_frame.grid(row=row, column=col, padx=PADDING, pady=PADDING, sticky="nsew")
            
            # Renk önizleme
            preview = tk.Canvas(color_frame, width=PADDING, height=PADDING,
                              bg=color['hex'], relief="ridge", bd=1)
            preview.pack(pady=PADDING)
            
            # Renk değerleri
            ctk.CTkLabel(color_frame, text=color['hex'],
                        font=ctk.CTkFont(size=10)).pack()
            
            # Tıklama olayı
            preview.bind("<Button-1>", 
                       lambda e, c=color: self.on_history_color_click(c))
            
        # Grid hücrelerinin boyutlarını ayarla
        for i in range(cols):
            self.history_grid.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.history_grid.grid_rowconfigure(i, weight=1)
            
    def on_history_color_click(self, color):
        r, g, b = eval(color['rgb'].strip('rgb()'))
        adjuster = ColorAdjuster(self.root, (r, g, b))
        
    def take_screenshot(self):
        self.root.iconify()  # Pencereyi küçült
        time.sleep(0.5)  # Küçük bir bekleme
        
        # Ekran görüntüsü al
        screenshot = ImageGrab.grab()
        
        # Geçici dosya oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot.save(filename)
        
        # Panoya kopyala
        from io import BytesIO
        output = BytesIO()
        screenshot.convert('RGB').save(output, 'BMP')
        data = output.getvalue()[14:]  # BMP başlığını atla
        output.close()
        
        import win32clipboard
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, data)
        win32clipboard.CloseClipboard()
        
        self.root.deiconify()  # Pencereyi geri getir
        self.status_label.configure(text=f"Ekran görüntüsü kaydedildi ve panoya kopyalandı")
        self.root.after(2000, lambda: self.status_label.configure(text="Durum: Aktif"))
        
    def load_hotkeys(self):
        try:
            if os.path.exists('hotkeys.json'):
                with open('hotkeys.json', 'r') as f:
                    loaded_hotkeys = json.load(f)
                    self.hotkeys = self.default_hotkeys.copy()
                    for key in loaded_hotkeys:
                        if key in self.hotkeys:
                            self.hotkeys[key] = loaded_hotkeys[key]
            else:
                self.hotkeys = self.default_hotkeys.copy()
        except:
            self.hotkeys = self.default_hotkeys.copy()
        self.save_hotkeys()
            
    def save_hotkeys(self):
        with open('hotkeys.json', 'w') as f:
            json.dump(self.hotkeys, f)
            
    def change_hotkey(self, hotkey_type):
        current_key = self.hotkeys[hotkey_type]
        dialog = HotkeyDialog(self.root, f"Kısayol Tuşu Değiştir - {hotkey_type}", current_key)
        self.root.wait_window(dialog)
        
        if dialog.result:
            try:
                keyboard.remove_hotkey(self.hotkeys[hotkey_type])
            except:
                pass
                
            self.hotkeys[hotkey_type] = dialog.result
            self.save_hotkeys()
            self.setup_hotkeys()
            
            label = getattr(self, f"{hotkey_type}_label")
            label.configure(text=dialog.result)
                
    def setup_hotkeys(self):
        keyboard.unhook_all()
        keyboard.add_hotkey(self.hotkeys['quit'], self.quit_app)
        keyboard.add_hotkey(self.hotkeys['copy_rgb'], self.copy_rgb_to_clipboard)
        keyboard.add_hotkey(self.hotkeys['copy_hex'], self.copy_hex_to_clipboard)
        keyboard.add_hotkey(self.hotkeys['copy_both'], self.copy_both_to_clipboard)
        keyboard.add_hotkey(self.hotkeys['screenshot'], self.take_screenshot)
        
    def track_color(self):
        while self.running:
            try:
                x, y = pyautogui.position()
                pixel = pyautogui.screenshot().getpixel((x, y))
                self.current_color = pixel
                self.update_color_info(pixel)
                time.sleep(0.1)
            except Exception as e:
                self.status_label.configure(text=f"Hata: {str(e)}")
    
    def copy_rgb_to_clipboard(self):
        if self.current_color:
            self.set_cross_cursor()  # Artı işareti cursoru
            r, g, b = self.current_color
            rgb_text = f"rgb({r}, {g}, {b})"
            pyperclip.copy(rgb_text)
            self.color_history.add_color(rgb_text, '#{:02x}{:02x}{:02x}'.format(r, g, b))
            self.update_history_display()
            self.show_copy_notification("RGB")
            self.root.after(1000, self.set_main_cursor)  # 1 saniye sonra normal cursor
            
    def copy_hex_to_clipboard(self):
        if self.current_color:
            self.set_cross_cursor()  # Artı işareti cursoru
            r, g, b = self.current_color
            hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            pyperclip.copy(hex_color)
            self.color_history.add_color(f"rgb({r}, {g}, {b})", hex_color)
            self.update_history_display()
            self.show_copy_notification("HEX")
            self.root.after(1000, self.set_main_cursor)  # 1 saniye sonra normal cursor
            
    def copy_both_to_clipboard(self):
        if self.current_color:
            self.set_cross_cursor()  # Artı işareti cursoru
            r, g, b = self.current_color
            rgb_text = f"rgb({r}, {g}, {b})"
            hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            copy_text = f"{rgb_text}\n{hex_color}"
            pyperclip.copy(copy_text)
            self.color_history.add_color(rgb_text, hex_color)
            self.update_history_display()
            self.show_copy_notification("RGB ve HEX")
            self.root.after(1000, self.set_main_cursor)  # 1 saniye sonra normal cursor
            
    def show_copy_notification(self, format_type):
        message = f"{format_type} renk kodu kopyalandı!"
        NotificationWindow(self.root, message)
        self.status_label.configure(text=message)
        self.root.after(2000, lambda: self.status_label.configure(text="Durum: Aktif"))
                
    def update_color_info(self, pixel):
        r, g, b = pixel
        hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
        
        self.rgb_label.configure(text=f"RGB: ({r}, {g}, {b})")
        self.hex_label.configure(text=f"HEX: {hex_color}")
        self.color_preview.configure(bg=hex_color)
        
    def quit_app(self):
        self.running = False
        self.cleanup_cursor_files()  # Cursor dosyalarını temizle
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.quit()
        
    def run(self):
        self.root.mainloop()

    def create_hotkey_row(self, parent, label_text, hotkey_type):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        
        ctk.CTkLabel(frame, text=label_text).pack(side=tk.LEFT, padx=PADDING)
        
        label = ctk.CTkLabel(frame, text=self.hotkeys[hotkey_type])
        label.pack(side=tk.LEFT, padx=PADDING)
        
        ctk.CTkButton(frame, text="Değiştir",
                     command=lambda: self.change_hotkey(hotkey_type)).pack(side=tk.RIGHT, padx=PADDING)
        
        setattr(self, f"{hotkey_type}_label", label)

    def set_cursor_icon(self):
        try:
            # Özel imleç yerine Tkinter'ın yerleşik imleçlerini kullanalım
            self.root.config(cursor="crosshair")  # Normal mod için artı şeklinde imleç
            self.is_cross_cursor = False
            
        except Exception as e:
            print(f"Cursor ayarlanırken hata oluştu: {e}")
            
    def set_main_cursor(self):
        try:
            self.root.config(cursor="crosshair")
            self.is_cross_cursor = False
        except Exception as e:
            print(f"Ana cursor ayarlanırken hata oluştu: {e}")
            
    def set_cross_cursor(self):
        try:
            self.root.config(cursor="tcross")  # Kopyalama modu için farklı bir artı imleç
            self.is_cross_cursor = True
        except Exception as e:
            print(f"Cross cursor ayarlanırken hata oluştu: {e}")
            
    def cleanup_cursor_files(self):
        pass  # Artık temizlenecek dosya yok

    def add_to_startup(self):
        try:
            # Kayıt defteri yolu
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Exe dosyasının tam yolu
            exe_path = os.path.abspath(sys.argv[0])
            if exe_path.endswith('.py'):
                exe_path = exe_path.replace('.py', '.exe')
            
            # Kayıt defterini aç
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, 
                                winreg.KEY_ALL_ACCESS)
            
            # Programı başlangıçta çalıştırılacaklar listesine ekle
            winreg.SetValueEx(key, "ColorPicker", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Başlangıca ekleme hatası: {e}")
            return False

if __name__ == "__main__":
    app = ColorPicker()
    app.run() 