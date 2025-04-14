import socket

def get_port():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        print("Conectando ao servidor principal...")
        client_sock.connect(('127.0.0.1', 5000))
        port = int(client_sock.recv(1024).decode())
        client_sock.close()
        print(f"Redirecionado para porta {port}")
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
        print(f"Conectando à porta {port}...")
        client_sock.connect(('127.0.0.1', port))
        print("Conexão estabelecida com sucesso!\n")
        
        while True:
            data = client_sock.recv(2048).decode()
            
            # Separa a mensagem de status do mapa de assentos
            if "\nAssentos:\n" in data:
                status_msg, seats_display = data.split("\nAssentos:\n")
                if status_msg.strip():  # Mostra mensagem de status se existir
                    print("\n" + "="*40)
                    print(status_msg.strip())
                    print("="*40 + "\n")
            else:
                seats_display = data
            
            # Exibe os assentos
            if "Assentos:" in data or seats_display:
                print("="*40)
                print("  TELA DO CINEMA  ")
                print("="*40)
                print("\nAssentos disponíveis (-- = ocupado):\n")
                print(seats_display.strip())
                print("\n" + "="*40 + "\n")
            
            # Mostra comandos disponíveis
            print("\nComandos disponíveis:")
            print("1. Digite o número do assento (ex: B5)")
            print("2. 'listar' - Atualizar assentos")
            print("3. 'sair' - Encerrar\n")
            
            command = input("Digite o número do assento ou comando: ").strip().upper()
            client_sock.sendall(command.encode())
            
            if command.lower() == 'sair':
                print("Saindo do sistema...")
                break

    except KeyboardInterrupt:
        print("\nInterrupção recebida. Encerrando cliente...")
        client_sock.sendall(b'sair') 
    except Exception as e:
        print(f"\nErro durante a conexão: {e}")
    finally:
        client_sock.close()
        print("Conexão encerrada")

if __name__ == "__main__":
    print("=== CLIENTE DO CINEMA ===")
    cinema_client()