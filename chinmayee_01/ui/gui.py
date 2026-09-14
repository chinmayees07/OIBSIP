"""
Graphical User Interface (GUI) Module
Modern Dark-themed Tkinter UI displaying conversation logs, dynamic status badges,
audio controls, and fallback text input for maximum accessibility.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import datetime
import config

logger = config.logger

# Color Palette (Modern Dark Theme)
BG_DARK = "#121826"
BG_CARD = "#1e293b"
BG_INPUT = "#0f172a"
ACCENT_PRIMARY = "#38bdf8"    # Sky Blue
ACCENT_HOVER = "#0284c7"
TEXT_WHITE = "#f8fafc"
TEXT_MUTED = "#94a3b8"
STATUS_IDLE = "#10b981"       # Emerald Green
STATUS_LISTEN = "#3b82f6"     # Blue
STATUS_PROCESS = "#f59e0b"    # Amber
STATUS_SPEAK = "#8b5cf6"      # Purple
STATUS_ERROR = "#ef4444"      # Red


class VoiceAssistantGUI:
    def __init__(self, on_command_callback=None, on_mic_request=None):
        """
        Initializes the desktop UI.
        :param on_command_callback: function(text_command: str) to execute a textual/manual command.
        :param on_mic_request: function() to trigger a single speech-to-text listening cycle.
        """
        self.on_command_callback = on_command_callback
        self.on_mic_request = on_mic_request

        self.root = tk.Tk()
        self.root.title(f"{config.ASSISTANT_NAME} — AI Voice Assistant")
        self.root.geometry("760x650")
        self.root.minsize(620, 520)
        self.root.configure(bg=BG_DARK)

        self._continuous_listening = tk.BooleanVar(value=False)
        self._is_busy = False

        self._build_ui()

    def _build_ui(self):
        # Main Header Frame
        header_frame = tk.Frame(self.root, bg=BG_CARD, padx=20, pady=15)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            header_frame,
            text=f"🎙️ {config.ASSISTANT_NAME} Voice Assistant",
            font=("Helvetica", 16, "bold"),
            fg=TEXT_WHITE,
            bg=BG_CARD
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Intelligent Desktop Voice Assistant & Productivity Companion",
            font=("Helvetica", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # Status Badge Indicator
        self.status_badge = tk.Label(
            header_frame,
            text="● SYSTEM READY",
            font=("Helvetica", 9, "bold"),
            fg=STATUS_IDLE,
            bg="#0f172a",
            padx=10,
            pady=4,
            relief=tk.FLAT
        )
        self.status_badge.place(relx=1.0, rely=0.5, anchor="e")

        # Chat / Conversation Log Area
        chat_container = tk.Frame(self.root, bg=BG_DARK, padx=20, pady=10)
        chat_container.pack(fill=tk.BOTH, expand=True)

        self.chat_log = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            bg=BG_CARD,
            fg=TEXT_WHITE,
            font=("Consolas", 10),
            padx=12,
            pady=12,
            relief=tk.FLAT,
            state=tk.DISABLED,
            insertbackground=TEXT_WHITE
        )
        self.chat_log.pack(fill=tk.BOTH, expand=True)

        # Configure custom tags for rich message formatting
        self.chat_log.tag_config("user_tag", foreground="#38bdf8", font=("Consolas", 10, "bold"))
        self.chat_log.tag_config("assistant_tag", foreground="#34d399", font=("Consolas", 10, "bold"))
        self.chat_log.tag_config("system_tag", foreground="#94a3b8", font=("Consolas", 9, "italic"))
        self.chat_log.tag_config("error_tag", foreground="#f87171", font=("Consolas", 10, "bold"))
        self.chat_log.tag_config("content_tag", foreground="#f8fafc", font=("Consolas", 10))

        # Quick Actions Shortcut Bar
        quick_frame = tk.Frame(self.root, bg=BG_DARK, padx=20, pady=4)
        quick_frame.pack(fill=tk.X)

        quick_buttons = [
            ("🕒 Time", "what time is it"),
            ("📅 Date", "what is today's date"),
            ("🌤️ Weather", "what's the weather"),
            ("📝 Read Notes", "read my notes"),
            ("⚡ System Status", "system status"),
            ("😂 Joke", "tell me a joke")
        ]

        for label_text, cmd_text in quick_buttons:
            btn = tk.Button(
                quick_frame,
                text=label_text,
                font=("Helvetica", 8),
                bg="#334155",
                fg=TEXT_WHITE,
                activebackground=ACCENT_PRIMARY,
                activeforeground=BG_DARK,
                relief=tk.FLAT,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda c=cmd_text: self._handle_quick_command(c)
            )
            btn.pack(side=tk.LEFT, padx=3)

        # Control Panel & Voice Button Frame
        control_frame = tk.Frame(self.root, bg=BG_CARD, padx=20, pady=15)
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Microphone Button
        self.mic_button = tk.Button(
            control_frame,
            text="🎙️  CLICK TO SPEAK",
            font=("Helvetica", 11, "bold"),
            bg=ACCENT_PRIMARY,
            fg="#0f172a",
            activebackground=ACCENT_HOVER,
            activeforeground=TEXT_WHITE,
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._on_mic_click
        )
        self.mic_button.pack(side=tk.LEFT, padx=(0, 15))

        # Text Command Fallback Input Field
        self.cmd_entry = tk.Entry(
            control_frame,
            bg=BG_INPUT,
            fg=TEXT_WHITE,
            font=("Helvetica", 11),
            insertbackground=TEXT_WHITE,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#334155",
            highlightcolor=ACCENT_PRIMARY
        )
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=6)
        self.cmd_entry.bind("<Return>", lambda event: self._send_manual_command())

        # Send Button
        send_button = tk.Button(
            control_frame,
            text="Send",
            font=("Helvetica", 10, "bold"),
            bg="#334155",
            fg=TEXT_WHITE,
            activebackground=ACCENT_PRIMARY,
            activeforeground="#0f172a",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._send_manual_command
        )
        send_button.pack(side=tk.LEFT, padx=(0, 10))

        # Clear Chat Button
        clear_button = tk.Button(
            control_frame,
            text="Clear",
            font=("Helvetica", 9),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            activebackground="#475569",
            activeforeground=TEXT_WHITE,
            relief=tk.FLAT,
            padx=8,
            pady=6,
            cursor="hand2",
            command=self.clear_chat
        )
        clear_button.pack(side=tk.RIGHT)

        # Initial Welcome Message
        self.log_system_message(f"Assistant initialized. Press 'Click to Speak' or type a command below.")

    def update_status(self, state: str):
        """Thread-safe UI status badge updater."""
        self.root.after(0, self._apply_status_update, state)

    def _apply_status_update(self, state: str):
        state_lower = state.lower()
        if state_lower == "listening":
            self.status_badge.config(text="🔵 LISTENING (Speak now...)", fg=STATUS_LISTEN)
            self.mic_button.config(bg=STATUS_LISTEN, text="🎙️ LISTENING...")
        elif state_lower == "processing":
            self.status_badge.config(text="🟡 PROCESSING INTENT...", fg=STATUS_PROCESS)
            self.mic_button.config(bg=STATUS_PROCESS, text="⏳ THINKING...")
        elif state_lower == "speaking":
            self.status_badge.config(text="🟣 SPEAKING RESPONSE...", fg=STATUS_SPEAK)
            self.mic_button.config(bg=STATUS_SPEAK, text="🔊 SPEAKING...")
        elif state_lower == "error":
            self.status_badge.config(text="🔴 ERROR / MIC OFFLINE", fg=STATUS_ERROR)
            self.mic_button.config(bg=STATUS_ERROR, text="⚠️ RETRY MIC")
        else:  # Idle
            self.status_badge.config(text="🟢 SYSTEM READY", fg=STATUS_IDLE)
            self.mic_button.config(bg=ACCENT_PRIMARY, text="🎙️ CLICK TO SPEAK")

    def log_user_message(self, text: str):
        """Appends user speech transcript to chat log."""
        self.root.after(0, self._append_message, f"You: ", "user_tag", f"{text}\n\n")

    def log_assistant_message(self, text: str):
        """Appends assistant response to chat log."""
        self.root.after(0, self._append_message, f"{config.ASSISTANT_NAME}: ", "assistant_tag", f"{text}\n\n")

    def log_system_message(self, text: str):
        """Appends system notification to chat log."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.root.after(0, self._append_message, f"[{timestamp}] [System] ", "system_tag", f"{text}\n\n")

    def _append_message(self, prefix: str, tag: str, content: str):
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, prefix, tag)
        self.chat_log.insert(tk.END, content, "content_tag")
        self.chat_log.see(tk.END)
        self.chat_log.config(state=tk.DISABLED)

    def clear_chat(self):
        """Clears the chat text area."""
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.delete(1.0, tk.END)
        self.chat_log.config(state=tk.DISABLED)
        self.log_system_message("Conversation cleared.")

    def _on_mic_click(self):
        """Triggers single voice recognition cycle."""
        if self.on_mic_request:
            threading.Thread(target=self.on_mic_request, daemon=True).start()

    def _send_manual_command(self):
        """Dispatches typed command from the text entry box."""
        text = self.cmd_entry.get().strip()
        if text:
            self.cmd_entry.delete(0, tk.END)
            self.log_user_message(text)
            if self.on_command_callback:
                threading.Thread(target=self.on_command_callback, args=(text,), daemon=True).start()

    def _handle_quick_command(self, cmd_text: str):
        """Dispatches quick action shortcut button command."""
        self.log_user_message(cmd_text)
        if self.on_command_callback:
            threading.Thread(target=self.on_command_callback, args=(cmd_text,), daemon=True).start()

    def run(self):
        """Starts the Tkinter main event loop."""
        self.root.mainloop()
