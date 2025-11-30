import socket
import threading
import time
from datetime import datetime

class ChatServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.clients = []  # List of connected clients
        self.nicknames = []  # List of client nicknames
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Emoji mapping
        self.emoji_map = {
            ':)': '😊', ':(': '😢', ':D': '😃', ';)': '😉', ':P': '😛', ':O': '😮',
            ':*': '😘', '<3': '❤️', ':/': '😕', ':|': '😐', ';)': '😜', ':\\': '😕',
            ':\'(': '😭', '>:(': '😠', ':|': '😐', 'o:)': '😇', '3:)': '😈', ':@': '😠',
            ':3': '😺', '^_^': '😄', '>_<': '😣', 'T_T': '😭', '>:D': '😈', ':-)': '😊',
            ':-(': '😞', ':-D': '😃', ';-D': '😜', ':-P': '😛', ':-O': '😮', ':-*': '😘',
            '</3': '💔', ':\\': '😕', ':\'D': '😂', '>:O': '😲', 'O_O': '😳', 'X-O': '🤕',
            'B)': '😎', ':poop:': '💩', ':fire:': '🔥', ':thumbsup:': '👍', ':thumbsdown:': '👎',
            ':clap:': '👏', ':pray:': '🙏', ':muscle:': '💪', ':100:': '💯', ':tada:': '🎉',
            ':camera:': '📷', ':book:': '📖', ':computer:': '💻', ':phone:': '📱'
        }
        
    def parse_emojis(self, text):
        """Replace emoji codes with actual emojis"""
        for code, emoji in self.emoji_map.items():
            text = text.replace(code, emoji)
        return text
        
    def broadcast(self, message, sender_socket=None):
        """Send message to all connected clients except the sender"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        print(formatted_message)  # Display on server console
        
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(formatted_message.encode('utf-8'))
                except:
                    # Remove broken connections
                    self.remove_client(client)

    def update_user_list(self):
        """Send updated user list to all clients"""
        user_list = "USERS:" + ",".join(self.nicknames)
        self.broadcast(user_list, None)
    
    def remove_client(self, client_socket):
        """Remove a client and clean up"""
        if client_socket in self.clients:
            index = self.clients.index(client_socket)
            nickname = self.nicknames[index]
            
            self.clients.remove(client_socket)
            self.nicknames.remove(nickname)
            
            self.broadcast(f"🚪 {nickname} left the chat!")
            self.update_user_list()  # Update user list after removal
            client_socket.close() 
    
    def handle_client(self, client_socket):
        """Handle messages from a single client"""
        try:
            # Ask for nickname
            client_socket.send("NICK".encode('utf-8'))
            nickname = client_socket.recv(1024).decode('utf-8')
            
            self.clients.append(client_socket)
            self.nicknames.append(nickname)
            
            # Update user list for all clients
            self.update_user_list()
            
            # Welcome the new user
            welcome_msg = f"🎉 Welcome to Python Chat, {nickname}!"
            client_socket.send(welcome_msg.encode('utf-8'))
            
            # Send emoji help message
            emoji_help = "💡 Emoji tip: Use :) :( :D <3 etc. in your messages!"
            client_socket.send(emoji_help.encode('utf-8'))
            
            # Notify all users about new connection
            self.broadcast(f"👋 {nickname} joined the chat!")
            
            while True:
                try:
                    message = client_socket.recv(1024).decode('utf-8')
                    if message:
                        # Parse emojis in the message before broadcasting
                        message_with_emojis = self.parse_emojis(message)
                        self.broadcast(f"{nickname}: {message_with_emojis}", client_socket)
                    else:
                        self.remove_client(client_socket)
                        break
                except:
                    self.remove_client(client_socket)
                    break
                    
        except Exception as e:
            print(f"Error handling client: {e}")
            self.remove_client(client_socket)

    
    def start_server(self):
        """Start the chat server"""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            print(f"🚀 Chat Server started on {self.host}:{self.port}")
            print("📍 Waiting for connections...")
            print("📍 Type 'SHUTDOWN' to stop the server\n")
            
            # Thread to handle server commands
            command_thread = threading.Thread(target=self.handle_server_commands)
            command_thread.daemon = True
            command_thread.start()
            
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"✅ New connection from {address[0]}:{address[1]}")
                
                # Start a new thread for each client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.server_socket.close()
    
    def handle_server_commands(self):
        """Handle server admin commands"""
        while True:
            command = input().strip()
            if command.upper() == 'SHUTDOWN':
                print("🛑 Shutting down server...")
                self.shutdown_server()
                break
            elif command.upper() == 'USERS':
                print(f"📊 Connected users: {', '.join(self.nicknames) if self.nicknames else 'None'}")
            elif command.upper() == 'EMOJIS':
                print("🎭 Available emojis:")
                for code, emoji in self.emoji_map.items():
                    print(f"  {code} -> {emoji}")
            elif command.upper() == 'HELP':
                print("Available commands: SHUTDOWN, USERS, EMOJIS, HELP")
    
    def shutdown_server(self):
        """Gracefully shutdown the server"""
        self.broadcast("🔴 Server is shutting down. Goodbye!")
        time.sleep(1)  # Give clients time to receive the message
        
        for client in self.clients:
            client.close()
        
        self.server_socket.close()
        print("✅ Server shut down successfully")
 
if __name__ == "__main__":
    server = ChatServer()
    server.start_server()