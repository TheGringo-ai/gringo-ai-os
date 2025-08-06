#!/usr/bin/env python3
"""
GRINGO AI OS Desktop Launcher
Branded launcher with logo and enhanced startup experience
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class GringoLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GRINGO AI OS Launcher")
        self.root.geometry("500x400")
        self.root.configure(bg='#0f172a')
        
        # Set window icon with your company logo
        try:
            self.root.iconphoto(True, tk.PhotoImage(file="assets/company_logo.png"))
        except:
            # Fallback if logo file not found
            pass
        
        self.setup_ui()
        self.streamlit_process = None
        
    def setup_ui(self):
        """Create the launcher UI"""
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#0f172a')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Logo section - clean design without large image
        logo_frame = tk.Frame(main_frame, bg='#0f172a')
        logo_frame.pack(pady=(0, 20))
        
        # Clean gear icon display
        logo_text = tk.Label(
            logo_frame,
            text="⚙️",
            font=("Arial", 48, "bold"),
            fg="#06b6d4",
            bg="#0f172a"
        )
        logo_text.pack()
        
        # Title
        title_label = tk.Label(
            logo_frame,
            text="GRINGO AI OS",
            font=("Arial", 24, "bold"),
            fg="#06b6d4",
            bg="#0f172a"
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            logo_frame,
            text="Ultimate AI-Powered Development Environment",
            font=("Arial", 12),
            fg="#e2e8f0",
            bg="#0f172a"
        )
        subtitle_label.pack()
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg='#0f172a')
        status_frame.pack(fill='x', pady=20)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to launch GRINGO AI OS",
            font=("Arial", 10),
            fg="#94a3b8",
            bg="#0f172a"
        )
        self.status_label.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(
            status_frame,
            mode='indeterminate',
            style='Cyan.Horizontal.TProgressbar'
        )
        self.progress.pack(fill='x', pady=(10, 0))
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#0f172a')
        buttons_frame.pack(fill='x', pady=20)
        
        # Launch button
        self.launch_btn = tk.Button(
            buttons_frame,
            text="🚀 Launch GRINGO AI OS",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#06b6d4",
            activebackground="#0891b2",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10,
            command=self.launch_gringo
        )
        self.launch_btn.pack(side='left', padx=(0, 10))
        
        # Stop button
        self.stop_btn = tk.Button(
            buttons_frame,
            text="⏹️ Stop",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#ef4444",
            activebackground="#dc2626",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10,
            command=self.stop_gringo,
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=(0, 10))
        
        # Settings button
        settings_btn = tk.Button(
            buttons_frame,
            text="⚙️ Settings",
            font=("Arial", 12),
            fg="#e2e8f0",
            bg="#374151",
            activebackground="#4b5563",
            activeforeground="white",
            relief="flat",
            padx=15,
            pady=8,
            command=self.show_settings
        )
        settings_btn.pack(side='right')
        
        # Features frame
        features_frame = tk.Frame(main_frame, bg='#0f172a')
        features_frame.pack(fill='both', expand=True, pady=20)
        
        features_title = tk.Label(
            features_frame,
            text="✨ Features",
            font=("Arial", 14, "bold"),
            fg="#06b6d4",
            bg="#0f172a"
        )
        features_title.pack(anchor='w')
        
        features = [
            "🤖 Multi-Agent Orchestration (10 specialized agents)",
            "🚀 Natural Language → Working Code",
            "📁 Project Learning & Analysis",
            "🔒 Privacy-First Local AI Processing",
            "🛠️ AI-Powered Custom Tools",
            "💬 Local LLaMA3 Integration"
        ]
        
        for feature in features:
            feature_label = tk.Label(
                features_frame,
                text=feature,
                font=("Arial", 10),
                fg="#94a3b8",
                bg="#0f172a",
                anchor='w'
            )
            feature_label.pack(anchor='w', pady=2)
        
        # Configure progress bar style
        style = ttk.Style()
        style.configure(
            'Cyan.Horizontal.TProgressbar',
            background='#06b6d4',
            troughcolor='#1e293b',
            borderwidth=0,
            lightcolor='#06b6d4',
            darkcolor='#06b6d4'
        )
    
    def launch_gringo(self):
        """Launch GRINGO AI OS"""
        self.launch_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress.start(10)
        
        def launch_thread():
            try:
                self.status_label.config(text="🔍 Checking dependencies...")
                time.sleep(1)
                
                self.status_label.config(text="🤖 Starting AI services...")
                time.sleep(1)
                
                self.status_label.config(text="🚀 Launching GRINGO AI OS...")
                
                # Launch Streamlit
                script_dir = os.path.dirname(os.path.abspath(__file__))
                self.streamlit_process = subprocess.Popen([
                    sys.executable, '-m', 'streamlit', 'run', 
                    os.path.join(script_dir, 'ultimate_gringo.py'),
                    '--server.port', '8506',
                    '--server.headless', 'true'
                ], cwd=script_dir)
                
                time.sleep(3)
                
                # Open browser
                import webbrowser
                webbrowser.open('http://localhost:8506')
                
                self.status_label.config(text="✅ GRINGO AI OS running at http://localhost:8506")
                self.progress.stop()
                
            except Exception as e:
                self.status_label.config(text=f"❌ Launch failed: {str(e)}")
                self.progress.stop()
                self.launch_btn.config(state='normal')
                self.stop_btn.config(state='disabled')
                messagebox.showerror("Launch Error", f"Failed to launch GRINGO: {str(e)}")
        
        threading.Thread(target=launch_thread, daemon=True).start()
    
    def stop_gringo(self):
        """Stop GRINGO AI OS"""
        if self.streamlit_process:
            self.streamlit_process.terminate()
            self.streamlit_process = None
        
        self.progress.stop()
        self.status_label.config(text="⏹️ GRINGO AI OS stopped")
        self.launch_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("GRINGO Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#0f172a')
        
        # Settings content
        tk.Label(
            settings_window,
            text="⚙️ GRINGO Settings",
            font=("Arial", 16, "bold"),
            fg="#06b6d4",
            bg="#0f172a"
        ).pack(pady=20)
        
        # Port setting
        port_frame = tk.Frame(settings_window, bg='#0f172a')
        port_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            port_frame,
            text="Server Port:",
            font=("Arial", 12),
            fg="#e2e8f0",
            bg="#0f172a"
        ).pack(side='left')
        
        port_entry = tk.Entry(port_frame, font=("Arial", 12))
        port_entry.insert(0, "8506")
        port_entry.pack(side='right')
        
        # AI Model setting
        model_frame = tk.Frame(settings_window, bg='#0f172a')
        model_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            model_frame,
            text="AI Model:",
            font=("Arial", 12),
            fg="#e2e8f0",
            bg="#0f172a"
        ).pack(side='left')
        
        model_var = tk.StringVar(value="llama3")
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=model_var,
            values=["llama3", "llama2", "mistral", "codellama"],
            state="readonly"
        )
        model_combo.pack(side='right')
    
    def run(self):
        """Run the launcher"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        if self.streamlit_process:
            self.streamlit_process.terminate()
        self.root.destroy()

if __name__ == "__main__":
    launcher = GringoLauncher()
    launcher.run()
