import socket
import threading
import time

class ChatClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.nickname = ""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
    
    def receive_messages(self):
        """Receive messages from server in a separate thread"""
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    print(f"\r{message}\nYou: ", end="")
                else:
                    print("\r❌ Connection lost with server")
                    self.running = False
                    break
            except:
                print("\r❌ Error receiving messages")
                self.running = False
                break
    
    def send_message(self, message):
        """Send message to server"""
        try:
            self.client_socket.send(message.encode('utf-8'))
        except:
            print("❌ Failed to send message")
    
    def start_client(self):
        """Start the chat client"""
        try:
            print("🤖 Python Chat Client")
            print("=" * 30)
            
            # Connect to server
            self.client_socket.connect((self.host, self.port))
            print(f"✅ Connected to server {self.host}:{self.port}")
            
            # Get nickname from server request
            nickname_request = self.client_socket.recv(1024).decode('utf-8')
            if nickname_request == "NICK":
                self.nickname = input("Enter your nickname: ").strip()
                while not self.nickname:
                    self.nickname = input("Nickname cannot be empty. Enter your nickname: ").strip()
                self.client_socket.send(self.nickname.encode('utf-8'))
            
            # Receive welcome message and emoji tip
            welcome_msg = self.client_socket.recv(1024).decode('utf-8')
            emoji_tip = self.client_socket.recv(1024).decode('utf-8')
            
            print(f"\n{welcome_msg}")
            print(f"{emoji_tip}")
            print("\n💬 Start chatting! (Type 'QUIT' to exit)")
            print("🎭 Use emojis: :) :( :D ;) :P <3 :O")
            print("-" * 50)
            
            # Start message receiving thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Main message sending loop
            while self.running:
                message = input("You: ").strip()
                
                if not message:
                    continue
                
                if message.upper() == 'QUIT':
                    print("👋 Goodbye!")
                    self.running = False
                    break
                elif message.upper() == 'HELP':
                    print("Available commands: QUIT, HELP")
                    print("Emoji examples: :) :( :D ;) :P <3 :O :*")
                    continue
                elif message.upper() == 'EMOJIS':
                    print("Common emojis:")
                    print("  :) 😊  :( 😢  :D 😃  ;) 😉  :P 😛")
                    print("  :O 😮  :* 😘  <3 ❤️ :/ 😕  :| 😐")
                    continue
                
                self.send_message(message)
            
        except ConnectionRefusedError:
            print("❌ Could not connect to server. Make sure the server is running.")
        except Exception as e:
            print(f"❌ Client error: {e}")
        finally:
            self.client_socket.close()
            print("🔌 Disconnected from server")
 
if __name__ == "__main__":
    client = ChatClient()
    client.start_client()