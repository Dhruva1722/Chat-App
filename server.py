# import socket
# import struct
# import pickle
# import threading

# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('localhost', 9999))
# server_socket.listen(4)

# clients_connected = {}
# clients_data = {}
# count = 1


# def connection_requests():
#     global count
#     while True:
#         try:
#             print("Waiting for connection...")
#             client_socket, address = server_socket.accept()

#             print(f"Connection from {address} has been established")
#             print(len(clients_connected))
#             if len(clients_connected) == 4:
#                 client_socket.send('not_allowed'.encode())
#                 client_socket.close()
#                 continue
#             else:
#                 client_socket.send('allowed'.encode())
#         except (ConnectionAbortedError, ConnectionError) as e:
#             print(e.strerror)
            
#         try:
#             client_name = client_socket.recv(1024).decode('utf-8')
#         except:
#             print(f"{address} disconnected")
#             client_socket.close()
#             continue

#         print(f"{address} identified itself as {client_name}")

#         clients_connected[client_socket] = client_name

#         clients_data[count] = client_name

#         clients_data_bytes = pickle.dumps(clients_data)
#         clients_data_length = struct.pack('i', len(clients_data_bytes))

#         client_socket.send(clients_data_length)
#         client_socket.send(clients_data_bytes)

#         if client_socket.recv(1024).decode() == 'data_received':
#             client_socket.send(struct.pack('i', count))

#             for client in clients_connected:
#                 if client != client_socket:
#                     client.send('notification'.encode())
#                     data = pickle.dumps({'message': f"{client_name} joined the chat", 'n_type': 'joined', 'id': count})
#                     data_length_bytes = struct.pack('i', len(data))
#                     client.send(data_length_bytes)
#                     client.send(data)
#         count += 1
#         t = threading.Thread(target=receive_data, args=(client_socket,))
#         t.start()


# def receive_data(client_socket):
#     while True:
#         try:
#             data_bytes = client_socket.recv(1024)
#         except ConnectionResetError:
#             print(f"{clients_connected[client_socket][0]} disconnected")

#             for client in clients_connected:
#                 if client != client_socket:
#                     client.send('notification'.encode())

#                     data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} left the chat",
#                                          'id': clients_connected[client_socket][1], 'n_type': 'left'})

#                     data_length_bytes = struct.pack('i', len(data))
#                     client.send(data_length_bytes)

#                     client.send(data)
#                 client_index = clients_connected[client_socket][1]
#                 if client_index in clients_data:
#                     del clients_data[client_index]

#             # del clients_data[clients_connected[client_socket][1]]
#             del clients_connected[client_socket]
#             client_socket.close()
#             break
#         except ConnectionAbortedError:
#             print(f"{clients_connected[client_socket][0]} disconnected unexpectedly.")

#             for client in clients_connected:
#                 if client != client_socket:
#                     client.send('notification'.encode())
#                     data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} left the chat",
#                                          'id': clients_connected[client_socket][1], 'n_type': 'left'})
#                     data_length_bytes = struct.pack('i', len(data))
#                     client.send(data_length_bytes)
#                     client.send(data)

#             del clients_data[clients_connected[client_socket][1]]
#             del clients_connected[client_socket]
#             client_socket.close()
#             break

#         for client in clients_connected:
#             if client != client_socket:
#                 client.send('message'.encode())
#                 client.send(data_bytes)


# connection_requests()


import socket
import threading
import pickle
import struct

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.clients = {}
        self.client_id = 1
        self.lock = threading.Lock()

    def start(self):
        print("Server started. Waiting for connections...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.lock.acquire()
            self.clients[self.client_id] = (client_socket, client_address)
            self.lock.release()
            print(f"New connection: {client_address[0]}:{client_address[1]}")
            threading.Thread(target=self.client_thread, args=(client_socket, self.client_id)).start()
            self.client_id += 1

    def client_thread(self, client_socket, client_id):
        client_socket.send("allowed".encode('utf-8'))

        self.send_clients_data(client_socket)

        client_name = client_socket.recv(1024).decode('utf-8')
        print(f"{client_name} connected as user no. {client_id}")

        self.broadcast_notification(f"{client_name} joined the chat.", client_id, client_name, 'joined')

        while True:
            try:
                data_bytes = client_socket.recv(1024)
                if not data_bytes:
                    break
                data = pickle.loads(data_bytes)
                self.broadcast_message(data['message'], client_id)

            except ConnectionResetError:
                break

        self.lock.acquire()
        del self.clients[client_id]
        self.lock.release()

        self.broadcast_notification(f"{client_name} left the chat.", client_id, client_name, 'left')
        client_socket.close()

    def send_clients_data(self, client_socket):
        clients_data = {}
        for client_id, (socket, address) in self.clients.items():
            clients_data[client_id] = {
                'address': address[0],
                'port': address[1]
            }
        clients_data_bytes = pickle.dumps(clients_data)
        clients_data_size_bytes = struct.pack('i', len(clients_data_bytes))
        client_socket.send(clients_data_size_bytes)
        client_socket.sendall(clients_data_bytes)

    def broadcast_message(self, message, from_client_id):
        data = {'from': from_client_id, 'message': message}
        data_bytes = pickle.dumps(data)

        self.lock.acquire()
        for client_id, (client_socket, _) in self.clients.items():
            if client_id != from_client_id:
                client_socket.send(data_bytes)
        self.lock.release()

    def broadcast_notification(self, message, client_id, name, n_type):
        data = {'id': client_id, 'name': name, 'message': message, 'n_type': n_type}
        data_bytes = pickle.dumps(data)
        data_size = struct.pack('i', len(data_bytes))

        self.lock.acquire()
        for _, (client_socket, _) in self.clients.items():
            client_socket.send('notification'.encode())
            client_socket.send(data_size)
            client_socket.sendall(data_bytes)
        self.lock.release()

    def stop(self):
        self.server_socket.close()
        print("Server stopped.")

if __name__ == "__main__":
    server = Server("192.168.43.69", 5050)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()