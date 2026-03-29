import psutil
import socket

def check_network_connections():
    """Imprime las conexiones de red activas."""
    print("\n--- Conexiones de Red Activas ---")
    try:
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            if conn.status == 'ESTABLISHED':
                print(f"  Proto: {conn.type}  Local: {conn.laddr.ip}:{conn.laddr.port}  Remoto: {conn.raddr.ip}:{conn.raddr.port}  Estado: {conn.status}  PID: {conn.pid}")
    except Exception as e:
        print(f"  Error al obtener conexiones de red: {e}")

def check_running_processes():
    """Imprime los procesos en ejecución."""
    print("\n--- Procesos en Ejecución ---")
    try:
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            print(f"  PID: {proc.info['pid']}  Nombre: {proc.info['name']}  Usuario: {proc.info['username']}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
    except Exception as e:
        print(f"  Error al obtener los procesos: {e}")


def scan_open_ports(target="127.0.0.1", start_port=1, end_port=1024):
    """Escanea los puertos abiertos en una dirección IP."""
    print(f"\n--- Escaneando Puertos Abiertos en {target} ---")
    try:
        for port in range(start_port, end_port + 1):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(1)
            result = sock.connect_ex((target, port))
            if result == 0:
                print(f"  Puerto {port}: Abierto")
            sock.close()
    except socket.error as e:
        print(f"  No se pudo conectar al host: {e}")
    except Exception as e:
        print(f"  Error al escanear puertos: {e}")


if __name__ == "__main__":
    print("Iniciando revisión de seguridad...")
    check_network_connections()
    check_running_processes()
    scan_open_ports()
    print("\nRevisión de seguridad básica completada.")