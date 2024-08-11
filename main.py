import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pynput import keyboard, mouse
import time

class KeyloggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger App")
        
        # Variables
        self.recording = False
        self.log = []
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Interface graphique
        self.create_widgets()
    
    def create_widgets(self):
        self.start_button = ttk.Button(self.root, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=10)
        
        self.stop_button = ttk.Button(self.root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=10)
        
        self.save_button = ttk.Button(self.root, text="Save Recording", command=self.save_recording, state=tk.DISABLED)
        self.save_button.pack(pady=10)
        
        self.device_frame = ttk.LabelFrame(self.root, text="Select Devices")
        self.device_frame.pack(pady=20, padx=20, fill="x")

        self.keyboard_var = tk.BooleanVar(value=True)
        self.mouse_var = tk.BooleanVar(value=True)

        self.keyboard_check = ttk.Checkbutton(self.device_frame, text="Keyboard", variable=self.keyboard_var)
        self.keyboard_check.pack(side="left", padx=10, pady=10)

        self.mouse_check = ttk.Checkbutton(self.device_frame, text="Mouse", variable=self.mouse_var)
        self.mouse_check.pack(side="left", padx=10, pady=10)

    def start_recording(self):
        self.recording = True
        self.start_time = time.time()
        self.log = []
        
        if self.keyboard_var.get():
            self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
            self.keyboard_listener.start()

        if self.mouse_var.get():
            self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move)
            self.mouse_listener.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)
        
    def stop_recording(self):
        self.recording = False
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)
    
    def save_recording(self):
        if not self.log:
            messagebox.showwarning("Warning", "No data to save!")
            return
        
        with open("recording.txt", "w") as file:
            for entry in self.log:
                file.write(f"{entry}\n")
        
        messagebox.showinfo("Info", "Recording saved as 'recording.txt'")
        self.save_button.config(state=tk.DISABLED)
    
    def on_key_press(self, key):
        if self.recording:
            duration = time.time() - self.start_time
            try:
                self.log.append(f"{duration:.4f}: Key pressed: {key.char}")
            except AttributeError:
                self.log.append(f"{duration:.4f}: Special Key pressed: {key}")
    
    def on_key_release(self, key):
        if self.recording:
            duration = time.time() - self.start_time
            try:
                self.log.append(f"{duration:.4f}: Key released: {key.char}")
            except AttributeError:
                self.log.append(f"{duration:.4f}: Special Key released: {key}")
    
    def on_click(self, x, y, button, pressed):
        if self.recording:
            duration = time.time() - self.start_time
            if pressed:
                self.log.append(f"{duration:.4f}: Mouse clicked at ({x}, {y}) with {button}")
            else:
                self.log.append(f"{duration:.4f}: Mouse released at ({x}, {y}) with {button}")
    
    def on_move(self, x, y):
        if self.recording:
            duration = time.time() - self.start_time
            self.log.append(f"{duration:.4f}: Mouse moved to ({x}, {y})")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = KeyloggerApp(root)
    root.mainloop()
