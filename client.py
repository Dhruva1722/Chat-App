import socket
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import pickle
from datetime import datetime
import os
import threading
import struct


class FirstScreen(tk.Tk):
    def __init__(self):
        super().__init__()

        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()

        self.x_co = int((screen_width / 2) - (550 / 2))
        self.y_co = int((screen_height / 2) - (400 / 2)) - 80
        self.geometry(f"550x400+{self.x_co}+{self.y_co}")
        self.title("Chat Room")

        self.user = None
        self.image_extension = None
        self.image_path = None
       
        self.first_frame = tk.Frame(self, bg="sky blue")
        self.first_frame.pack(fill="both", expand=True)

        app_icon = Image.open('assets/chaticon.png')
        app_icon = ImageTk.PhotoImage(app_icon)

        self.iconphoto(False, app_icon)

        background = Image.open("images/login_bg_ca.jpg")
        background = background.resize((550, 400), Image.LANCZOS)
        background = ImageTk.PhotoImage(background)
     

        tk.Label(self.first_frame, image=background).place(x=0, y=0)

        head = tk.Label(self.first_frame, text="Sign Up", font="lucida 17 bold", bg="grey")
        head.place(relwidth=1, y=24)

        self.username = tk.Label(self.first_frame, text="Username", font="lucida 12 bold", bg="grey")
        self.username.place(x=80, y=150)

        self.username_entry = tk.Entry(self.first_frame,  font="lucida 12 bold", width=10,
                                       highlightcolor="blue", highlightthickness=1)
        self.username_entry.place(x=195, y=150)

        self.username_entry.focus_set()

        submit_button = tk.Button(self.first_frame, text="Connect", font="lucida 12 bold", padx=30, cursor="hand2",
                                  command=self.process_data, bg="#16cade", relief="solid", bd=2)

        submit_button.place(x=200, y=275)

        self.mainloop()

    def process_data(self):
        if self.username_entry.get():
            if len(self.username_entry.get().strip()) > 6:
                self.user = self.username_entry.get()[:6] + "."
            else:
                self.user = self.username_entry.get()

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect(("192.168.43.69", 5050))
                status = client_socket.recv(1024).decode()
                if status == 'not_allowed':
                    client_socket.close()
                    messagebox.showinfo(title="Can't connect!", message='Sorry, server is completely occupied. Try again later')
                    return

            except ConnectionRefusedError:
                messagebox.showinfo(title="Can't connect!", message="Server is offline, try again later.")
                print("Server is offline, try again later.")
                return

            client_socket.send(self.user.encode('utf-8'))

      

        clients_data_size_bytes = client_socket.recv(4)
        clients_data_size_int = struct.unpack('i', clients_data_size_bytes)[0]
        clients_data_bytes = b""
        while len(clients_data_bytes) < clients_data_size_int:
            data = client_socket.recv(clients_data_size_int - len(clients_data_bytes))
            if not data:
                break
            clients_data_bytes += data

        clients_connected = pickle.loads(clients_data_bytes)

        user_id_bytes = client_socket.recv(4)  # Receive 4 bytes
        user_id = struct.unpack('i', user_id_bytes)[0]
        print(f"{self.user} is user no. {user_id}")
        ChatScreen(self, self.first_frame, client_socket, clients_connected, user_id)


class ChatScreen(tk.Canvas):
    def __init__(self, parent, first_frame, client_socket, clients_connected, user_id):
        # background_img = tk.PhotoImage(file="assets/backimage1.png")
        super().__init__(parent)

        self.window = 'ChatScreen'

        self.first_frame = first_frame
        self.first_frame.pack_forget()

        self.parent = parent
        self.bind('<Return>', lambda e: self.sent_message_format(e))

        self.all_user_image = {}

        self.user_id = user_id

        self.clients_connected = clients_connected
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.client_socket = client_socket
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()

        x_co = int((screen_width / 2) - (680 / 2))
        y_co = int((screen_height / 2) - (750 / 2)) - 80
        self.parent.geometry(f"680x750+{x_co}+{y_co}")
        # user_image = Image.open(self.parent.image_path)
        # user_image = user_image.resize((40, 40), Image.LANCZOS)
        # self.user_image = ImageTk.PhotoImage(user_image)

        global group_photo
        group_photo = Image.open('images/group_ca.png')
        group_photo = group_photo.resize((60, 60), Image.LANCZOS)
        group_photo = ImageTk.PhotoImage(group_photo)

        self.y = 140
        self.clients_online_labels = {}


        self.create_text(545, 120, text="Online", font="lucida 12 bold", fill="#40C961")

        tk.Label(self, text="   ", font="lucida 15 bold", bg="#b5b3b3").place(x=4, y=29)

        tk.Label(self, text="Group Chat", font="lucida 15 bold", padx=20, fg="green",
                 bg="#b5b3b3", anchor="w", justify="left").place(x=88, y=29, relwidth=1)

        # self.create_image(60, 40)  

        container = tk.Frame(self)
    
        container.place(x=40, y=120, width=450, height=550)
        self.canvas = tk.Canvas(container, bg="#595656")
        self.scrollable_frame = tk.Frame(self.canvas, bg="#595656")

        scrollable_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def configure_scroll_region(e):
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))

        def resize_frame(e):
            self.canvas.itemconfig(scrollable_window, width=e.width)

        self.scrollable_frame.bind("<Configure>", configure_scroll_region)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.yview_moveto(1.0)

        scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", resize_frame)
        self.canvas.pack(fill="both", expand=True)

        send_button = tk.Button(self, text="Send", fg="#83eaf7", font="lucida 11 bold", bg="#7d7d7d", padx=10,
                                relief="solid", bd=2, command=self.sent_message_format)
        send_button.place(x=400, y=680)

        self.entry = tk.Text(self, font="lucida 10 bold", width=38, height=2,
                             highlightcolor="blue", highlightthickness=1)
        self.entry.place(x=40, y=681)

        self.entry.focus_set()


        m_frame = tk.Frame(self.scrollable_frame, bg="#d9d5d4")

        t_label = tk.Label(m_frame, bg="#d9d5d4", text=datetime.now().strftime('%H:%M'), font="lucida 9 bold")
        t_label.pack()

        m_label = tk.Label(m_frame, wraplength=250, text=f"Happy Chatting {self.parent.user}",
                           font="lucida 10 bold", bg="orange")
        m_label.pack(fill="x")

        m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

        self.pack(fill="both", expand=True)

        self.clients_online([])

        t = threading.Thread(target=self.receive_data,daemon=True)
        t.start()

    def receive_data(self):
        while True:
            try:
                data_type = self.client_socket.recv(1024)

                if data_type == 'notification':
                    data_size = self.client_socket.recv(2048)
                    data_size_int = struct.unpack('i', data_size)[0]

                    b = b''
                    while True:
                        data_bytes = self.client_socket.recv(1024)
                        b += data_bytes
                        if len(b) == data_size_int:
                            break
                    data = pickle.loads(b)
                    self.notification_format(data)

                else:
                    data_bytes = self.client_socket.recv(1024)
                    data = pickle.loads(data_bytes)
                    self.received_message_format(data)

            except ConnectionAbortedError:
                print("you disconnected ...")
                self.client_socket.close()
                break
            except ConnectionResetError:
                messagebox.showinfo(title='No Connection !', message="Server offline..try connecting again later")
                self.client_socket.close()
                self.first_screen()
                break


    def on_closing(self):
        if self.window == 'ChatScreen':
            res = messagebox.askyesno(title='Warning!', message="Do you really want to disconnect?")
            if res:
                if self.user_id in self.all_user_image:
                    os.remove(self.all_user_image[self.user_id])
                    del self.all_user_image[self.user_id]
                self.client_socket.close()
                # self.first_frame.tkraise()  # Show the FirstFrame when ChatScreen is closed
                self.parent.destroy()
    # def on_closing(self):
    #         if self.window == 'ChatScreen':
    #             res = messagebox.askyesno(title='Warning !',message="Do you really want to disconnect ?")
    #             if res:
    #                 import os
    #                 os.remove(self.all_user_image[self.user_id])
    #                 self.client_socket.close()
    #                 self.first_screen()
    #         else:
    #             self.parent.destroy()

    def received_message_format(self, data):
        message = data['message']
        from_ = data['from']

        m_frame = tk.Frame(self.scrollable_frame, bg="#595656")
        m_frame.columnconfigure(1, weight=1)

        t_label = tk.Label(m_frame, bg="#595656", fg="white", text=datetime.now().strftime('%H:%M'), font="lucida 7 bold",
                        justify="left", anchor="w")
        t_label.grid(row=0, column=1, padx=2, sticky="w")

        m_label = tk.Label(m_frame, wraplength=250, fg="black", bg="#c5c7c9", text=message, font="lucida 9 bold",
                        justify="left", anchor="w")
        m_label.grid(row=1, column=1, padx=2, pady=2, sticky="w")

        m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        
    def sent_message_format(self, event=None):
        message = self.entry.get('1.0', 'end-1c')

        if message:
            if event:
                message = message.strip()
            self.entry.delete("1.0", "end-1c")

            from_ = self.user_id

            data = {'from_': from_, 'message': message}
            data_bytes = pickle.dumps(data)

            self.client_socket.send(data_bytes)

            m_frame = tk.Frame(self.scrollable_frame, bg="#595656")
            m_frame.columnconfigure(0, weight=1)

            t_label = tk.Label(m_frame, bg="#595656", fg="white", text=datetime.now().strftime('%H:%M'),
                            font="lucida 7 bold", justify="right", anchor="e")
            t_label.grid(row=0, column=0, padx=2, sticky="e")

            m_label = tk.Label(m_frame, wraplength=250, text=message, fg="black", bg="#40C961",
                            font="lucida 9 bold", justify="left", anchor="e")
            m_label.grid(row=1, column=0, padx=2, pady=2, sticky="e")

            m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1.0)


    def notification_format(self, data):
        if data['n_type'] == 'joined':

            name = data['name']
            image = data['image_bytes']
            extension = data['extension']
            message = data['message']
            client_id = data['id']
            self.clients_connected[client_id] = (name, image, extension)
            self.clients_online([client_id, name, image, extension])
            # print(self.clients_connected)

        elif data['n_type'] == 'left':
            client_id = data['id']
            message = data['message']
            self.remove_labels(client_id)
            del self.clients_connected[client_id]

        m_frame = tk.Frame(self.scrollable_frame, bg="#595656")

        t_label = tk.Label(m_frame, fg="white", bg="#595656", text=datetime.now().strftime('%H:%M'),
                           font="lucida 9 bold")
        t_label.pack()

        m_label = tk.Label(m_frame, wraplength=250, text=message, font="lucida 10 bold", justify="left", bg="sky blue")
        m_label.pack()

        m_frame.pack(pady=10, padx=10, fill="x", expand=True, anchor="e")

        self.canvas.yview_moveto(1.0)
    def clients_online(self, connected_clients):
        for widget in self.clients_online_labels.values():
            widget.destroy()
        self.clients_online_labels = {}

        for user_id, (name, _) in connected_clients:
            if user_id in self.all_user_image:
                image = self.all_user_image[user_id]
                label = tk.Label(self.scrollable_frame, text=name, compound="left", image=image,
                                font="lucida 10 bold", bg="#d9d5d4", padx=10, pady=5)
            else:
                label = tk.Label(self.scrollable_frame, text=name, font="lucida 10 bold",
                                bg="#d9d5d4", padx=10, pady=5)
            label.pack(anchor="w", fill="x", padx=10)
            self.clients_online_labels[user_id] = label
    def remove_labels(self, client_id):
        for user_id in list(self.clients_online_labels.keys()):
            label = self.clients_online_labels[user_id][0]
            y_co = self.clients_online_labels[user_id][1]
            if user_id == client_id:
                print("yes")
                label.destroy()
                del self.clients_online_labels[client_id]
                
            elif user_id > client_id:
                y_co -= 60
                label.place(x=510, y=y_co)
                self.clients_online_labels[user_id] = (label, y_co)
                self.y -= 60
    def first_screen(self):
        self.destroy()
        self.winfo_geometry(f"550x400+{self.parent.x_co}+{self.parent.y_co}")
        self.pack(fill="both", expand=True)
        self.window = None
FirstScreen()