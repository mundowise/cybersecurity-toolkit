from abc import ABC, abstractmethod


class WiFiPlugin(ABC):
    """
    Interfaz base para plugins de WiFiNetScanner.
    """

    @abstractmethod
    def register(self, scanner) -> None:
        """
        Registra el plugin en una instancia de WiFiScanner.
        El plugin puede añadir hooks, comandos o procesar eventos.
        """
        pass