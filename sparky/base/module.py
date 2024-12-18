import sys
from typing import Dict, List, Optional
from logging import Logger
# from config import Configuration

class Interface():
    pass


class PluginPoint(property):

    interface: Interface

    def __init__(self, interface: Interface):
        property.__init__(self, self.extensions)
        self.interface = interface

    def extensions(self, module: 'Module'):
        classes = ModuleMeta._registry.get(self.interface, ())
        modules = [module.modmgr[cls] for cls in classes]
        return [c for c in modules if c]

    def __repr__(self):
        return f"<PluginPoint {self.interface.__name__}>"


class ModuleMeta(type):
    _modules: List['Module'] = []
    _registry: Dict[Interface, 'Module'] = {}

    def __new__(mcs, name: Optional[str] = None, bases=None, attributes=None):
        new_class = super().__new__(mcs, name, bases, attributes)
        if name == "Module":
            return new_class
        if attributes.get('abstract'):
            return new_class

        ModuleMeta._modules.append(new_class)

        registry = ModuleMeta._registry
        for cls in new_class.__mro__:
            for interface in cls.__dict__.get("implements", ()):
                classes = registry.setdefault(interface, [])
                if new_class not in classes:
                    classes.append(new_class)
        return new_class

    def __call__(cls, *args, **kwds):
        if issubclass(cls, ModuleManager):
            self = cls.__new__(cls)
            self.modmgr = self
            self.__init__(*args, **kwds)
            return self

        modmgr = args[0]
        self = modmgr.modules.get(cls)
        if self is None:
            self = cls.__new__(cls)
            self.modmgr = modmgr
            modmgr.module_activated(self)
            self.__init__()
            modmgr.modules[cls] = self
        return self


class Module(metaclass=ModuleMeta):

    # env: Environment = None
    config = None
    log: Logger = None

    @property
    def fqname(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}"

    @staticmethod
    def implements(*interfaces):
        frame = sys._getframe(1)
        locals = frame.f_locals

        in_class_def = locals is not frame.f_globals and '__module__' in locals
        if not in_class_def:
            raise Exception(
                "implements() can only be used in a class definition")

        locals.setdefault('_implements', []).extend(interfaces)


implements = Module.implements


class ModuleManager:

    modules: Dict[type, Module] = {}
    enabled: Dict[Module, bool] = {}

    def __init__(self):
        if isinstance(self, Module):
            self.modules[self.__class__] = self

    def __contains__(self, cls: Module):
        return cls in self.modules

    def __getitem__(self, cls: Module):
        if not self.is_enabled(cls):
            return None

        module = self.modules.get(cls)
        if not module:
            if cls not in ModuleMeta._modules:
                raise Exception(f"Module {cls.__name__} is not registered")
            try:
                module = cls(self)
            except TypeError as e:
                raise Exception(f"Unable to create module ({cls}): {e}")

        return module

    def is_enabled(self, cls: Module):
        if cls not in self.enabled:
            self.enabled[cls] = self.is_module_enabled(cls)
        return self.enabled[cls]

    def disable_module(self, module: Module):
        if not isinstance(module, type):
            module = module.__class__
        self.enabled[module] = False
        self.modules[module] = None

    def module_activated(self, module: Module):
        """Can be overriden for special init"""

    def is_module_enabled(self, _cls: Module):
        return True
