import importlib
import pkgutil
import logging
from core.interfaces.plugin import WiFiPlugin

class PluginLoader:
    """
    Carga dinámica de plugins desde el paquete 'modules'.
    """

    def __init__(self, plugins_package: str = 'modules'):
        self.plugins_package = plugins_package
        self.log = logging.getLogger(self.__class__.__name__)

    def load_plugins(self) -> list[WiFiPlugin]:
        plugins: list[WiFiPlugin] = []
        try:
            package = importlib.import_module(self.plugins_package)
        except ImportError as e:
            self.log.error(f"No se encontró el paquete de plugins '{self.plugins_package}': {e}")
            return plugins

        for finder, name, ispkg in pkgutil.iter_modules(package.__path__):
            if ispkg:
                continue
            module_name = f"{self.plugins_package}.{name}"
            try:
                module = importlib.import_module(module_name)
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, type) and issubclass(obj, WiFiPlugin) and obj is not WiFiPlugin:
                        instance = obj()
                        plugins.append(instance)
                        self.log.info(f"Plugin cargado: {obj.__name__}")
            except Exception as e:
                self.log.error(f"Fallo cargando plugin '{name}': {e}")
        return plugins