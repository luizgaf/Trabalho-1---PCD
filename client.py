import socket

def get_port():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_sock.connect(('127.0.0.1', 5000))
        port = int(client_sock.recv(1024).decode())
        client_sock.close()
        return port
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def cinema_client():
    port = get_port()
    if not port:
        print("Não foi possível obter uma porta do servidor")
        return

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_sock.connect(('127.0.0.1', port))
        
        while True:
            data = client_sock.recv(2048).decode()
            print(data)
            
            if "Mapa de Assentos" in data:  # Alterado aqui
                print("\nComandos disponíveis:")
                print("1. Digite o número do assento para reservar (ex: B5)")
                print("2. Digite 'listar' para ver assentos disponíveis")
                print("3. Digite 'sair' para encerrar a conexão\n")
            
            command = input("Digite seu comando: ").strip().upper()  # Adicionado upper()
            client_sock.sendall(command.encode())
            
            if command.lower() == 'sair':
                break

    except KeyboardInterrupt:
        print("\nEncerrando cliente...")
        client_sock.sendall(b'sair')  # Informa ao servidor que está saindo
    except Exception as e:
        print(f"\nErro durante a conexão: {e}")
    finally:
        client_sock.close()
        print("Conexão encerrada")

if __name__ == "__main__":
    cinema_client()