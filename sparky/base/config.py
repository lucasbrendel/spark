import os
from typing import Any, Dict, List, Optional, Type, Union
import tomlkit
from base.module import ModuleManager

class Configuration:

    def __init__(self, filename: str, params={}):
        self.filename = filename
        self.params = params
        self.parents = self._get_parents()
        self._sections = {}
        with open(filename, 'r') as doc:
            self.doc = tomlkit.parse(doc.read())

    def __getitem__(self, name: str) -> 'Section':
        if name not in self._sections:
            self._sections[name] = Section(self, name)
        return self._sections[name]

    def __delitem__(self, name: str):
        self._sections.pop(name, None)
        self.doc.remove(name)

    def __contains__(self, name: str):
        return name in self.sections()

    def get(self, section, key, default=''):
        return self[section].get(key, default)

    def set(self, section, key, value):
        self[section][key] = value

    def defaults(self, modmgr: ModuleManager = None):
        defaults = {}
        for (section, key), option in Option.get_registry(modmgr).items():
            defaults.setdefault(section, {})[key] = option.default
        return defaults

    def options(self, section: str, modmgr: ModuleManager = None) -> List['Option']:
        return self[section].options(modmgr)

    def remove(self, section: str, key: Optional[str] = None):
        if key:
            self[section].remove(key)
        else:
            del self[section]

    def sections(self, modmgr: ModuleManager = None, defaults=True, empty=False) -> List['Section']:
        sections = set(self.doc.keys())
        for parent in self.parents:
            sections.update(parent.sections(modmgr, defaults=False))
        if defaults:
            sections.update(self.defaults(modmgr))
        if empty:
            sections.update(ConfigSection.get_registry(modmgr))
        return sorted(sections)

    def has_option(self, section: str, option: str, defaults=True):
        return self[section].contains(option, defaults)

    def save(self):
        options = {}
        for (section, name), option in Option.get_registry().items():
            options.setdefault(section, {})[name] = option

        sections = []
        for section in self.sections():
            options = []
            for option in self[section]:
                default = None
                for parent in self.parents:
                    if parent.has_option(section, option, defaults=False):
                        default = parent.get(section, option)
                        break
                if self.has_option(section, option):
                    current = self.get(section, option)
                    if current != default:
                        options.append((option, current))
            if options:
                sections.append((section, sorted(options)))

            for section, options in sections:
                self.doc[section] = {}
                for option, value in options:
                    self.doc[section][option] = value

            with open(self.filename, 'w') as file:
                file.write(tomlkit.dumps(self.doc))

    def set_defaults(self, modmgr: ModuleManager = None, module: Optional[str] = None):
        def set_option_default(option: Option):
            section = option.section
            name = option.name
            if not self.has_option(section, name, defaults=False):
                value = option.default
                self.set(section, name, value)
        if module:
            if module.endswith(".*"):
                module = module[:-2]
            module = module.lower().split(".")
            from base.module import ModuleMeta
            for cls in ModuleMeta._modules:
                clsname = (cls.__module__ + '.' +
                           cls.__name__).lower().split('.')
                if clsname[:len(module)] == module:
                    for option in cls.__dict__.values():
                        if isinstance(option, Option):
                            set_option_default(option)
        else:
            for option in Option.get_registry(modmgr).values():
                set_option_default(option)

    def _get_parents(self) -> List['Configuration']:
        _parents = []
        section = 'inherit'
        key = 'file'
        if section in self.doc.keys():
            if key in self.doc[section]:
                for filename in self.doc[section][key]:
                    if not os.path.isabs(filename):
                        filename = os.path.join(
                            os.path.dirname(self.filename), filename)
                    _parents.append(Configuration(filename))
        return _parents

    def getbool(self, section, key, default=None):
        return bool(self[section].get(key, default))


class Section:

    def __init__(self, config: Configuration, name: str):
        self.config = config
        self.name = name

    def __repr__(self):
        return f"<{self.__class__.__name__} [{self.name}]>"

    def contains(self, key, defaults=True):
        pass


class ConfigSection:

    registry = {}

    def __init__(self, name: str, doc: str):
        self.name = name
        self.__doc__ = doc

    @staticmethod
    def get_registry(modmgr: ModuleManager = None):
        return _get_registry(ConfigSection, modmgr)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        config = getattr(instance, 'config', None)
        if config and isinstance(config, Configuration):
            return config[self.name]

    def __repr__(self):
        return f"<{self.__class__.__name__[{self.name}]}"

    @property
    def doc(self):
        return self.__doc__


class Option:

    registry = {}

    def accessor(self, section: Dict[str, Dict[str, Any]], name: str, default):
        return section.get(name, default)

    @staticmethod
    def get_registry(modmgr: ModuleManager = None):
        return _get_registry(Option, modmgr)

    def __init__(self, section: str, name: str, default=None, doc=''):
        self.section = section
        self.name = name
        self.default = default
        self.__doc__ = doc
        self.registry[(self.section, self.name)] = self

    def __get__(self, instance, owner):
        if instance is None:
            return self
        config = getattr(instance, 'config', None)
        if config and isinstance(config, Configuration):
            section = config[self.section]
            value = self.accessor(section, self.name, self.default)
            return value

    def __set__(self, instance, value):
        raise AttributeError("Setting attribute is not allowed.")

    def __repr__(self):
        return f"<{self.__class__.__name__} [{self.section}] {self.name}>"

    @property
    def doc(self):
        return self.__doc__


def _get_registry(cls: Union[Type[Option], Type[ConfigSection]], modmgr: ModuleManager = None):
    """Get registered items.

    Args:
        cls (Union[Type[Option], Type[ConfigSection]]): Class of registered items to return
        modmgr (ModuleManager, optional): If not None then only return instances from modules that are enabled. Defaults to None.

    Returns:
        Dict: Dictionary of registered items
    """
    if modmgr is None:
        return cls.registry

    from base.module import ModuleMeta
    modules = {}
    for mod in ModuleMeta._modules:
        for attr in mod.__dict__.values():
            if isinstance(attr, cls):
                modules[attr] = mod
    return dict(each for each in cls.registry.items() if each[1] not in modules or modmgr.is_module_enabled(modules[each[1]]))


class BoolOption(Option):
    pass


class IntOption(Option):
    pass


class PathOption(Option):
    pass
