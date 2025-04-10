import socket

def redirect(port = 5000):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"Tentando Conexão porta: {port}")
        client_sock.connect(('127.0.0.1', port))
        print(f"Conexão na porta {port} estabelecida")

        while True:
            port = int((client_sock.recv(1024)).decode())
            return port

        
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Finalizando...")
    finally:
        client_sock.close()

def connect(port):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"Tentando Conexão porta: {port}")
        client_sock.connect(('127.0.0.1', port))
        print(f"Conexão na porta {port} estabelecida")

        while True:
            data = client_sock.recv(2048)
            print(f"\nServidor: {data.decode('utf-8')}")

            msg = str(input(f"\nCadeiras:"))
            client_sock.sendall(msg.encode('utf-8'))

        
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Finalizando...")
    finally:
        client_sock.close()

if __name__ == "__main__":
    connect(redirect()) # porta padra pra solicitar redirect
