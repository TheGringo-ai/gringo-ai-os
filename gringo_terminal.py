#!/usr/bin/env python3
"""
Enhanced Terminal Interface for GRINGO Personal OS
Provides full CLI integration within the Streamlit UI
"""

import streamlit as st
import subprocess
import os
import sys
import threading
import queue
import time
from typing import Dict, List, Any

class GringoTerminal:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.current_dir = workspace_root
        self.command_history = []
        self.environment = os.environ.copy()
        self.environment['GRINGO_HOME'] = os.path.dirname(os.path.abspath(__file__))
        
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute command and return structured result"""
        self.command_history.append(command)
        
        # Handle built-in commands
        if command.strip() == "clear":
            return {"success": True, "output": "", "clear": True}
        
        if command.startswith("cd "):
            return self._handle_cd(command)
        
        if command == "pwd":
            return {"success": True, "output": self.current_dir}
        
        if command == "history":
            return {"success": True, "output": "\n".join(self.command_history[-20:])}
        
        # Execute external commands
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.current_dir,
                env=self.environment,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "⏰ Command timed out (30s limit)"}
        except Exception as e:
            return {"success": False, "error": f"❌ Error: {str(e)}"}
    
    def _handle_cd(self, command: str) -> Dict[str, Any]:
        """Handle directory change command"""
        parts = command.split()
        if len(parts) == 1:
            # cd with no args goes to workspace root
            target = self.workspace_root
        else:
            target = parts[1]
            
        # Handle relative paths
        if not os.path.isabs(target):
            target = os.path.join(self.current_dir, target)
        
        # Normalize path
        target = os.path.normpath(target)
        
        if os.path.exists(target) and os.path.isdir(target):
            self.current_dir = target
            return {"success": True, "output": f"📁 {target}"}
        else:
            return {"success": False, "error": f"❌ Directory not found: {target}"}
    
    def get_prompt(self) -> str:
        """Get command prompt string"""
        rel_path = os.path.relpath(self.current_dir, self.workspace_root)
        if rel_path == ".":
            rel_path = "~"
        return f"🤖 gringo:{rel_path} $ "

class StreamlitTerminalUI:
    def __init__(self, terminal: GringoTerminal):
        self.terminal = terminal
        
    def render(self):
        """Render the terminal interface"""
        st.subheader("💻 GRINGO Terminal")
        
        # Terminal output area
        if 'terminal_output' not in st.session_state:
            st.session_state.terminal_output = ["🤖 GRINGO Personal OS Terminal", "Type 'help' for available commands", ""]
        
        if 'terminal_input' not in st.session_state:
            st.session_state.terminal_input = ""
        
        # Display terminal output
        terminal_content = "\n".join(st.session_state.terminal_output)
        st.code(terminal_content, language="bash")
        
        # Command input
        col1, col2 = st.columns([4, 1])
        
        with col1:
            command = st.text_input(
                "Command:",
                value="",
                placeholder=self.terminal.get_prompt(),
                key="command_input",
                label_visibility="collapsed"
            )
        
        with col2:
            execute_btn = st.button("Execute", type="primary")
        
        # Execute command
        if (execute_btn or command) and command.strip():
            self._execute_and_display(command.strip())
            # Clear input by rerunning
            st.rerun()
        
        # Quick command buttons
        st.markdown("**Quick Commands:**")
        quick_cols = st.columns(6)
        
        quick_commands = [
            ("📋 ls", "ls -la"),
            ("🏠 Home", "cd"),
            ("🤖 Agents", "gringo agents"),
            ("📊 Status", "gringo file summarize ."),
            ("🧹 Clean", "gringo duplicates ."),
            ("❓ Help", "gringo help")
        ]
        
        for i, (label, cmd) in enumerate(quick_commands):
            with quick_cols[i]:
                if st.button(label, key=f"quick_{i}"):
                    self._execute_and_display(cmd)
                    st.rerun()
    
    def _execute_and_display(self, command: str):
        """Execute command and update display"""
        # Add command to output
        prompt = self.terminal.get_prompt()
        st.session_state.terminal_output.append(f"{prompt}{command}")
        
        # Execute command
        result = self.terminal.execute_command(command)
        
        # Handle clear command
        if result.get("clear"):
            st.session_state.terminal_output = ["🤖 Terminal cleared"]
            return
        
        # Add result to output
        if result["success"]:
            if result.get("output"):
                # Split long output into lines
                output_lines = result["output"].strip().split('\n')
                st.session_state.terminal_output.extend(output_lines)
        else:
            error_msg = result.get("error", "Unknown error")
            st.session_state.terminal_output.append(f"❌ {error_msg}")
        
        # Add empty line
        st.session_state.terminal_output.append("")
        
        # Keep only last 100 lines
        if len(st.session_state.terminal_output) > 100:
            st.session_state.terminal_output = st.session_state.terminal_output[-100:]

def create_enhanced_terminal_interface():
    """Create and return terminal interface components"""
    
    # Initialize terminal if not exists
    if 'gringo_terminal' not in st.session_state:
        workspace_root = os.path.expanduser("~/gringo_workspace")
        os.makedirs(workspace_root, exist_ok=True)
        st.session_state.gringo_terminal = GringoTerminal(workspace_root)
    
    # Create UI
    terminal_ui = StreamlitTerminalUI(st.session_state.gringo_terminal)
    
    return terminal_ui
