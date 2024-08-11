import tkinter as tk
from tkinter import filedialog, messagebox
import json
import time
from pynput import mouse, keyboard
import pygame
import pygetwindow as gw
import threading
from datetime import datetime

class KeyloggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger Application")
        self.recording = False
        self.data = []
        self.start_time = None
        self.devices = []
        self.joystick_name = None  # Pour stocker le nom du joystick
        self.selected_joystick = None  # Pour stocker la manette sélectionnée

        self.setup_ui()

        pygame.init()
        self.check_devices_thread = threading.Thread(target=self.check_devices)
        self.check_devices_thread.daemon = True
        self.check_devices_thread.start()

    def setup_ui(self):
        # Start/Stop button
        self.toggle_button = tk.Button(self.root, text="Start Recording", command=self.toggle_recording, bg="lightgreen")
        self.toggle_button.pack(pady=10)

        # Save file
        self.save_button = tk.Button(self.root, text="Save Recording", command=self.save_recording, state=tk.DISABLED)
        self.save_button.pack(pady=10)

        # Device selection in a LabelFrame
        self.device_frame = tk.LabelFrame(self.root, text="Select Devices")
        self.device_frame.pack(pady=20, padx=20, fill="x")

        self.device_listbox = tk.Listbox(self.device_frame, selectmode=tk.MULTIPLE)
        self.device_listbox.pack(pady=10, padx=10, fill="x")

        # Joystick selection in a LabelFrame
        self.joystick_frame = tk.LabelFrame(self.root, text="Select Joystick")
        self.joystick_frame.pack(pady=20, padx=20, fill="x")

        self.joystick_listbox = tk.Listbox(self.joystick_frame, selectmode=tk.SINGLE)
        self.joystick_listbox.pack(pady=10, padx=10, fill="x")

    def check_devices(self):
        while True:
            new_devices = []
            pygame.joystick.quit()
            pygame.joystick.init()

            new_devices.append("Keyboard")
            new_devices.append("Mouse")
            if pygame.joystick.get_count() > 0:
                new_devices.append("Joystick")
                self.update_joystick_list()

            if new_devices != self.devices:
                self.devices = new_devices
                self.update_devices()

            time.sleep(1)  # Vérifie les périphériques toutes les secondes

    def update_devices(self):
        self.device_listbox.delete(0, tk.END)
        for device in self.devices:
            self.device_listbox.insert(tk.END, device)

    def update_joystick_list(self):
        self.joystick_listbox.delete(0, tk.END)
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joystick_listbox.insert(tk.END, joystick.get_name())

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.devices_used = [self.device_listbox.get(i) for i in self.device_listbox.curselection()]
        selected_joystick_index = self.joystick_listbox.curselection()
        
        if not self.devices_used:
            messagebox.showwarning("No Device Selected", "Please select at least one device to record.")
            return
        
        if "Joystick" in self.devices_used and not selected_joystick_index:
            messagebox.showwarning("No Joystick Selected", "Please select a joystick to record.")
            return

        if "Joystick" in self.devices_used:
            self.selected_joystick = pygame.joystick.Joystick(selected_joystick_index[0])

        self.recording = True
        self.toggle_button.config(text="Stop Recording", bg="red")
        self.start_time = time.time()
        self.data = []

        self.mouse_listener = mouse.Listener(on_click=self.on_click) if "Mouse" in self.devices_used else None
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release) if "Keyboard" in self.devices_used else None
        self.joystick_listener = self.selected_joystick if self.selected_joystick else None

        if self.mouse_listener: self.mouse_listener.start()
        if self.keyboard_listener: self.keyboard_listener.start()
        if self.joystick_listener:
            self.joystick_name = self.selected_joystick.get_name()  # Enregistrement du nom du joystick
            self.record_joystick()
        
        self.save_button.config(state=tk.DISABLED)

    def stop_recording(self):
        self.recording = False
        if self.mouse_listener: self.mouse_listener.stop()
        if self.keyboard_listener: self.keyboard_listener.stop()

        self.toggle_button.config(text="Start Recording", bg="lightgreen")
        self.save_button.config(state=tk.NORMAL)

    def save_recording(self):
        if not self.data:
            messagebox.showwarning("Warning", "No data to save!")
            return

        # Demander à l'utilisateur de choisir un nom de fichier
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not filename:
            return
        
        if not filename.endswith(".json"):
            filename += ".json"

        try:
            # Calcul de la durée totale
            duration = time.time() - self.start_time
            
            # Données à sauvegarder
            data = {
                "recording_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "duration": f"{duration:.4f} seconds",
                "devices": self.devices_used,
                "joystick_name": self.joystick_name,  # Ajouter le nom du joystick
                "events": self.data
            }
            
            # Sauvegarde des données dans un fichier JSON
            with open(filename, "w") as file:
                json.dump(data, file, indent=4)
            
            messagebox.showinfo("Info", f"Recording saved as '{filename}'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save recording: {str(e)}")
        
        self.save_button.config(state=tk.DISABLED)

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
        if self.recording and self.joystick_listener:
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
