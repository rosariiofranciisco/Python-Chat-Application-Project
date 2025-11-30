import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import socket
import threading
import time
from datetime import datetime
import json

class ModernChatClient:
    def __init__(self):
        self.host = 'localhost'
        self.port = 12345
        self.nickname = ""
        self.client_socket = None
        self.running = False
        self.connected = False
        
        # Create modern window
        self.root = tk.Tk()
        self.root.title("PyChat • Modern Messaging")
        self.root.geometry("800x600")  # More reasonable default size
        self.root.configure(bg='#FFFFFF')
        self.root.minsize(400, 300)  # Much smaller minimum size
        
        # Modern color scheme
        self.colors = {
            'primary': '#0084FF',
            'primary_light': '#E5F3FF',
            'background': '#FFFFFF',
            'sidebar_bg': '#F0F0F0',
            'message_sent': '#0084FF',
            'message_received': '#F0F0F0',
            'text_light': '#FFFFFF',
            'text_dark': '#000000',
            'text_gray': '#666666',
            'online_green': '#00D500'
        }
        
        # Emoji picker data
        self.common_emojis = ['😊', '😂', '❤️', '😍', '🔥', '👍', '😎', '🎉', '👏', '🙏', '💯', '😢', '😡', '🤔', '👀']
        
        self.setup_modern_gui()
        
    def setup_modern_gui(self):
        """Setup modern social media-style interface"""
        # Main container with modern styling
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar (Conversations list) - Like WhatsApp left panel
        self.setup_sidebar(main_container)
        
        # Chat area - Like WhatsApp right panel
        self.setup_chat_area(main_container)
        
        # Connection panel at bottom
        self.setup_connection_panel()
        
    def setup_sidebar(self, parent):
        """Setup the conversations sidebar"""
        sidebar_frame = tk.Frame(parent, bg=self.colors['sidebar_bg'], width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        sidebar_frame.pack_propagate(False)
        
        # Sidebar header
        header_frame = tk.Frame(sidebar_frame, bg=self.colors['primary'], height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # App title in header
        title_label = tk.Label(
            header_frame,
            text="💬 PyChat",
            font=('Segoe UI', 16, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['primary'],
            pady=20
        )
        title_label.pack(side=tk.LEFT, padx=15)
        
        # Search bar (now functional)
        search_frame = tk.Frame(sidebar_frame, bg=self.colors['sidebar_bg'], height=50)
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
        self.search_entry.insert(0, "🔍 Search conversations...")
        self.search_entry.bind('<FocusIn>', self.clear_search_placeholder)
        self.search_entry.bind('<FocusOut>', self.restore_search_placeholder)
        self.search_entry.bind('<KeyRelease>', self.filter_conversations)
        
        # Conversations list
        conversations_frame = tk.Frame(sidebar_frame, bg=self.colors['sidebar_bg'])
        conversations_frame.pack(fill=tk.BOTH, expand=True)
        
        # Online users list container with scrollbar
        self.conversations_container = tk.Frame(conversations_frame, bg=self.colors['sidebar_bg'])
        self.conversations_container.pack(fill=tk.BOTH, expand=True)
        
        # Default group chat
        self.conversations = ["💬 General Chat"]
        self.add_conversation_item("💬 General Chat", "Group chat with everyone", "10:30", True)
        
    def setup_chat_area(self, parent):
        """Setup the main chat area"""
        self.chat_container = tk.Frame(parent, bg=self.colors['background'])
        self.chat_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chat header (like WhatsApp chat header)
        self.chat_header = tk.Frame(self.chat_container, bg=self.colors['sidebar_bg'], height=60)
        self.chat_header.pack(fill=tk.X, padx=0, pady=0)
        self.chat_header.pack_propagate(False)
        
        # Chat info in header
        self.chat_title = tk.Label(
            self.chat_header,
            text="💬 General Chat",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_dark'],
            bg=self.colors['sidebar_bg']
        )
        self.chat_title.pack(side=tk.LEFT, padx=20, pady=20)
        
        self.chat_status = tk.Label(
            self.chat_header,
            text="Offline - Click Connect to start chatting",
            font=('Segoe UI', 10),
            fg=self.colors['text_gray'],
            bg=self.colors['sidebar_bg']
        )
        self.chat_status.pack(side=tk.LEFT, padx=20)
        
        # Messages area with modern scrollbar
        messages_container = tk.Frame(self.chat_container, bg=self.colors['background'])
        messages_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create a frame for messages with scrollbar
        self.messages_frame = tk.Frame(messages_container, bg=self.colors['background'])
        self.messages_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a canvas and scrollbar for messages
        self.messages_canvas = tk.Canvas(
            self.messages_frame,
            bg=self.colors['background'],
            highlightthickness=0
        )
        
        self.scrollbar = ttk.Scrollbar(self.messages_frame, orient="vertical", command=self.messages_canvas.yview)
        self.messages_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollable_messages_frame = tk.Frame(self.messages_canvas, bg=self.colors['background'])
        self.scrollable_messages_frame.bind(
            "<Configure>",
            lambda e: self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all"))
        )
        
        self.messages_canvas.create_window((0, 0), window=self.scrollable_messages_frame, anchor="nw", width=self.messages_canvas.winfo_width())
        
        # Pack the canvas and scrollbar
        self.messages_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind the canvas resize event
        self.messages_canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Message input area
        self.input_frame = tk.Frame(self.chat_container, bg=self.colors['sidebar_bg'], height=100)
        self.input_frame.pack(fill=tk.X, padx=0, pady=0)
        self.input_frame.pack_propagate(False)
        
        # Emoji picker row
        emoji_frame = tk.Frame(self.input_frame, bg=self.colors['sidebar_bg'], height=30)
        emoji_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Add common emojis as quick buttons
        emoji_label = tk.Label(
            emoji_frame,
            text="Quick emojis:",
            font=('Segoe UI', 9),
            fg=self.colors['text_gray'],
            bg=self.colors['sidebar_bg']
        )
        emoji_label.pack(side=tk.LEFT)
        
        for emoji in self.common_emojis:
            emoji_btn = tk.Label(
                emoji_frame,
                text=emoji,
                font=('Segoe UI', 12),
                bg=self.colors['sidebar_bg'],
                cursor="hand2",
                padx=2
            )
            emoji_btn.pack(side=tk.LEFT, padx=1)
            emoji_btn.bind("<Button-1>", lambda e, em=emoji: self.insert_emoji(em))
        
        # Message input with modern styling
        input_container = tk.Frame(self.input_frame, bg=self.colors['background'])
        input_container.place(relx=0.5, rely=0.7, anchor='center', width=500, height=40)
        
        self.message_entry = tk.Entry(
            input_container,
            font=('Segoe UI', 12),
            bg=self.colors['background'],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=self.colors['primary'],
            highlightbackground='#DDDDDD'
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=5)
        self.message_entry.bind('<Return>', lambda event: self.send_message())
        
        # Send button with modern style
        self.send_button = tk.Label(
            input_container,
            text="➤",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_light'],
            bg='#CCCCCC',  # Start disabled
            width=3,
            height=1,
            cursor="hand2",
            relief=tk.FLAT
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 10), pady=5)
        self.send_button.bind("<Button-1>", lambda e: self.send_message())
        
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
            padx=15,
            pady=5,
            relief=tk.FLAT
        )
        self.connect_btn.pack(side=tk.RIGHT, padx=20, pady=5)
        self.connect_btn.bind("<Button-1>", lambda e: self.toggle_connection())
        
    def insert_emoji(self, emoji):
        """Insert emoji at cursor position"""
        if self.message_entry['state'] == 'normal':
            current_text = self.message_entry.get()
            cursor_pos = self.message_entry.index(tk.INSERT)
            self.message_entry.delete(0, tk.END)
            self.message_entry.insert(0, current_text[:cursor_pos] + emoji + current_text[cursor_pos:])
            self.message_entry.focus()
            self.message_entry.icursor(cursor_pos + len(emoji))
        
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        self.messages_canvas.itemconfig(1, width=event.width)  # 1 is the first item created (our frame)
        
    def clear_search_placeholder(self, event):
        """Clear search placeholder text"""
        if self.search_entry.get() == "🔍 Search conversations...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.colors['text_dark'])
            
    def restore_search_placeholder(self, event):
        """Restore search placeholder if empty"""
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "🔍 Search conversations...")
            self.search_entry.config(fg=self.colors['text_gray'])
            
    def filter_conversations(self, event):
        """Filter conversations based on search text"""
        search_text = self.search_entry.get().lower()
        if search_text == "🔍 search conversations...":
            return
            
        # Clear current conversations
        for widget in self.conversations_container.winfo_children():
            widget.destroy()
            
        # Add filtered conversations
        for conv in self.conversations:
            if search_text in conv.lower():
                self.add_conversation_item(conv, "Group chat with everyone", "10:30", False)
                 
    def add_conversation_item(self, name, last_message, time, selected=False):
        """Add a conversation item to sidebar"""
        conv_frame = tk.Frame(self.conversations_container, bg=self.colors['sidebar_bg'], height=70)
        conv_frame.pack(fill=tk.X, padx=5, pady=1)
        conv_frame.pack_propagate(False)
        
        # Highlight if selected
        if selected:
            conv_frame.config(bg=self.colors['primary_light'])
            bg_color = self.colors['primary_light']
        else:
            bg_color = self.colors['sidebar_bg']
        
        # Avatar
        avatar = tk.Label(
            conv_frame,
            text=name[0],
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['primary'],
            width=3,
            height=2,
            relief=tk.FLAT
        )
        avatar.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Conversation info
        info_frame = tk.Frame(conv_frame, bg=bg_color)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        name_label = tk.Label(
            info_frame,
            text=name,
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_dark'],
            bg=bg_color,
            anchor='w'
        )
        name_label.pack(fill=tk.X)
        
        msg_label = tk.Label(
            info_frame,
            text=last_message,
            font=('Segoe UI', 10),
            fg=self.colors['text_gray'],
            bg=bg_color,
            anchor='w'
        )
        msg_label.pack(fill=tk.X)
        
        # Time
        time_label = tk.Label(
            conv_frame,
            text=time,
            font=('Segoe UI', 9),
            fg=self.colors['text_gray'],
            bg=bg_color
        )
        time_label.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Bind click event
        conv_frame.bind("<Button-1>", lambda e: self.select_conversation(name, conv_frame))
        for child in conv_frame.winfo_children():
            child.bind("<Button-1>", lambda e, n=name, f=conv_frame: self.select_conversation(n, f))
        
    def select_conversation(self, name, frame):
        """Handle conversation selection"""
        self.chat_title.config(text=name)
        # Reset all backgrounds
        for widget in self.conversations_container.winfo_children():
            widget.config(bg=self.colors['sidebar_bg'])
            for child in widget.winfo_children():
                if isinstance(child, tk.Frame):
                    child.config(bg=self.colors['sidebar_bg'])
        
        # Highlight selected
        frame.config(bg=self.colors['primary_light'])
        for child in frame.winfo_children():
            if isinstance(child, tk.Frame):
                child.config(bg=self.colors['primary_light'])
                
    def add_message_bubble(self, message, is_sent=False, sender="", timestamp=""):
        """Add a modern message bubble"""
        if not timestamp:
            timestamp = datetime.now().strftime("%H:%M")
            
        message_frame = tk.Frame(self.scrollable_messages_frame, bg=self.colors['background'])
        message_frame.pack(fill=tk.X, padx=20, pady=2)
        
        # Align messages to right if sent, left if received
        if is_sent:
            bubble_bg = self.colors['message_sent']
            text_color = self.colors['text_light']
            anchor = 'e'
            padx = (150, 20)  # More space on left to push to right
        else:
            bubble_bg = self.colors['message_received']
            text_color = self.colors['text_dark']
            anchor = 'w'
            padx = (20, 150)  # More space on right to push to left
            
        # Create bubble container with proper alignment
        bubble_container = tk.Frame(message_frame, bg=self.colors['background'])
        if is_sent:
            bubble_container.pack(anchor='e', fill=tk.X)
        else:
            bubble_container.pack(anchor='w', fill=tk.X)
        
        # Show sender name for received messages (not our own)
        if sender and not is_sent:
            sender_label = tk.Label(
                bubble_container,
                text=sender,
                font=('Segoe UI', 9, 'bold'),
                fg=self.colors['text_gray'],
                bg=self.colors['background'],
                anchor=anchor
            )
            sender_label.pack(anchor=anchor, padx=padx)
        
        # Message bubble frame for proper alignment
        bubble_frame = tk.Frame(bubble_container, bg=self.colors['background'])
        bubble_frame.pack(anchor=anchor, padx=padx)
        
        # Message bubble
        bubble = tk.Label(
            bubble_frame,
            text=message,
            font=('Segoe UI', 11),
            fg=text_color,
            bg=bubble_bg,
            wraplength=300,  # Fixed wrap length for better bubbles
            justify=tk.LEFT,
            padx=15,
            pady=8,
            relief=tk.FLAT
        )
        bubble.pack(anchor=anchor)
        
        # Time stamp
        time_label = tk.Label(
            bubble_frame,
            text=timestamp,
            font=('Segoe UI', 8),
            fg=self.colors['text_gray'],
            bg=self.colors['background']
        )
        time_label.pack(anchor=anchor)
        
        # Auto-scroll to bottom
        self.messages_canvas.update_idletasks()
        self.messages_canvas.yview_moveto(1.0)
        
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
                initialvalue="User"
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
            self.chat_status.config(text=f"Online as {self.nickname}")
            self.message_entry.config(state=tk.NORMAL)
            self.send_button.config(bg=self.colors['primary'])
            self.connect_btn.config(text="Disconnect")
            self.message_entry.focus()
            
            # Add welcome message
            self.add_message_bubble(f"Connected as '{self.nickname}'", is_sent=False, 
                                  sender="System")
            self.add_message_bubble("💡 Tip: Use the emoji buttons above or type :) :( :D <3 etc.", 
                                  is_sent=False, sender="System")
            
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
        self.send_button.config(bg='#CCCCCC')
        self.connect_btn.config(text="Connect")
        
        self.add_message_bubble("Disconnected from server", is_sent=False,
                              sender="System")
        
    def receive_messages(self):
        """Receive messages from server"""
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                    
                # Parse message and add to chat
                timestamp = datetime.now().strftime("%H:%M")
                
                if "joined the chat" in message:
                    self.add_message_bubble(message.split("👋 ")[1], is_sent=False,
                                          sender="System")
                elif "left the chat" in message:
                    self.add_message_bubble(message.split("🚪 ")[1], is_sent=False,
                                          sender="System")
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
                                self.add_message_bubble(msg_text, is_sent=is_my_message,
                                                      sender=sender if not is_my_message else "",
                                                      timestamp=timestamp)
                    
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
                break
                
        if self.running:
            self.root.after(0, self.disconnect_from_server)
            
    def send_message(self):
        """Send message to server"""
        message = self.message_entry.get().strip()
        if message and self.connected:
            try:
                # Send to server
                self.client_socket.send(message.encode('utf-8'))
                
                # Immediately show our own message in the UI
                timestamp = datetime.now().strftime("%H:%M")
                self.add_message_bubble(message, is_sent=True, timestamp=timestamp)
                
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                self.add_message_bubble(f"Failed to send: {e}", is_sent=False,
                                      sender="System")
                
    def run(self):
        """Start the application"""
        # Add welcome message
        self.add_message_bubble("Welcome to PyChat! Click 'Connect' to start chatting.", 
                              is_sent=False, sender="System")
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernChatClient()
    app.run()