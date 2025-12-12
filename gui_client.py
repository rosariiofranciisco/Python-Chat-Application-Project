import locale
locale.setlocale(locale.LC_NUMERIC, 'C')
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, Toplevel, filedialog
import socket
import threading
import time
from datetime import datetime
import re
import webbrowser
from PIL import Image, ImageTk, ImageOps
import os
import base64
import mimetypes
import hashlib
from pathlib import Path

class ModernChatClient:
    def __init__(self):
        self.host = 'localhost'
        self.port = 12345
        self.nickname = ""
        self.client_socket = None
        self.running = False
        self.connected = False
        self.online_users = []
        self.current_theme = 'light'
        self.received_files_dir = "received_files"
        
        # Create received files directory if it doesn't exist
        os.makedirs(self.received_files_dir, exist_ok=True)
        
        # File type icons
        self.file_icons = {
            'image': '🖼️',
            'pdf': '📄',
            'txt': '📝',
            'doc': '📋',
            'xls': '📊',
            'zip': '📦',
            'audio': '🎵',
            'video': '🎬',
            'default': '📎'
        }
        
        # Create modern window
        self.root = tk.Tk()
        self.root.title("PyChat • Modern Messaging")
        self.root.geometry("1000x700")
        self.root.configure(bg='#FFFFFF')
        self.root.minsize(700, 500)
        
        # Themes
        self.themes = {
            'light': {
                'primary': '#0084FF',
                'primary_light': '#E5F3FF',
                'background': '#FFFFFF',
                'sidebar_bg': '#F0F2F5',
                'message_sent': '#0084FF',
                'message_received': '#F0F0F0',
                'text_light': '#FFFFFF',
                'text_dark': '#000000',
                'text_gray': '#666666',
                'online_green': '#00D500',
                'border': '#DDDDDD',
                'hover': '#F8F9FA',
                'file_bg': '#E8F5E8',
                'file_text': '#1E7B1E'
            },
            'dark': {
                'primary': '#0084FF',
                'primary_light': '#1E2A3A',
                'background': '#0E141B',
                'sidebar_bg': '#1E2A3A',
                'message_sent': '#0084FF',
                'message_received': '#2D3A4D',
                'text_light': '#FFFFFF',
                'text_dark': '#E4E6EB',
                'text_gray': '#B0B3B8',
                'online_green': '#00D500',
                'border': '#2D3A4D',
                'hover': '#2A394E',
                'file_bg': '#1E3A1E',
                'file_text': '#90EE90'
            }
        }
        
        self.colors = self.themes['light']
        
        # Emoji picker data
        self.emoji_categories = {
            "😊 Smileys & People": ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🥸', '🤩', '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓', '🤗', '🤔', '🤭', '🤫', '🤥', '😶', '😐', '😑', '😬', '🙄', '😯', '😦', '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐', '🥴', '🤢', '🤮', '🤧', '😷', '🤒', '🤕', '🤑', '🤠'],
            "❤️ Hearts & Emotion": ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❤️‍🔥', '❤️‍🩹', '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟'],
            "👍 Gestures & Body": ['👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '👈', '👉', '👆', '👇', '☝️', '✋', '🤚', '🖐️', '🖖', '👋', '🤙', '💪', '🦵', '🦶', '👂', '👃', '🧠', '🦷', '🦴', '👀', '👁️', '👅', '👄'],
            "🐶 Animals & Nature": ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷', '🐸', '🐵', '🐔', '🐧', '🐦', '🐤', '🦆', '🦅', '🦉', '🦇', '🐺', '🐗', '🐴', '🦄', '🐝', '🐛', '🦋', '🐌', '🐞', '🐜', '🦟', '🦗', '🕷️'],
            "🎉 Celebration & Objects": ['🎉', '🎊', '🎈', '🎁', '🎂', '🍾', '🥳', '✨', '🌟', '💫', '⭐', '🔥', '💥', '🎇', '🎆', '📱', '💻', '⌚', '📷', '🎥', '📺', '📻', '🎙️', '🎚️', '🎛️', '📀', '💿', '📼', '📷', '🎞️', '🔍', '💡', '🔦', '🏮', '📔', '📕', '📖', '📗', '📘', '📙', '📚']
        }
        
        self.common_emojis = ['😊', '😂', '❤️', '😍', '🔥', '👍', '😎', '🎉', '👏', '🙏', '💯', '😢', '😡', '🤔', '👀']
        
        self.setup_modern_gui()
        
    def setup_modern_gui(self):
        """Setup modern social media-style interface"""
        # Main container with modern styling
        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar with online users
        self.setup_sidebar(main_container)
        
        # Main chat area
        self.setup_chat_area(main_container)
        
        main_container.add(self.sidebar_frame)
        main_container.add(self.chat_container)
        
        # Connection panel at bottom
        self.setup_connection_panel()
        
    def setup_sidebar(self, parent):
        """Setup the conversations sidebar"""
        self.sidebar_frame = tk.Frame(parent, bg=self.colors['sidebar_bg'], width=250)
        self.sidebar_frame.pack_propagate(False)
        
        # Sidebar header
        header_frame = tk.Frame(self.sidebar_frame, bg=self.colors['primary'], height=70)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # App title in header
        title_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        title_frame.pack(fill=tk.X, padx=15, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="💬 PyChat",
            font=('Segoe UI', 18, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['primary']
        )
        title_label.pack(side=tk.LEFT)
        
        # Theme toggle button
        self.theme_btn = tk.Label(
            title_frame,
            text="🌙",
            font=('Segoe UI', 12),
            fg=self.colors['text_light'],
            bg=self.colors['primary'],
            cursor="hand2",
            padx=5
        )
        self.theme_btn.pack(side=tk.RIGHT)
        self.theme_btn.bind("<Button-1>", lambda e: self.toggle_theme())
        
        # Search bar
        search_frame = tk.Frame(self.sidebar_frame, bg=self.colors['sidebar_bg'], height=50)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        search_frame.pack_propagate(False)
        
        self.search_entry = tk.Entry(
            search_frame,
            font=('Segoe UI', 10),
            bg=self.colors['background'],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=self.colors['primary']
        )
        self.search_entry.pack(fill=tk.X, padx=5, pady=10)
        self.search_entry.insert(0, "🔍 Search users...")
        self.search_entry.bind('<FocusIn>', self.clear_search_placeholder)
        self.search_entry.bind('<FocusOut>', self.restore_search_placeholder)
        self.search_entry.bind('<KeyRelease>', self.filter_users)
        
        # Online users section
        users_header = tk.Label(
            self.sidebar_frame,
            text="🟢 Online Users",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_dark'],
            bg=self.colors['sidebar_bg'],
            anchor='w',
            padx=15,
            pady=10
        )
        users_header.pack(fill=tk.X)
        
        # Online users list container
        self.users_container = tk.Frame(self.sidebar_frame, bg=self.colors['sidebar_bg'])
        self.users_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add default offline message
        self.add_user_item("No users online", "Connect to see users", False)
        
    def setup_chat_area(self, parent):
        """Setup the main chat area"""
        self.chat_container = tk.Frame(parent, bg=self.colors['background'])
        
        # Chat header (like WhatsApp chat header)
        self.chat_header = tk.Frame(self.chat_container, bg=self.colors['sidebar_bg'], height=70)
        self.chat_header.pack(fill=tk.X, padx=0, pady=0)
        self.chat_header.pack_propagate(False)
        
        # Chat info in header
        info_frame = tk.Frame(self.chat_header, bg=self.colors['sidebar_bg'])
        info_frame.pack(side=tk.LEFT, padx=20, pady=20)
        
        self.chat_title = tk.Label(
            info_frame,
            text="💬 General Chat",
            font=('Segoe UI', 16, 'bold'),
            fg=self.colors['text_dark'],
            bg=self.colors['sidebar_bg']
        )
        self.chat_title.pack(anchor='w')
        
        self.chat_status = tk.Label(
            info_frame,
            text="🔴 Offline - Click Connect to start chatting",
            font=('Segoe UI', 10),
            fg=self.colors['text_gray'],
            bg=self.colors['sidebar_bg']
        )
        self.chat_status.pack(anchor='w')
        
        # File upload button
        file_btn_frame = tk.Frame(self.chat_header, bg=self.colors['sidebar_bg'])
        file_btn_frame.pack(side=tk.RIGHT, padx=10, pady=20)
        
        self.file_upload_btn = tk.Label(
            file_btn_frame,
            text="📎",
            font=('Segoe UI', 14),
            fg=self.colors['text_dark'],
            bg=self.colors['sidebar_bg'],
            cursor="hand2",
            padx=10
        )
        self.file_upload_btn.pack()
        self.file_upload_btn.bind("<Button-1>", lambda e: self.upload_file())
        
        # Emoji picker button
        emoji_btn_frame = tk.Frame(self.chat_header, bg=self.colors['sidebar_bg'])
        emoji_btn_frame.pack(side=tk.RIGHT, padx=10, pady=20)
        
        self.emoji_picker_btn = tk.Label(
            emoji_btn_frame,
            text="😊",
            font=('Segoe UI', 14),
            fg=self.colors['text_dark'],
            bg=self.colors['sidebar_bg'],
            cursor="hand2",
            padx=10
        )
        self.emoji_picker_btn.pack()
        self.emoji_picker_btn.bind("<Button-1>", self.show_emoji_picker)
        
        # Messages area with modern scrollbar
        messages_container = tk.Frame(self.chat_container, bg=self.colors['background'])
        messages_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create a canvas and scrollbar for messages
        self.messages_canvas = tk.Canvas(
            messages_container,
            bg=self.colors['background'],
            highlightthickness=0
        )
        
        self.scrollbar = ttk.Scrollbar(messages_container, orient="vertical", command=self.messages_canvas.yview)
        self.messages_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollable_messages_frame = tk.Frame(self.messages_canvas, bg=self.colors['background'])
        self.scrollable_messages_frame.bind(
            "<Configure>",
            lambda e: self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))
        )
        
        self.canvas_window = self.messages_canvas.create_window((0, 0), window=self.scrollable_messages_frame, anchor="nw", width=self.messages_canvas.winfo_width())
        
        # Pack the canvas and scrollbar
        self.messages_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind the canvas resize event
        self.messages_canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind mouse wheel for scrolling
        self.messages_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Message input area
        self.input_frame = tk.Frame(self.chat_container, bg=self.colors['sidebar_bg'], height=120)
        self.input_frame.pack(fill=tk.X, padx=0, pady=0)
        self.input_frame.pack_propagate(False)
        
        # Formatting buttons row
        format_frame = tk.Frame(self.input_frame, bg=self.colors['sidebar_bg'], height=30)
        format_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Formatting buttons
        format_buttons = [
            ("B", "bold", "Bold"),
            ("I", "italic", "Italic"),
            ("U", "underline", "Underline"),
            ("@", "mention", "Mention user"),
            ("🔗", "link", "Insert link")
        ]
        
        for text, cmd, tooltip in format_buttons:
            btn = tk.Label(
                format_frame,
                text=text,
                font=('Segoe UI', 10, 'bold' if text == 'B' else 'normal'),
                fg=self.colors['text_dark'],
                bg=self.colors['sidebar_bg'],
                cursor="hand2",
                padx=5
            )
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind("<Button-1>", lambda e, c=cmd: self.apply_formatting(c))
        
        # Message input with modern styling
        input_container = tk.Frame(self.input_frame, bg=self.colors['sidebar_bg'])
        input_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # Create a frame for the input field and button
        input_field_frame = tk.Frame(input_container, bg=self.colors['background'])
        input_field_frame.pack(fill=tk.BOTH, expand=True)
        
        self.message_entry = tk.Text(
            input_field_frame,
            font=('Segoe UI', 12),
            bg=self.colors['background'],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=self.colors['primary'],
            highlightbackground=self.colors['border'],
            height=2,
            wrap=tk.WORD
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=5)
        self.message_entry.bind('<Return>', self.on_enter_pressed)
        self.message_entry.bind('<KeyRelease>', self.on_message_change)
        
        # Send button with modern style
        self.send_button = tk.Button(
            input_field_frame,
            text="➤",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_light'],
            bg="#1086CF",
            width=3,
            cursor="hand2",
            relief=tk.FLAT,
            borderwidth=0,
            command=self.send_message,
            state=tk.DISABLED
        )
        self.send_button.pack(side=tk.RIGHT, padx=(0, 0), pady=5, ipadx=5, ipady=5)
        
        # Character counter
        self.char_counter = tk.Label(
            self.input_frame,
            text="0/500",
            font=('Segoe UI', 9),
            fg=self.colors['text_gray'],
            bg=self.colors['sidebar_bg']
        )
        self.char_counter.pack(side=tk.RIGHT, padx=(0, 25), pady=(0, 10))
        
        # Disable initially
        self.message_entry.config(state=tk.DISABLED)
        
    def setup_connection_panel(self):
        """Setup connection status panel"""
        self.connection_frame = tk.Frame(self.root, bg=self.colors['sidebar_bg'], height=40)
        self.connection_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.connection_frame.pack_propagate(False)
        
        self.connection_status = tk.Label(
            self.connection_frame,
            text="🔴 Disconnected",
            font=('Segoe UI', 10),
            fg='#FF4444',
            bg=self.colors['sidebar_bg']
        )
        self.connection_status.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.connect_btn = tk.Label(
            self.connection_frame,
            text="Connect",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['primary'],
            cursor="hand2",
            padx=20,
            pady=5,
            relief=tk.FLAT
        )
        self.connect_btn.pack(side=tk.RIGHT, padx=20, pady=5)
        self.connect_btn.bind("<Button-1>", lambda e: self.toggle_connection())
        
    # ========== FILE SHARING FEATURES ==========
    def upload_file(self):
        """Open file dialog to select file for upload"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the server first.")
            return
            
        file_path = filedialog.askopenfilename(
            title="Select a file to send",
            filetypes=[
                ("All files", "*.*"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Documents", "*.pdf *.doc *.docx *.txt"),
                ("Archives", "*.zip *.rar *.7z")
            ]
        )
        
        if file_path:
            # Show progress dialog
            progress = Toplevel(self.root)
            progress.title("Uploading File")
            progress.geometry("300x100")
            progress.resizable(False, False)
            progress.transient(self.root)
            progress.grab_set()
            
            progress_label = tk.Label(progress, text=f"Preparing to send: {os.path.basename(file_path)}", pady=10)
            progress_label.pack()
            
            progress_bar = ttk.Progressbar(progress, mode='indeterminate')
            progress_bar.pack(pady=10)
            progress_bar.start()
            
            # Process file in separate thread to avoid freezing GUI
            def process_file():
                try:
                    file_size = os.path.getsize(file_path)
                    
                    # Check file size (10MB limit)
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        self.root.after(0, lambda: messagebox.showerror("File Too Large", "File size exceeds 10MB limit."))
                        return
                    
                    # Read and encode file
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    # Convert to base64 for safe transmission
                    encoded_content = base64.b64encode(file_content).decode('utf-8')
                    
                    # Get file info
                    file_name = os.path.basename(file_path)
                    file_extension = os.path.splitext(file_name)[1].lower().replace('.', '')
                    
                    # Send file to server
                    file_message = f"FILE:{file_name}:{file_extension}:{encoded_content}"
                    
                    if self.connected and self.client_socket:
                        self.client_socket.send(file_message.encode('utf-8'))
                        
                        # Show success message
                        self.root.after(0, lambda: self.add_message_bubble(
                            f"📎 Sent file: {file_name} ({self.format_file_size(file_size)})",
                            is_sent=True,
                            sender=""
                        ))
                        
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Upload Error", f"Failed to send file: {str(e)}"))
                finally:
                    self.root.after(0, progress.destroy)
            
            # Start file processing in separate thread
            threading.Thread(target=process_file, daemon=True).start()
    
    def format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_file_icon(self, file_extension):
        """Get appropriate emoji icon for file type"""
        file_type = file_extension.lower()
        
        if file_type in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']:
            return self.file_icons['image']
        elif file_type in ['pdf']:
            return self.file_icons['pdf']
        elif file_type in ['txt', 'log', 'md']:
            return self.file_icons['txt']
        elif file_type in ['doc', 'docx', 'odt']:
            return self.file_icons['doc']
        elif file_type in ['xls', 'xlsx', 'csv']:
            return self.file_icons['xls']
        elif file_type in ['zip', 'rar', '7z', 'tar', 'gz']:
            return self.file_icons['zip']
        elif file_type in ['mp3', 'wav', 'ogg', 'flac']:
            return self.file_icons['audio']
        elif file_type in ['mp4', 'avi', 'mkv', 'mov']:
            return self.file_icons['video']
        else:
            return self.file_icons['default']
    
    def add_file_message(self, file_name, file_extension, file_content_base64, sender="", is_sent=False):
        """Add file message to chat"""
        # Decode file content
        try:
            file_content = base64.b64decode(file_content_base64)
        except:
            self.add_message_bubble(f"❌ Failed to decode file: {file_name}", is_sent=False, sender="System")
            return
        
        # Save file locally
        safe_filename = self.make_filename_safe(file_name)
        save_path = os.path.join(self.received_files_dir, safe_filename)
        
        # Handle duplicate filenames
        counter = 1
        while os.path.exists(save_path):
            name, ext = os.path.splitext(safe_filename)
            save_path = os.path.join(self.received_files_dir, f"{name}_{counter}{ext}")
            counter += 1
        
        try:
            with open(save_path, 'wb') as f:
                f.write(file_content)
            
            file_size = len(file_content)
            file_icon = self.get_file_icon(file_extension)
            
            # Create file message frame
            message_frame = tk.Frame(self.scrollable_messages_frame, bg=self.colors['background'])
            message_frame.pack(fill=tk.X, padx=20, pady=3)
            
            # Align based on sender
            if is_sent:
                anchor = 'e'
                padx = (150, 20)
                bubble_frame = tk.Frame(message_frame, bg=self.colors['background'])
                bubble_frame.pack(anchor='e', fill=tk.X)
            else:
                anchor = 'w'
                padx = (20, 150)
                bubble_frame = tk.Frame(message_frame, bg=self.colors['background'])
                bubble_frame.pack(anchor='w', fill=tk.X)
            
            # Show sender name for received messages
            if sender and not is_sent:
                sender_label = tk.Label(
                    bubble_frame,
                    text=sender,
                    font=('Segoe UI', 10, 'bold'),
                    fg=self.colors['text_gray'],
                    bg=self.colors['background'],
                    anchor=anchor
                )
                sender_label.pack(anchor=anchor, padx=padx)
            
            # File message bubble
            file_bubble = tk.Frame(
                bubble_frame,
                bg=self.colors['file_bg'],
                relief=tk.FLAT
            )
            file_bubble.pack(anchor=anchor, padx=padx)
            
            # File icon and info
            inner_frame = tk.Frame(file_bubble, bg=self.colors['file_bg'])
            inner_frame.pack(padx=15, pady=10)
            
            # File icon
            icon_label = tk.Label(
                inner_frame,
                text=file_icon,
                font=('Segoe UI', 24),
                bg=self.colors['file_bg'],
                fg=self.colors['file_text']
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # File info
            info_frame = tk.Frame(inner_frame, bg=self.colors['file_bg'])
            info_frame.pack(side=tk.LEFT)
            
            file_name_label = tk.Label(
                info_frame,
                text=file_name,
                font=('Segoe UI', 11, 'bold'),
                bg=self.colors['file_bg'],
                fg=self.colors['file_text'],
                anchor='w'
            )
            file_name_label.pack(fill=tk.X)
            
            size_label = tk.Label(
                info_frame,
                text=self.format_file_size(file_size),
                font=('Segoe UI', 9),
                bg=self.colors['file_bg'],
                fg=self.colors['file_text'],
                anchor='w'
            )
            size_label.pack(fill=tk.X)
            
            # Download button
            def open_file():
                try:
                    os.startfile(save_path)
                except:
                    # For non-Windows systems or if startfile fails
                    try:
                        import subprocess
                        if os.name == 'nt':  # Windows
                            os.startfile(save_path)
                        elif os.name == 'posix':  # Linux, macOS
                            subprocess.run(['xdg-open', save_path], check=False)
                    except:
                        messagebox.showinfo("File Saved", f"File saved to:\n{save_path}")
            
            # Make the entire bubble clickable
            file_bubble.bind("<Button-1>", lambda e: open_file())
            for child in file_bubble.winfo_children():
                child.bind("<Button-1>", lambda e: open_file())
            
            # Add cursor to indicate clickable
            file_bubble.config(cursor="hand2")
            for child in file_bubble.winfo_children():
                if isinstance(child, tk.Frame):
                    for subchild in child.winfo_children():
                        subchild.config(cursor="hand2")
            
            # Time stamp
            timestamp = datetime.now().strftime("%H:%M")
            time_label = tk.Label(
                bubble_frame,
                text=timestamp,
                font=('Segoe UI', 9),
                fg=self.colors['text_gray'],
                bg=self.colors['background']
            )
            time_label.pack(anchor=anchor, padx=padx)
            
            # Auto-scroll to bottom
            self.messages_canvas.update_idletasks()
            self.messages_canvas.yview_moveto(1.0)
            
        except Exception as e:
            self.add_message_bubble(f"❌ Failed to save file: {file_name}", is_sent=False, sender="System")
    
    def make_filename_safe(self, filename):
        """Remove invalid characters from filename"""
        # Replace invalid characters with underscore
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    # ========== ENHANCED MESSAGE FORMATTING ==========
    def format_message_text(self, text, is_html=False):
        """Apply formatting to message text"""
        if is_html:
            # For HTML display in labels
            formatted = text
            
            # Bold: *text* -> <b>text</b>
            formatted = re.sub(r'\*([^\*]+)\*', r'<b>\1</b>', formatted)
            
            # Italic: _text_ -> <i>text</i>
            formatted = re.sub(r'_([^_]+)_', r'<i>\1</i>', formatted)
            
            # Underline: ~text~ -> <u>text</u>
            formatted = re.sub(r'~([^~]+)~', r'<u>\1</u>', formatted)
            
            # Code: `text` -> <code>text</code>
            formatted = re.sub(r'`([^`]+)`', r'<code>\1</code>', formatted)
            
            # Mentions: @username -> styled mention
            formatted = re.sub(r'@(\w+)', r'<span foreground="#0084FF"><b>@\1</b></span>', formatted)
            
            # URLs - make clickable
            url_pattern = r'(https?://[^\s]+)'
            formatted = re.sub(url_pattern, r'<a href="\1">\1</a>', formatted)
            
            return formatted
        else:
            # For plain text
            return text
    
    def apply_formatting(self, format_type):
        """Apply formatting to selected text"""
        if self.message_entry['state'] == 'disabled':
            return
            
        try:
            # Get selected text indices
            sel_start = self.message_entry.index(tk.SEL_FIRST)
            sel_end = self.message_entry.index(tk.SEL_LAST)
            selected_text = self.message_entry.get(sel_start, sel_end)
            
            # Apply formatting based on type
            formats = {
                'bold': ('*', '*'),
                'italic': ('_', '_'),
                'underline': ('~', '~'),
                'mention': ('@', ''),
                'link': ('', '')  # Special handling
            }
            
            if format_type == 'link':
                url = simpledialog.askstring("Insert Link", "Enter URL:", parent=self.root)
                if url:
                    formatted_text = f"[link]({url})"
            elif format_type in formats:
                start, end = formats[format_type]
                formatted_text = f"{start}{selected_text}{end}"
            else:
                return
                
            # Replace selected text with formatted text
            self.message_entry.delete(sel_start, sel_end)
            self.message_entry.insert(sel_start, formatted_text)
            
        except tk.TclError:
            # No text selected, insert formatting markers at cursor
            cursor_pos = self.message_entry.index(tk.INSERT)
            if format_type == 'mention':
                # Get username from dialog
                username = simpledialog.askstring("Mention User", "Enter username:", parent=self.root)
                if username:
                    self.message_entry.insert(cursor_pos, f"@{username} ")
            elif format_type == 'link':
                url = simpledialog.askstring("Insert Link", "Enter URL:", parent=self.root)
                if url:
                    self.message_entry.insert(cursor_pos, f"[link]({url})")
            else:
                markers = formats.get(format_type, ('', ''))
                self.message_entry.insert(cursor_pos, f"{markers[0]}{markers[1]}")
                # Move cursor between markers
                self.message_entry.mark_set(tk.INSERT, f"{cursor_pos}+{len(markers[0])}c")
    
    # ========== ONLINE USERS LIST ==========
    def add_user_item(self, username, status, is_online=True):
        """Add a user item to sidebar"""
        user_frame = tk.Frame(self.users_container, bg=self.colors['sidebar_bg'], height=60)
        user_frame.pack(fill=tk.X, padx=5, pady=2)
        user_frame.pack_propagate(False)
        
        # Avatar with online indicator
        avatar_frame = tk.Frame(user_frame, bg=self.colors['sidebar_bg'])
        avatar_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        avatar = tk.Label(
            avatar_frame,
            text=username[0].upper() if username else "?",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['primary'],
            width=3,
            height=1,
            relief=tk.FLAT
        )
        avatar.pack()
        
        # Online indicator
        if is_online:
            indicator = tk.Label(
                avatar_frame,
                text="●",
                font=('Segoe UI', 8),
                fg=self.colors['online_green'],
                bg=self.colors['sidebar_bg']
            )
            indicator.place(relx=0.7, rely=0.7)
        
        # User info
        info_frame = tk.Frame(user_frame, bg=self.colors['sidebar_bg'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        name_label = tk.Label(
            info_frame,
            text=username,
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_dark'],
            bg=self.colors['sidebar_bg'],
            anchor='w'
        )
        name_label.pack(fill=tk.X)
        
        status_label = tk.Label(
            info_frame,
            text=status,
            font=('Segoe UI', 9),
            fg=self.colors['text_gray'],
            bg=self.colors['sidebar_bg'],
            anchor='w'
        )
        status_label.pack(fill=tk.X)
        
        # Make clickable for mentions
        def make_mention():
            if self.message_entry['state'] == 'normal':
                self.message_entry.insert(tk.END, f"@{username} ")
                self.message_entry.focus()
        
        user_frame.bind("<Button-1>", lambda e: make_mention())
        for child in user_frame.winfo_children():
            child.bind("<Button-1>", lambda e: make_mention())
        
        return user_frame
    
    def update_online_users(self, users_list):
        """Update the online users list"""
        # Clear current users
        for widget in self.users_container.winfo_children():
            widget.destroy()
        
        # Add current user first
        if self.nickname:
            self.add_user_item(self.nickname, "You", True)
        
        # Add other users
        for user in users_list:
            if user != self.nickname:
                self.add_user_item(user, "Online", True)
        
        # Show message if no other users
        if len(users_list) <= 1:
            self.add_user_item("No other users online", "Waiting for others to connect...", False)

    def filter_users(self, event):
        """Filter users based on search text"""
        search_text = self.search_entry.get().lower()
        
        # Check if it's placeholder text
        if search_text == "🔍 search users...":
            return
        
        # Clear current user display
        for widget in self.users_container.winfo_children():
            widget.destroy()
        
        # If search is empty, show all users
        if not search_text.strip():
            self.update_online_users(self.online_users)
            return
        
        # Filter users based on search text
        filtered_users = []
        for user in self.online_users:
            if search_text in user.lower():
                filtered_users.append(user)
        
        # Check if we're connected and have a nickname
        is_connected = self.connected and self.nickname
        
        # Add current user first if connected
        if is_connected and search_text in self.nickname.lower():
            self.add_user_item(self.nickname, "You", True)
        
        # Add filtered users
        user_added = False
        for user in filtered_users:
            if is_connected and user == self.nickname:
                continue  # Already added
            self.add_user_item(user, "Online", True)
            user_added = True
        
        # Show "no results" message if no matches found
        if not user_added:
            if is_connected and search_text in self.nickname.lower():
                # Only current user matches
                self.add_user_item("No other users match your search", "Try different keywords", False)
            else:
                # No matches at all
                self.add_user_item(f"No users matching '{search_text}'", "Try different keywords", False)
    
    # ========== EMOJI PICKER ==========
    def show_emoji_picker(self, event):
        """Show emoji picker popup"""
        if not hasattr(self, 'emoji_picker') or not self.emoji_picker.winfo_exists():
            self.emoji_picker = Toplevel(self.root)
            self.emoji_picker.title("Emoji Picker")
            self.emoji_picker.geometry("400x500")
            self.emoji_picker.configure(bg=self.colors['background'])
            self.emoji_picker.resizable(False, False)
            
            # Make it transient
            self.emoji_picker.transient(self.root)
            
            # Category tabs
            notebook = ttk.Notebook(self.emoji_picker)
            notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            for category, emojis in self.emoji_categories.items():
                category_frame = tk.Frame(notebook, bg=self.colors['background'])
                notebook.add(category_frame, text=category)
                
                # Create emoji grid
                self.create_emoji_grid(category_frame, emojis)
    
    def create_emoji_grid(self, parent, emojis):
        """Create a grid of emoji buttons"""
        row, col = 0, 0
        for emoji in emojis:
            btn = tk.Label(
                parent,
                text=emoji,
                font=('Segoe UI', 16),
                bg=self.colors['background'],
                cursor="hand2",
                padx=5,
                pady=5
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            btn.bind("<Button-1>", lambda e, em=emoji: self.insert_emoji(em))
            
            col += 1
            if col > 7:  # 8 emojis per row
                col = 0
                row += 1
    
    def insert_emoji(self, emoji):
        """Insert emoji at cursor position"""
        if self.message_entry['state'] == 'normal':
            self.message_entry.insert(tk.INSERT, emoji)
            self.message_entry.focus()
            if hasattr(self, 'emoji_picker'):
                self.emoji_picker.destroy()
    
    # ========== THEME SWITCHING ==========
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.colors = self.themes[self.current_theme]
        self.theme_btn.config(text="☀️" if self.current_theme == 'dark' else "🌙")
        self.apply_theme()
    
    def apply_theme(self):
        """Apply current theme to all widgets"""
        # Update root
        self.root.configure(bg=self.colors['background'])
        
        # Update all frames and widgets
        self.update_widget_colors(self.root)
        
        # Update message display
        self.messages_canvas.configure(bg=self.colors['background'])
        self.scrollable_messages_frame.configure(bg=self.colors['background'])
        
        # Force redraw
        self.root.update_idletasks()
    
    def update_widget_colors(self, widget):
        """Recursively update widget colors"""
        try:
            if isinstance(widget, tk.Frame) or isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                # Update background
                if 'background' in widget.keys() or 'bg' in widget.keys():
                    current_bg = widget.cget('bg') if 'bg' in widget.keys() else widget.cget('background')
                    
                    # Map old colors to new
                    color_map = {
                        '#FFFFFF': self.colors['background'],
                        '#F0F2F5': self.colors['sidebar_bg'],
                        '#F0F0F0': self.colors['message_received'],
                        '#E5F3FF': self.colors['primary_light'],
                        '#000000': self.colors['text_dark'],
                        '#666666': self.colors['text_gray'],
                        '#E8F5E8': self.colors['file_bg']
                    }
                    
                    if current_bg in color_map:
                        widget.configure(bg=color_map[current_bg])
                    
                    # Update foreground
                    if 'foreground' in widget.keys() or 'fg' in widget.keys():
                        current_fg = widget.cget('fg') if 'fg' in widget.keys() else widget.cget('foreground')
                        if current_fg in color_map:
                            widget.configure(fg=color_map[current_fg])
            
            # Recursively update children
            for child in widget.winfo_children():
                self.update_widget_colors(child)
                
        except tk.TclError:
            pass
    
    # ========== ENHANCED MESSAGE DISPLAY ==========
    def add_message_bubble(self, message, is_sent=False, sender="", timestamp=""):
        """Add a modern message bubble with formatting support"""
        if not timestamp:
            timestamp = datetime.now().strftime("%H:%M")
            
        message_frame = tk.Frame(self.scrollable_messages_frame, bg=self.colors['background'])
        message_frame.pack(fill=tk.X, padx=20, pady=3)
        
        # Align messages to right if sent, left if received
        if is_sent:
            bubble_bg = self.colors['message_sent']
            text_color = self.colors['text_light']
            anchor = 'e'
            padx = (150, 20)
            bubble_frame = tk.Frame(message_frame, bg=self.colors['background'])
            bubble_frame.pack(anchor='e', fill=tk.X)
        else:
            bubble_bg = self.colors['message_received']
            text_color = self.colors['text_dark']
            anchor = 'w'
            padx = (20, 150)
            bubble_frame = tk.Frame(message_frame, bg=self.colors['background'])
            bubble_frame.pack(anchor='w', fill=tk.X)
        
        # Show sender name for received messages (not our own)
        if sender and not is_sent:
            sender_label = tk.Label(
                bubble_frame,
                text=sender,
                font=('Segoe UI', 10, 'bold'),
                fg=self.colors['text_gray'],
                bg=self.colors['background'],
                anchor=anchor
            )
            sender_label.pack(anchor=anchor, padx=padx)
        
        # Create bubble with formatted text
        bubble = tk.Label(
            bubble_frame,
            text=message,
            font=('Segoe UI', 11),
            fg=text_color,
            bg=bubble_bg,
            wraplength=350,
            justify=tk.LEFT,
            padx=15,
            pady=10,
            relief=tk.FLAT
        )
        bubble.pack(anchor=anchor, padx=padx)
        
        # Apply formatting (handles URLs, mentions, etc.)
        formatted_text = self.format_message_text(message, is_html=True)
        
        # Configure tags for clickable URLs
        bubble.bind("<Button-1>", lambda e, txt=message: self.handle_message_click(txt))
        
        # Time stamp
        time_label = tk.Label(
            bubble_frame,
            text=timestamp,
            font=('Segoe UI', 9),
            fg=self.colors['text_gray'],
            bg=self.colors['background']
        )
        time_label.pack(anchor=anchor, padx=padx)
        
        # Auto-scroll to bottom
        self.messages_canvas.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
    
    def handle_message_click(self, text):
        """Handle clicks on messages (for URLs)"""
        # Find URLs in text
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        
        if urls:
            # Open first URL
            webbrowser.open(urls[0])
    
    # ========== UTILITY METHODS ==========
    def clear_search_placeholder(self, event):
        """Clear search placeholder text"""
        if self.search_entry.get() == "🔍 Search users...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.colors['text_dark'])
            
    def restore_search_placeholder(self, event):
        """Restore search placeholder if empty"""
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "🔍 Search users...")
            self.search_entry.config(fg=self.colors['text_gray'])
            
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        self.messages_canvas.itemconfig(self.canvas_window, width=event.width)
        
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.messages_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_enter_pressed(self, event):
        """Handle Enter key in message entry"""
        # Check if Shift is pressed for new line
        if event.state & 0x1:  # Shift key
            self.message_entry.insert(tk.INSERT, "\n")
            return "break"
        else:
            self.send_message()
            return "break"
    
    def on_message_change(self, event):
        """Handle message text changes"""
        text = self.message_entry.get("1.0", tk.END).strip()
        char_count = len(text)
        
        # Update character counter
        self.char_counter.config(
            text=f"{char_count}/500",
            fg="#FF4444" if char_count > 500 else self.colors['text_gray']
        )
        
        # Enable/disable send button based on connection and message length
        if char_count > 0 and char_count <= 500 and self.connected:
            self.send_button.config(state=tk.NORMAL, bg=self.colors['primary'])
        else:
            self.send_button.config(state=tk.DISABLED, bg='#CCCCCC')
    
    # ========== NETWORK METHODS ==========
    def toggle_connection(self):
        """Connect or disconnect from server"""
        if not self.connected:
            self.connect_to_server()
        else:
            self.disconnect_from_server()
            
    def connect_to_server(self):
        """Connect to chat server"""
        try:
            # Get nickname with modern dialog
            self.nickname = simpledialog.askstring(
                "Welcome to PyChat", 
                "Enter your display name:",
                parent=self.root,
                initialvalue=f"User{time.time() % 1000:.0f}"
            )
            
            if not self.nickname:
                return
                
            # Connect to server
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            
            # Handle nickname request
            nickname_request = self.client_socket.recv(1024).decode('utf-8')
            if nickname_request == "NICK":
                self.client_socket.send(self.nickname.encode('utf-8'))
                
            # Start receiving thread
            self.running = True
            self.connected = True
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Update UI
            self.connection_status.config(text="🟢 Connected", fg='#00AA00')
            self.chat_status.config(text=f"Online as {self.nickname} • 0 users")
            self.message_entry.config(state=tk.NORMAL)
            self.connect_btn.config(text="Disconnect")
            self.message_entry.focus()
            
            # Add welcome message
            self.add_message_bubble(f"✅ Connected as '{self.nickname}'", 
                                  is_sent=False, sender="System")
            self.add_message_bubble("💡 **Tip:** Use *bold* _italic_ ~underline~ formatting\n🔗 Links are clickable\n😊 Click the emoji button for more\n📎 Use the paperclip button to send files", 
                                  is_sent=False, sender="Tips")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server:\n{e}")
            
    def disconnect_from_server(self):
        """Disconnect from server"""
        self.running = False
        self.connected = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
                
        # Update UI
        self.connection_status.config(text="🔴 Disconnected", fg='#FF4444')
        self.chat_status.config(text="Offline - Click Connect to start chatting")
        self.message_entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED, bg='#CCCCCC')
        self.connect_btn.config(text="Connect")
        
        # Clear online users
        for widget in self.users_container.winfo_children():
            widget.destroy()
        self.add_user_item("No users online", "Connect to see users", False)
        
        self.add_message_bubble("🔌 Disconnected from server", 
                              is_sent=False, sender="System")
        
    def receive_messages(self):
        """Receive messages from server"""
        while self.running:
            try:
                message = self.client_socket.recv(65536).decode('utf-8')  # Increased buffer for files
                if not message:
                    break
                    
                # Check if it's a user list update
                if message.startswith("USERS:"):
                    users = message[6:].split(',')
                    self.online_users = [user for user in users if user]
                    self.root.after(0, lambda: self.update_online_users(self.online_users))
                    self.root.after(0, lambda: self.update_user_count(len(self.online_users)))
                    continue
                
                # Check if it's a file message
                if message.startswith("FILE:"):
                    # Parse file message
                    parts = message.split(":", 3)
                    if len(parts) == 4:
                        _, file_name, file_extension, file_content = parts
                        # Extract sender from the beginning of file name if present
                        sender = ""
                        if " from " in file_name:
                            parts = file_name.split(" from ", 1)
                            if len(parts) == 2:
                                file_name = parts[0]
                                sender = parts[1]
                        
                        is_my_file = (sender == self.nickname) or not sender
                        self.root.after(0, lambda: self.add_file_message(
                            file_name, file_extension, file_content, 
                            sender if not is_my_file else "",
                            is_sent=is_my_file
                        ))
                    continue
                
                # Parse message and add to chat
                timestamp = datetime.now().strftime("%H:%M")
                
                if "joined the chat" in message:
                    user = message.split("👋 ")[1].split(" joined")[0]
                    self.add_message_bubble(f"👋 {user} joined the chat", 
                                          is_sent=False, sender="System")
                elif "left the chat" in message:
                    user = message.split("🚪 ")[1].split(" left")[0]
                    self.add_message_bubble(f"🚪 {user} left the chat", 
                                          is_sent=False, sender="System")
                else:
                    # Regular message - extract sender and message
                    if ":" in message:
                        # Find the first colon after timestamp
                        parts = message.split("] ", 1)
                        if len(parts) > 1:
                            msg_content = parts[1]
                            if ": " in msg_content:
                                sender, msg_text = msg_content.split(": ", 1)
                                is_my_message = (sender == self.nickname)
                                self.root.after(0, lambda: self.add_message_bubble(
                                    msg_text, 
                                    is_sent=is_my_message,
                                    sender=sender if not is_my_message else "",
                                    timestamp=timestamp
                                ))
                    
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
                break
                
        if self.running:
            self.root.after(0, self.disconnect_from_server)
    
    def update_user_count(self, count):
        """Update user count in status"""
        self.chat_status.config(text=f"Online as {self.nickname} • {count} users")
            
    def send_message(self):
        """Send message to server"""
        if not self.connected:
            return
            
        message = self.message_entry.get("1.0", tk.END).strip()
        if message and len(message) <= 500:
            try:
                # Send to server
                self.client_socket.send(message.encode('utf-8'))
                
                # Immediately show our own message in the UI
                timestamp = datetime.now().strftime("%H:%M")
                self.add_message_bubble(message, is_sent=True, timestamp=timestamp)
                
                self.message_entry.delete("1.0", tk.END)
                
            except Exception as e:
                self.add_message_bubble(f"❌ Failed to send: {e}", 
                                      is_sent=False, sender="System")
        elif len(message) > 500:
            self.add_message_bubble("❌ Message too long (max 500 characters)", 
                                  is_sent=False, sender="System")
                
    def run(self):
        """Start the application"""
        # Add welcome message
        self.add_message_bubble("👋 **Welcome to PyChat!**\n\nClick *Connect* to start chatting with others.\n\n**Features:**\n• *Formatting* with *bold* _italic_ ~underline~\n• 😊 **Enhanced emoji picker**\n• 👥 **Live user list**\n• 🌙 **Dark/light themes**\n• 📎 **File sharing** (images, PDFs, etc.)", 
                              is_sent=False, sender="Welcome")
        self.root.mainloop()
        
    def update_widget_colors(self, widget):
        """Recursively update widget colors for theme switching"""
        try:
            # Get widget type
            widget_class = widget.winfo_class()
            
            # Update background
            if 'background' in widget.keys() or 'bg' in widget.keys():
                try:
                    current_bg = widget.cget('bg')
                    # Map colors
                    if current_bg == '#FFFFFF' or current_bg == 'SystemButtonFace':
                        widget.configure(bg=self.colors['background'])
                    elif current_bg == '#F0F2F5':
                        widget.configure(bg=self.colors['sidebar_bg'])
                    elif current_bg == '#F0F0F0':
                        widget.configure(bg=self.colors['message_received'])
                    elif current_bg == '#E8F5E8':
                        widget.configure(bg=self.colors['file_bg'])
                except:
                    pass
            
            # Update foreground/text color
            if 'foreground' in widget.keys() or 'fg' in widget.keys():
                try:
                    current_fg = widget.cget('fg')
                    if current_fg == '#000000':
                        widget.configure(fg=self.colors['text_dark'])
                    elif current_fg == '#666666':
                        widget.configure(fg=self.colors['text_gray'])
                    elif current_fg == '#1E7B1E':
                        widget.configure(fg=self.colors['file_text'])
                except:
                    pass
            
            # Update highlight colors
            if 'highlightcolor' in widget.keys():
                try:
                    if widget.cget('highlightcolor') == '#0084FF':
                        widget.configure(highlightcolor=self.colors['primary'])
                except:
                    pass
            
            # Recursively update children
            for child in widget.winfo_children():
                self.update_widget_colors(child)
                
        except tk.TclError:
            pass

if __name__ == "__main__":
    app = ModernChatClient()
    app.run()