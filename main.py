import tkinter as tk
from tkinter import filedialog, messagebox
import json
import time
from pynput import mouse, keyboard
import pygame
import pygetwindow as gw

class KeyloggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger Application")
        self.recording = False
        self.data = []
        self.start_time = None

        self.setup_ui()

        pygame.init()
        self.update_devices()

    def setup_ui(self):
        # Start/Stop buttons
        self.start_button = tk.Button(self.root, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        # File naming
        self.file_label = tk.Label(self.root, text="Output File Name:")
        self.file_label.pack(pady=5)
        self.file_entry = tk.Entry(self.root)
        self.file_entry.pack(pady=5)

        # Device selection
        self.device_label = tk.Label(self.root, text="Select Devices:")
        self.device_label.pack(pady=5)

        self.device_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.device_listbox.pack(pady=10)

    def update_devices(self):
        self.device_listbox.delete(0, tk.END)
        self.device_listbox.insert(tk.END, "Keyboard")
        self.device_listbox.insert(tk.END, "Mouse")
        if pygame.joystick.get_count() > 0:
            self.device_listbox.insert(tk.END, "Joystick")

    def start_recording(self):
        selected_devices = [self.device_listbox.get(i) for i in self.device_listbox.curselection()]
        if not selected_devices:
            messagebox.showwarning("No Device Selected", "Please select at least one device to record.")
            return

        self.recording = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.start_time = time.time()
        self.data = []

        self.mouse_listener = mouse.Listener(on_click=self.on_click) if "Mouse" in selected_devices else None
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release) if "Keyboard" in selected_devices else None
        self.joystick_listener = pygame.joystick.Joystick(0) if "Joystick" in selected_devices and pygame.joystick.get_count() > 0 else None

        if self.mouse_listener: self.mouse_listener.start()
        if self.keyboard_listener: self.keyboard_listener.start()
        if self.joystick_listener: self.record_joystick()

    def stop_recording(self):
        self.recording = False
        if self.mouse_listener: self.mouse_listener.stop()
        if self.keyboard_listener: self.keyboard_listener.stop()

        output_file = self.file_entry.get() + ".json"
        if output_file:
            with open(output_file, 'w') as f:
                json.dump({
                    "start_time": self.start_time,
                    "duration": time.time() - self.start_time,
                    "events": self.data
                }, f, indent=4)

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        messagebox.showinfo("Recording Stopped", f"Data saved to {output_file}")

    def on_click(self, x, y, button, pressed):
        if self.recording:
            if gw.getActiveWindow().title != self.root.title():  # Ignore actions in the app's own window
                self.data.append({
                    "time": time.time() - self.start_time,
                    "event": "mouse_click",
                    "position": (x, y),
                    "button": str(button),
                    "pressed": pressed
                })

    def on_press(self, key):
        if self.recording:
            if gw.getActiveWindow().title != self.root.title():
                self.data.append({
                    "time": time.time() - self.start_time,
                    "event": "key_press",
                    "key": str(key)
                })

    def on_release(self, key):
        if self.recording:
            if gw.getActiveWindow().title != self.root.title():
                self.data.append({
                    "time": time.time() - self.start_time,
                    "event": "key_release",
                    "key": str(key)
                })

    def record_joystick(self):
        if self.recording:
            joystick = self.joystick_listener
            while self.recording:
                pygame.event.pump()
                axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
                buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
                self.data.append({
                    "time": time.time() - self.start_time,
                    "event": "joystick",
                    "axes": axes,
                    "buttons": buttons
                })
                time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyloggerApp(root)
    root.mainloop()
