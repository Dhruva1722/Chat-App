import socket
import threading
import tkinter as tk

# Create a server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("192.168.1.188", 8000))
server_socket.listen(5)

# List to hold client connections and usernames
client_sockets = []
client_usernames = []


def handle_client(client_socket):
    # Receive the username from the client
    username = client_socket.recv(1024).decode("utf-8")
    client_usernames.append(username)
    
    while True:
        try:
            # Receive message from the client
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                # If the client connection is closed, remove it from the list
                index = client_sockets.index(client_socket)
                print(f"Received message from {username}: {message}")
                client_sockets.remove(client_socket)
                client_usernames.remove(client_usernames[index])
                break

            # Broadcast the message to all connected client
            for socket in client_sockets:
                socket.send((username + ": " + message).encode("utf-8"))
        except ConnectionResetError:
            # If the client connection is reset, remove it from the list
            index = client_sockets.index(client_socket)
            client_sockets.remove(client_socket)
            client_usernames.remove(client_usernames[index])
            break

def accept_connections():
    while True:
        # Accept new client connections
        client_socket, address = server_socket.accept()
        client_sockets.append(client_socket)

        # Start a new thread to handle the client
        threading.Thread(target=handle_client, args=(client_socket,)).start()

def close_sockets():
    for client_socket in client_sockets:
        client_socket.close()
    server_socket.close()
    server_ui.destroy()

# Create the server UI
server_ui = tk.Tk()
server_ui.geometry("700x470")
server_ui.title("Chat Room")
logo = tk.PhotoImage(file="assets/chaticon.png")
server_ui.iconphoto(False,logo)


#backgroung img
background_image = tk.PhotoImage(file="assets/chatbg.png")
background_label = tk.Label(server_ui,image=background_image )
background_label.place(x=0, y=0, relwidth=1, relheight=1)


# Label to display server status
status_label = tk.Label(server_ui ,text="Server is listening on localhost:8000",background="black",height=3,width=40,font=(("Comic Sans MS", 15)) ,fg="white") 
status_label.pack(padx=10,pady=10)

# Label to display welcome message
welcome_label = tk.Label(server_ui, text="Welcome to the chat room!",background="black",height=3,width=25 ,font=(("Comic Sans MS", 15)),fg="white")
welcome_label.pack(padx=10,pady=10)

# Button to close the server
close_button = tk.Button(server_ui, text="Close Server", command=close_sockets,background="black",bd=0,height=3,width=15,font=(("Comic Sans MS", 15)),fg="white")
close_button.pack(padx=10,pady=10)

# Start accepting client connections
accept_thread = threading.Thread(target=accept_connections)
accept_thread.start()

# Run the Tkinter event loop
server_ui.mainloop()


