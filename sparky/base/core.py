import sys
from typing import Dict, List, Optional

from sparky.base.config import Configuration
from sparky.base.env import Environment


class sparkyError(Exception):

    def __init__(self, message: Optional[str] = None, title: Optional[str] = None, show_traceback=False):
        super().__init__(self, message)
        self._message = message
        self.title = title or self.title
        self.show_traceback = show_traceback

    message = property(lambda self: self._message,
                       lambda self, v: setattr(self, '_message', v))


class Interface():
    pass


class ExtensionPoint(property):

    interface: Interface

    def __init__(self, interface: Interface):
        property.__init__(self, self.extensions)
        self.interface = interface

    def extensions(self, component: 'Component'):
        classes = ComponentMeta._registry.get(self.interface, ())
        components = [component.compmgr[cls] for cls in classes]
        return [c for c in components if c]

    def __repr__(self):
        return f"<ExtensionPoint {self.interface.__name__}>"


class ComponentMeta(type):
    _components: List['Component'] = []
    _registry: Dict[Interface, 'Component'] = {}

    def __new__(mcs, name: Optional[str] = None, bases=None, attributes=None):
        new_class = super().__new__(mcs, name, bases, attributes)
        if name == "Component":
            return new_class
        if attributes.get('abstract'):
            return new_class

        ComponentMeta._components.append(new_class)

        registry = ComponentMeta._registry
        for cls in new_class.__mro__:
            for interface in cls.__dict__.get("implements", ()):
                classes = registry.setdefault(interface, [])
                if new_class not in classes:
                    classes.append(new_class)
        return new_class

    def __call__(cls, *args, **kwds):
        if issubclass(cls, ComponentManager):
            self = cls.__new__(cls)
            self.compmgr = self
            self.__init__(*args, **kwds)
            return self

        compmgr = args[0]
        self = compmgr.components.get(cls)
        if self is None:
            self = cls.__new__(cls)
            self.compmgr = compmgr
            compmgr.component_activated(self)
            self.__init__()
            compmgr.components[cls] = self
        return self


class Component(metaclass=ComponentMeta):

    env: Environment = None
    config: Configuration = None
    log = None

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


implements = Component.implements


class ComponentManager:

    components: Dict[type, Component] = {}
    enabled: Dict[Component, bool] = {}

    def __init__(self):
        if isinstance(self, Component):
            self.components[self.__class__] = self

    def __contains__(self, cls: Component):
        return cls in self.components

    def __getitem__(self, cls: Component):
        if not self.is_enabled(cls):
            return None

        component = self.components.get(cls)
        if not component:
            if cls not in ComponentMeta._components:
                raise Exception(f"Component {cls.__name__} is not registered")
            try:
                component = cls(self)
            except TypeError as e:
                raise Exception(f"Unable to create component ({cls}): {e}")

        return component

    def is_enabled(self, cls: Component):
        if cls not in self.enabled:
            self.enabled[cls] = self.is_component_enabled(cls)
        return self.enabled[cls]

    def disable_component(self, component: Component):
        if not isinstance(component, type):
            component = component.__class__
        self.enabled[component] = False
        self.components[component] = None

    def component_activated(self, component: Component):
        """Can be overriden for special init"""

    def is_component_enabled(self, _cls: Component):
        return True
