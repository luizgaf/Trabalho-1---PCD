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
                    print(f"Porta {port} alocada para novo cliente")
                    return port
        print("Todas as portas estão ocupadas")
        return None

    def release_port(self, port):
        with self.port_lock:
            self.ports[port] = True
            print(f"Porta {port} liberada")

    def get_seats_list(self):
        with self.lock:
            seats_list = []
            for row in "ABCDEFGHIJ":
                row_seats = []
                for col in range(1, 11):
                    seat = f"{row}{col}"
                    row_seats.append(seat if not self.seats[seat] else "--")
                seats_list.append(" ".join(row_seats))
            return "\n".join(seats_list)

    def handle_client(self, client_sock, port):
        try:
            print(f"\n[Cliente conectado] Porta: {port}")
            welcome_msg = "Bem-vindo ao cinema\nFILME: VINGADORES\n"
            seats_display = self.get_seats_list()
            full_msg = welcome_msg + "Assentos:\n" + seats_display + "\n"
            client_sock.sendall(full_msg.encode('utf-8'))
            print(f"[Mapa enviado] Para cliente na porta {port}")

            while True:
                data = client_sock.recv(2048).decode('utf-8').strip()
                if not data:
                    print(f"[Cliente desconectado] Porta: {port}")
                    break

                print(f"[Solicitação recebida] Porta {port}: {data}")

                if data.lower() == 'sair':
                    print(f"[Cliente encerrou] Porta: {port}")
                    break
                elif data.lower() == 'listar':
                    seats_display = self.get_seats_list()
                    client_sock.sendall(("Assentos:\n" + seats_display + "\n").encode('utf-8'))
                    print(f"[Mapa reenviado] Para porta {port}")
                else:
                    response = self.reserve_seat(data)
                    seats_display = self.get_seats_list()
                    full_response = response + "\nAssentos:\n" + seats_display + "\n"
                    client_sock.sendall(full_response.encode('utf-8'))
                    print(f"[Reserva processada] Porta {port}: {data} - {response}")

        except Exception as e:
            print(f"[Erro] Porta {port}: {e}")
        finally:
            client_sock.close()
            self.release_port(port)

    def reserve_seat(self, seat):
        with self.lock:
            seat = seat.upper()
            if seat in self.seats:
                if not self.seats[seat]:
                    self.seats[seat] = True
                    print(f"[Assento reservado] {seat}")
                    return f"Assento {seat} reservado com sucesso!"
                else:
                    print(f"[Tentativa de reserva] {seat} já ocupado")
                    return f"Assento {seat} já está ocupado."
            else:
                print(f"[Assento inválido] Tentativa: {seat}")
                return f"Assento {seat} inválido."

    def start_port_distributor(self):
        distributor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        distributor.bind(('0.0.0.0', 5000))
        distributor.listen(10)

        print("\n=== Servidor Iniciado ===")
        print("Distribuidor principal na porta 5000")

        try:
            while True:
                client_sock, addr = distributor.accept()
                print(f"\n[Nova conexão] Endereço: {addr}")

                port = self.get_available_port()
                if port:
                    client_sock.sendall(str(port).encode())
                    client_sock.close()
                    print(f"[Redirecionamento] Cliente enviado para porta {port}")

                    server_thread = threading.Thread(target=self.start_server, args=(port,))
                    server_thread.daemon = True
                    server_thread.start()
                else:
                    client_sock.sendall(b"Servidor cheio. Tente novamente mais tarde.")
                    client_sock.close()
                    print("[Servidor cheio] Cliente rejeitado")

        except KeyboardInterrupt:
            print("\n=== Encerrando servidor ===")
        finally:
            distributor.close()

    def start_server(self, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', port))
        server.listen(5)

        print(f"Servidor secundário iniciado na porta {port}")

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