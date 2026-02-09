import sys
import os
import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QProcess, pyqtSignal, QTimer
from typing import Optional, List

from llm_manager import LLMManager

ASCII_VICTORS_LAB = """
 _   _ _____ _____ ___ ___ _   _   _   _ ____  
| | | |___  |___  |_ _/ __| | | | | | | |___ 
| |_| | / /| | / / | | (_ | |_| | | |_| | __) |
|  _  |/ /_| |/ /_|| |\___|\__, |  \__, |/ ____/
|_| |_/____|_|____|___|   |_|   |_|   |_|_____|
"""

FANGS_ANIMATION_FRAMES = [
    """
      .---.
     / \ / 
    |   V   |
     \     /
      `---'
    """,
    """
      .---.
     / \|/ 
    |   X   |
     \     /
      `---'
    """,
    """
      .---.
     / \_/ 
    |  / \  |
     \/   \/
      `---'
    """
]

LIGHTNING_ANIMATION_FRAMES = [
    """
       .
      .
     .
    """,
    """
       .
      .
     . 
        
    """,
    """
       .
      .
     . 
        
         
          
    """
]

class TerminalPanel(QWidget):
    closed_signal = pyqtSignal(QWidget)

    def __init__(self, parent=None, shell_command: str = None, llm_manager: Optional[LLMManager] = None):
        super().__init__(parent)
        self.shell_command = shell_command if shell_command else self._detect_shell()
        self.llm_manager = llm_manager
        self.process = QProcess(self)

        self._is_gemini_chat_active: bool = False
        self._current_gemini_chat_session_id: int = id(self) # Unique ID for this terminal's chat session

        self._build_ui()
        self._start_shell_process()
        
        QTimer.singleShot(100, self._post_shell_init) # Delay connecting signals and starting SarahGPT

    def _post_shell_init(self):
        # Connect signals now that initial output is consumed/discarded
        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.finished.connect(self._terminal_finished)

        # --- Auto-start SarahGPT (Gemini Chat) ---
        if self.llm_manager:
            default_model = "models/gemini-2.5-flash-lite"
            response_msg = self.llm_manager.start_gemini_chat(
                model_name=default_model,
                session_id=self._current_gemini_chat_session_id
            )
            # self.output.clear() # Clear the terminal before displaying SarahGPT auto-start messages
            if "Error" not in response_msg:
                self._is_gemini_chat_active = True
                # self.output.append(f"
<span style='color:#FF69B4;'>{response_msg}</span>") # Hidden as per user request
                # self.output.append(f"<span style='color:#FF69B4;'>SarahGPT is now active. Type your messages directly. Use '!gemini chat end' to stop.</span>
") # Hidden as per user request
                # Auto-send a "hello" message
                hello_response = self.llm_manager.send_gemini_chat_message(
                    prompt="hello",
                    session_id=self._current_gemini_chat_session_id
                )
                self.output.append(f"") # Add an empty line for spacing before the auto-response
                self.output.append(f"<span style='color:#FF69B4;'>SarahGPT Chat Response:</span>
{hello_response}
")
            else:
                self.output.append(f"
<span style='color:red;'>{response_msg}</span>
")
        else:
            self.output.append(f"
<span style='color:red;'>Error: LLM Manager not configured for auto-start.</span>
")

    def _detect_shell(self) -> str:
        if sys.platform == "win32":
            return "cmd.exe"
        else:
            return "bash"

    def _build_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("SarahGPT")
        self.title_label.setStyleSheet("font-weight: bold; color: #EEEEEE; margin-left: 5px;")
        control_layout.addWidget(self.title_label)
        
        control_layout.addStretch()

        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #CC3333;
                color: #EEEEEE;
                border: 1px solid #FF6666;
                border-radius: 10px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
        """)
        self.close_btn.clicked.connect(self._close_terminal)
        control_layout.addWidget(self.close_btn)
        
        self.layout.addLayout(control_layout)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: #1a1a1a; color: #00FF00; font-family: 'Consolas', 'Monospace'; font-size: 10pt; border: 1px solid #444444;")
        self.layout.addWidget(self.output)

        self.input = QLineEdit()
        self.input.setStyleSheet("background-color: #444444; color: #00FF00; font-family: 'Consolas', 'Monospace'; font-size: 10pt; border: 1px solid #777777;")
        self.input.returnPressed.connect(self._send_command)
        self.layout.addWidget(self.input)

    def _start_shell_process(self):
        # Start the process
        self.process.start(self.shell_command)

        # Give the process a moment to produce any initial output and then discard it
        # This is a bit of a hack, but QProcess can be tricky with initial output.
        self.process.waitForStarted(100) # Wait a bit for it to start
        if self.process.state() == QProcess.ProcessState.Running:
            # Read and discard any initial output
            self.process.readAllStandardOutput()
            self.process.readAllStandardError()

    def _send_command(self):
        command = self.input.text()
        self.output.append(f"> {command}")
        self.input.clear() # Clear input immediately

        # Clear terminal before starting any chat animation or response
        self.output.clear() 

        # Determine if it's an LLM command or shell command
        if len(command) > 0 and command.startswith('!'):
            parts = command.strip().split(maxsplit=2)
            llm_cmd = parts[0][1:].lower()

            if llm_cmd == "gemini":
                # Handle Gemini-specific commands: chat start/end
                if command.strip() == "!gemini chat start":
                    self._handle_gemini_chat_start_command()
                elif command.strip() == "!gemini chat end":
                    self._handle_gemini_chat_end_command()
                else:
                    # Regular Gemini call (single-turn or active chat message)
                    self._handle_gemini_command(command, parts)
            elif llm_cmd in ["ollama", "claude"]:
                # Handle other LLM commands without animation for now
                self._handle_other_llm_command(command, parts)
            else:
                # Not a recognized LLM command, send to shell
                self._handle_shell_command(command)
        elif self._is_gemini_chat_active:
            # If in active Gemini chat, send message to it
            self._handle_gemini_command(command, None) # Pass None for parts in chat mode
        else:
            # Not an LLM command, send to shell
            self._handle_shell_command(command)

    def _handle_gemini_chat_start_command(self):
        if self.llm_manager:
            default_model = "models/gemini-2.5-flash-lite"
            response_msg = self.llm_manager.start_gemini_chat(
                model_name=default_model,
                session_id=self._current_gemini_chat_session_id
            )
            # self.output.clear() # Already cleared at the beginning of _send_command
            if "Error" not in response_msg:
                self._is_gemini_chat_active = True
                self._display_ascii_animation(
                    FANGS_ANIMATION_FRAMES, 
                    on_finish=lambda: self._continue_gemini_chat_start_after_animation(response_msg)
                )
            else:
                self.output.append(f"<span style='color:red;'>{response_msg}</span>
")
        else:
            self.output.append(f"<span style='color:red;'>Error: LLM Manager not configured.</span>
")

    def _continue_gemini_chat_start_after_animation(self, response_msg):
        # Auto-send a "hello" message after animation and initial chat start
        hello_response = self.llm_manager.send_gemini_chat_message(
            prompt="hello",
            session_id=self._current_gemini_chat_session_id
        )
        self.output.append(f"
<span style='color:#FF69B4;'>SarahGPT Chat Response:</span>
{hello_response}
")

    def _handle_gemini_chat_end_command(self):
        if self.llm_manager:
            response_msg = self.llm_manager.end_gemini_chat(session_id=self._current_gemini_chat_session_id)
            self._is_gemini_chat_active = False
            self.output.append(f"
<span style='color:#FF69B4;'>{response_msg}</span>
") # Use pink for consistency
        else:
            self.output.append(f"<span style='color:red;'>Error: LLM Manager not configured.</span>
")

    def _handle_gemini_command(self, command: str, parts: Optional[List[str]]):
        # This handles both active chat messages and single-turn !gemini calls
        self._display_ascii_animation(
            FANGS_ANIMATION_FRAMES, 
            on_finish=lambda: self._continue_gemini_call_after_animation(command, parts)
        )

    def _continue_gemini_call_after_animation(self, command: str, parts: Optional[List[str]]):
        if not self.llm_manager:
            self.output.append(f"<span style='color:red;'>Error: LLM Manager not configured.</span>
")
            return

        if self._is_gemini_chat_active and parts is None: # Active chat message
            response = self.llm_manager.send_gemini_chat_message(
                prompt=command,
                session_id=self._current_gemini_chat_session_id
            )
            self._display_gemini_response(response, is_chat=True, original_command=command)
        else: # Single-turn !gemini call
            llm_type = "gemini"
            user_specified_model_name = None
            prompt = ""

            if parts and len(parts) > 1:
                potential_model_or_prompt_start = parts[1]
                if self.llm_manager.is_valid_gemini_model(potential_model_or_prompt_start):
                    user_specified_model_name = potential_model_or_prompt_start
                    if len(parts) > 2:
                        prompt = parts[2]
                    else:
                        prompt = ""
                else:
                    if len(parts) > 2:
                        prompt = potential_model_or_prompt_start + " " + parts[2]
                    else:
                        prompt = potential_model_or_prompt_start
            
            response = self.llm_manager.call_gemini(prompt, user_specified_model_name or "models/gemini-2.5-flash-lite")
            self._display_gemini_response(response, is_chat=False, original_command=command)

    def _display_gemini_response(self, response: str, is_chat: bool, original_command: str):
        if "Gemini failed" in response and self.llm_manager:
            # Trigger lightning animation for fallback, then display fallback message
            self._display_ascii_animation(
                LIGHTNING_ANIMATION_FRAMES, 
                on_finish=lambda: self._continue_ollama_fallback_after_animation(response)
            )
        else:
            response_prefix = "SarahGPT Chat Response:" if is_chat else "SarahGPT Response:"
            self.output.append(f"
<span style='color:#FF69B4;'>{response_prefix}</span>
{response}
")

    def _continue_ollama_fallback_after_animation(self, response: str):
        # Append ASCII art and descriptions after lightning animation
        self.output.append(f"
<span style='color:#FF69B4;'>{ASCII_VICTORS_LAB}</span>
") # ASCII art for fallback
        self.output.append(f"<span style='color:#FF69B4;'>{response}</span>
") # The full response from llm_manager now includes descriptions

    def _handle_other_llm_command(self, command: str, parts: List[str]):
        # This is for Ollama and Claude single-turn calls
        if not self.llm_manager:
            self.output.append(f"<span style='color:red;'>Error: LLM Manager not configured.</span>
")
            return

        llm_cmd = parts[0][1:].lower()
        llm_type = llm_cmd
        user_specified_model_name = None
        prompt = ""

        if len(parts) > 1:
            potential_model_or_prompt_start = parts[1]
            # Need specific logic here if Ollama/Claude also support model names in command
            # For simplicity, assuming second part is prompt if not Gemini model
            if len(parts) > 2:
                prompt = potential_model_or_prompt_start + " " + parts[2]
            else:
                prompt = potential_model_or_prompt_start
        
        self.output.append(f"<span style='color:#00FFFF;'>Calling {llm_type.capitalize()}...</span>
")
        response = "Error: Invalid LLM type or unhandled."
        try:
            if llm_type == "ollama":
                response = self.llm_manager.call_ollama(prompt, user_specified_model_name or "llama2")
            elif llm_type == "claude":
                response = self.llm_manager.call_claude(prompt, user_specified_model_name or "claude-3-opus-20240229")
        except Exception as e:
            response = f"Error calling {llm_type.capitalize()} API: {e}"
        
        self.output.append(f"
<span style='color:#FF69B4;'>{llm_type.capitalize()} Response:</span>
{response}
")

    def _handle_shell_command(self, command: str):
        self.process.write((command + "
").encode())

    def _read_stdout(self):
        data = self.process.readAllStandardOutput().data().decode().strip()
        if data:
            self.output.append(data)

    def _read_stderr(self):
        data = self.process.readAllStandardError().data().decode().strip()
        if data:
            self.output.append(f"<span style='color:red;'>{data}</span>")

    def _terminal_finished(self, exit_code, exit_status):
        self.output.append(f"
--- Terminal exited with code {exit_code} ---")
        self.input.setEnabled(False)
        self.process.close()
        
    def _close_terminal(self):
        self.process.terminate()
        self.process.waitForFinished(1000)
        self.process.kill()
        self.closed_signal.emit(self)

    def _display_ascii_animation(self, frames: List[str], delay_ms: int = 100, index: int = 0, on_finish=None, clear_output: bool = True):
        """Displays a sequence of ASCII art frames with delays."""
        # To disable animations, immediately call on_finish if it exists and return.
        if on_finish:
            on_finish()
        return