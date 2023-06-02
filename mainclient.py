import datetime
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

# File to save the chat messages
chat_log_file = "chat_log.txt"

def receive_message():
    while True:
        try:
            # Receive message from the server
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                # If the server connection is closed, exit the thread
                break
            
            current_time = datetime.now().strftime("%H:%M")
            formatted_message = f"{current_time} \n {message}"

            # Display the message in the chat window
            text_widget.configure(state=tk.NORMAL)
            text_widget.insert(tk.END, formatted_message + "\n")
            text_widget.configure(state="disabled")
            text_widget.see(tk.END)
            
             # Save the message to the chat log file
            save_to_chat_log(message)   
            
        except ConnectionResetError:
            # If the server connection is reset, exit the thread
            break
def save_to_chat_log(message):
    current_time = datetime.now().strftime("%H:%M:%S")
    formatted_message = f"[{current_time}] {message}"
    with open(chat_log_file, "a") as file:
        file.write(formatted_message + "\n")


def send_message(event=None):
    message = input_text.get()
    if message.strip() != "":
        # Send the message to the server
        client_socket.send(message.encode("utf-8"))
        # Clear the input field
        input_text.delete(0, "end")
        current_time = datetime.now().strftime("%H:%M")
        formatted_message = f"{current_time} \n {message}"

        # # Display the message in the chat window
        # text_widget.configure(state=tk.NORMAL)
        text_widget.insert(tk.END, formatted_message + "\n", "sent")  # Add a tag for sent messages
        # text_widget.configure(state="disabled")
        # text_widget.see(tk.END)

        # Save the message to the chat log file
        save_to_chat_log(message)
        
        
# Update the online icon based on the user's status
def update_online_status(status):
    if status == "online":
        online_icon_label.config(image=online_icon)
    else:
        online_icon_label.config(image="")  # Clear the icon if status is not online

# Call the update_online_status() function with the appropriate status
    update_online_status("online")
    
    
def remove_client():
        client_socket.send("left the chat room","received".encode("utf-8"))
        client_socket.close()
        client_ui.quit()

        
# Create a client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("192.168.1.188", 8000))

# Ask the user for a username
username = input("Enter your username: ")
client_socket.send(username.encode("utf-8"))

# Start a thread to receive messages from the server
receive_thread = threading.Thread(target=receive_message)
receive_thread.start()

# Main Tkinter window for the client UI
client_ui = tk.Tk()
client_ui.geometry("700x670")
client_ui.title("Chat App")
logo = tk.PhotoImage(file="assets/chaticon.png")
client_ui.iconphoto(False,logo)


#backgroung img
background_image = tk.PhotoImage(file="assets/chatbg.png")
background_label = tk.Label(client_ui,image=background_image )
background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Heading with icon
heading_frame = tk.Frame(client_ui, bg="whitesmoke")
heading_frame.pack(fill="x", padx=40, pady=20)
# Text
heading_label = tk.Label(heading_frame, text="Group Chating", font=("cursive", 16,"bold"),
                         bg="whitesmoke", fg="black")
heading_label.pack(side="left", padx=5)

name_frame = tk.Frame(client_ui, background="black")
name_frame.pack(padx=10, pady=10)

 #Username label
username_label = tk.Label( name_frame,text=f"Ready to Chat ({username})", background="black",
                          font=("Microsoft Sans Serif", 14, "bold"), fg="whitesmoke", compound="left")

online_icon = tk.PhotoImage(file="assets/green_dot.png")
online_icon_label = tk.Label( name_frame,image=online_icon, bg="black")

# Pack the username and online icon labels
username_label.pack(side="left")
online_icon_label.pack(side="left", padx=5)

 # Frame to hold the chat display, input label, and button
chat_frame = tk.Frame(client_ui, background="black", border=2, borderwidth=5)
chat_frame.pack(padx=20, pady=20)



    # Create a scrolled text widget for the chat display
text_widget = scrolledtext.ScrolledText(chat_frame, width=40, height=20,font=("Arial", 12))
text_widget.pack(padx=20,pady=10)
text_widget.configure(state="disabled",padx=10,pady=10)
# Configure tags for different message styles
text_widget.tag_config("received", foreground="red", lmargin1=10, lmargin2=10)
text_widget.tag_config("sent", foreground="blue", rmargin=10)

 # Input frame
input_frame = tk.Frame(chat_frame, background="dimgray",height=5)
input_frame.pack(pady=10)
# Entry widget for user input
input_text = tk.Entry( input_frame, width=30,font=("Arial", 12),background="lightgray")
input_text.bind("<Return>", send_message)
input_text.pack(side="left", padx=5)

# Button to send messages
send_icon = tk.PhotoImage(file="assets/send.png")
send_button = tk.Button(input_frame, image=send_icon, command=send_message,background="dimgray" ,bd=0)
send_button.pack(side="left", padx=5,pady=5)

 # Remove button
remove_icon = tk.PhotoImage(file="assets/remove.png")
remove_button = tk.Button(chat_frame,image=remove_icon, command=remove_client,background="black",bd=0)
remove_button.pack(side="bottom",padx=10)


# Run the Tkinter event loop
client_ui.mainloop()




