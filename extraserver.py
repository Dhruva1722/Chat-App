import socket
import threading

clients = []
addresses = []

def handle_client(client_socket, address):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == 'exit':
                index = clients.index(client_socket)
                clients.remove(client_socket)
                client_socket.close()
                address = addresses[index]
                addresses.remove(address)
                print(f"Connection closed with {address}")
                broadcast_message(f"User {address} has left the chat.")
                break
            else:
                print(f"Received message from {address}: {message}")
                broadcast_message(message)
        except:
            index = clients.index(client_socket)
            clients.remove(client_socket)
            client_socket.close()
            address = addresses[index]
            addresses.remove(address)
            print(f"Connection closed with {address}")
            broadcast_message(f"User {address} has left the chat.")
            break

def broadcast_message(message):
    for client in clients:
        client.send(message.encode('utf-8'))

def start_server():
    host = 'localhost'
    port = 9999

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print("Server started. Waiting for connections...")

    while True:
        client_socket, address = server_socket.accept()
        print(f"New connection from {address}")
        clients.append(client_socket)
        addresses.append(address)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()

start_server()
