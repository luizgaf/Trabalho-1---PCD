import socket
import threading



def client_handle(client_sock, port):
    try:
        print(f"Conexão estabelecida porta {port}")
        client_sock.sendall(f"Bem vido ao cinema\nFILME: VINGADORES\nCadeiras Disponíveis: A1, B4, C7, J10".encode('utf-8'))
        while True:

            data = client_sock.recv(2048)
            if not data:
                break
            print(f"\n{port}: {data.decode('utf-8')}")
            teste = str(input("\n"))
            client_sock.sendall(teste.encode('utf-8'))
        
    except KeyboardInterrupt:
        print("Finalizado")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client_sock.close()

def server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    print(f"Listening na Porta: {port} \n")

    try:
        while True:
            client_sock, port = server.accept()
            print(f"Conexão aceita: na porta {port}")
            client_handle(client_sock, port)
    except KeyboardInterrupt:
        print(f"Encerrando Conexão na porta {port}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.close()

def ports_distrib():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5000))
    server.listen((10)) # backlog

    ports = {
            5001:True,
            5002:True,
            5003:True,
            5004:True,
            5005:True
    }

    try:
        while True:
            client_sock, portClient = server.accept()
            print(f"Conexão aceita: da porta {portClient}")
            port = int()
            for port, status in ports.items():
                if status == True:
                    port = port
                    break

            client_sock.sendall(str(port).encode())
            server(port)
    finally:
        print("Ok")
    

if __name__ == "__main__":
    ports_distrib()
