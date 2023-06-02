import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

client_socket=None


def receive_message():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            text_widget.configure(state="normal")
            text_widget.insert(tk.END, message + '\n', "received_message")
            text_widget.configure(state="disabled")
            text_widget.see(tk.END)
        except Exception as e:
            print(f"Error receiving message: {str(e)}")
            break

def send_message(event=None):
    global client_socket
    message = input_text.get()
    if message and client_socket:
        input_text.delete(0, tk.END)
        text_widget.configure(state="normal")
        text_widget.insert(tk.END, f"{message}\n", "sent_message")
        text_widget.configure(state="disabled")
        text_widget.see(tk.END)
        client_socket.send(message.encode('utf-8'))

def connect_to_server():
    host = 'localhost'
    port = 9999

    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    receive_thread = threading.Thread(target=receive_message)
    receive_thread.start()


client_ui = tk.Tk()
client_ui.geometry("400x400")
client_ui.title("Chat App")

    # Background image
background_image = tk.PhotoImage(file="assets/chatbg.png")
background_label = tk.Label(client_ui, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Heading with icon
heading_frame = tk.Frame(client_ui, bg="whitesmoke")
heading_frame.pack(fill="x", padx=40, pady=20)

    # Icon
logo = tk.PhotoImage(file="assets/chaticon.png")
icon_label = tk.Label(heading_frame, image=logo)
icon_label.pack(side="left")

    # Text
heading_label = tk.Label(heading_frame, text="Group Chating", font=("Microsoft Sans Serif", 16),
                         bg="whitesmoke", fg="slategray")
heading_label.pack(side="left", padx=5)

    # Frame to hold the chat display, input label, and button
chat_frame = tk.Frame(client_ui, background="slategray", border=2, borderwidth=5)
chat_frame.pack(padx=20, pady=20, expand=True)

    # Username label
username = "John"  # Replace with the username entered by the client
username_label = tk.Label(chat_frame, text=f"Ready to Chat ({username})", background="slategray",
                              font=("Microsoft Sans Serif", 14, "bold"), fg="whitesmoke")
username_label.pack()

    # Create a scrolled text widget for the chat display
text_widget = scrolledtext.ScrolledText(chat_frame, width=40, height=10)
text_widget.pack(pady=10)

    # Configure tags for sent and received messages
text_widget.tag_configure("sent_message", justify="left", background="lightgreen")
text_widget.tag_configure("received_message", justify="right", background="pink")

    # Input frame
input_frame = tk.Frame(chat_frame, background="slategray")
input_frame.pack(pady=10)

    # Entry widget for user input
input_text = tk.Entry(input_frame, width=30, font=("Arial", 12))
input_text.bind("<Return>", send_message)
input_text.pack(side="left", padx=5)

    # Button to send the message
send_button = tk.Button(input_frame, text="Send", width=20, command=send_message)
send_button.pack(side="left", padx=5)

client_ui.mainloop()

connect_to_server()
