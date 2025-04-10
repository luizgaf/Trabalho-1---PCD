import socket
import threading

class CinemaServer:
    def __init__(self):
        self.seats = {f"{row}{col}": False for row in "ABCDEFGHIJ" for col in range(1, 11)}
        self.lock = threading.Lock()
        self.ports = {5001: True, 5002: True, 5003: True, 5004: True, 5005: True}
        self.port_lock = threading.Lock()

    def get_available_port(self):
        with self.port_lock:
            for port, available in self.ports.items():
                if available:
                    self.ports[port] = False
                    return port
        return None

    def release_port(self, port):
        with self.port_lock:
            self.ports[port] = True

    def get_seats_matrix(self):
        with self.lock:
            matrix = []
            # Cabeçalho com apenas 1 espaço entre os números
            header = "   " + " ".join(str(i) for i in range(1, 11))
            matrix.append(header)
            
            for row in "ABCDEFGHIJ":
                row_line = f"{row} |"
                for col in range(1, 11):
                    seat = f"{row}{col}"
                    status = "X" if self.seats[seat] else "O"
                    row_line += f" {status}"
                matrix.append(row_line)
            return "\n".join(matrix)

    def handle_client(self, client_sock, port):
        try:
            print(f"Conexão estabelecida na porta {port}")
            welcome_msg = "Bem-vindo ao cinema\nFILME: VINGADORES\n"
            seats_display = self.get_seats_matrix()
            client_sock.sendall((welcome_msg + "Mapa de Assentos:\n" + seats_display + "\n").encode('utf-8'))

            while True:
                data = client_sock.recv(2048).decode('utf-8').strip()
                if not data:
                    break

                if data.lower() == 'sair':
                    break
                elif data.lower() == 'listar':
                    seats_display = self.get_seats_matrix()
                    client_sock.sendall(("Mapa de Assentos Atualizado:\n" + seats_display + "\n").encode('utf-8'))
                else:
                    response = self.reserve_seat(data)
                    seats_display = self.get_seats_matrix()
                    client_sock.sendall((response + "\nMapa de Assentos Atualizado:\n" + seats_display + "\n").encode('utf-8'))

        except Exception as e:
            print(f"Erro: {e}")
        finally:
            client_sock.close()
            self.release_port(port)
            print(f"Conexão encerrada na porta {port}")

    def reserve_seat(self, seat):
        with self.lock:
            if seat in self.seats:
                if not self.seats[seat]:
                    self.seats[seat] = True
                    return f"Assento {seat} reservado com sucesso!"
                else:
                    return f"Assento {seat} já está ocupado."
            else:
                return f"Assento {seat} inválido."

    def start_port_distributor(self):
        distributor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        distributor.bind(('0.0.0.0', 5000))
        distributor.listen(10)

        print("Distribuidor de portas rodando na porta 5000")

        try:
            while True:
                client_sock, addr = distributor.accept()
                print(f"Conexão aceita de {addr}")

                port = self.get_available_port()
                if port:
                    client_sock.sendall(str(port).encode())
                    client_sock.close()

                    server_thread = threading.Thread(target=self.start_server, args=(port,))
                    server_thread.daemon = True
                    server_thread.start()
                else:
                    client_sock.sendall(b"Servidor cheio. Tente novamente mais tarde.")
                    client_sock.close()

        except KeyboardInterrupt:
            print("Encerrando distribuidor de portas")
        finally:
            distributor.close()

    def start_server(self, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', port))
        server.listen(5)

        print(f"Servidor de cinema rodando na porta {port}")

        try:
            while True:
                client_sock, addr = server.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_sock, port))
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print(f"Encerrando servidor na porta {port}")
        finally:
            server.close()

if __name__ == "__main__":
    cinema = CinemaServer()
    distributor_thread = threading.Thread(target=cinema.start_port_distributor)
    distributor_thread.daemon = True
    distributor_thread.start()
    distributor_thread.join()