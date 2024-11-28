import os
from collections import OrderedDict
from typing import Any, Dict, List, Optional

import tomlkit
import typer
from core import ComponentManager

app = typer.Typer()


class Option:

    registry = {}
    section: str
    name: str
    default: Any

    @staticmethod
    def get_registry(compmgr: Optional[ComponentManager] = None):
        return _get_registry(Option, compmgr)

    def __init__(self, section: str, name: str, default: Any = None, doc=''):
        self.section = section
        self.name = name
        self.default = default
        self.registry[(self.section, self.name)] = self
        self.__doc__ = doc  # TODO cleandoc

    def __get__(self, obj: 'Option', option_type=None):
        if obj is None:
            return self
        config = getattr(obj, 'config', None)
        if config and isinstance(config, Configuration):
            value = config.get(self.section, self.name)
            return self.transform(value, config=config)
        return None

    def __set__(self, obj: 'Option', value):
        obj.config.set(self.section, self.name, value)

    def __repr__(self):
        return f"{self.__class__.__name__, self.section, self.name}"

    def transform(self, value, config=None):
        return value

    def dumps(self, value) -> str:
        if value is None:
            return ''
        elif value is True:
            return 'enabled'
        elif value is False:
            return 'disabled'
        else:
            return value

    def get_file_path(self, config=None):
        if config and config.has_option(self.section, self.name):
            for file in config.filenames:
                with open(file, 'rb') as toml:
                    doc = tomlkit.parse(toml)
                    if self.section in doc.keys():
                        if self.name in doc[self.section].keys():
                            return file
        return config.filename


class Configuration():

    filename: str
    filenames: List[str]
    params: Dict[str, Any]

    def __init__(self, filename: str, params: Dict[str, Any] = None, create=False):
        # TODO set logging
        self.params = params or {}
        self.filename = os.path.abspath(os.path.normpath(filename))
        with open(filename, 'rb') as toml:
            self.doc = tomlkit.parse(toml)

    def __contains__(self, index: str):
        return index in self.doc.keys()

    def __getitem__(self, name: str):
        return self.doc[name]

    def __repr__(self):
        return f"{self.__class__.__name__} {self.filename}"

    def get(self, section: str, key: str, default=''):
        return self[section].get(key, default)

    def get_bool(self, section: str, key: str, default=''):
        return self[section].get_bool(key, default)

    def set(self, section: str, key: str, value):
        self.doc[section][key] = value

    def defaults(self, compmgr: Optional[ComponentManager] = None):
        defaults = OrderedDict()
        default_config = Option.get_registry(compmgr)
        for (section, key) in sorted(default_config):
            option = default_config[(section, key)]
            defaults.setdefault(section, OrderedDict())[key] = option.default
        return defaults

    def options(self, section: str, compmgr: Optional[ComponentManager] = None):
        for option in self[section].options(compmgr):
            yield option

    def remove(self, section: str, key: str):
        self[section].remove(key)

    def section(self, compmgr: Optional[ComponentManager] = None, defaults=True):
        sections = {s.strip() if isinstance(s, str) else str(s)
                    for s in self.doc.keys()}
        if defaults:
            sections.update(self.defaults(compmgr))
        return sections

    def has_option(self, section: str, option: str, defaults=True):
        if section in self.doc.keys():
            if option in self.doc[section].keys():
                return True
        return defaults and (section, option) in Option.registry

    def save(self):
        if not self.filename:
            return
        with open(self.filename, 'w') as toml:
            tomlkit.dump(self.doc, toml)

    def parse(self):
        pass

    def get_additional_configs(self, file: str):
        section = 'inherit'
        option = 'file'
        files = None

        self.filenames.append(file)

    def get_bool(self, section, key, default=False):
        value = self[section].get(key, default)
        return tomlkit.boolean(value)


def _get_registry(cls, compmgr: Optional[ComponentManager] = None):
    if not compmgr:
        return cls.registry
    from sparky.core import ComponentMeta
    components = {}
    for comp in ComponentMeta._components:
        for attr in comp.__dict__.itervalues():
            if isinstance(attr, cls):
                components[attr] = comp
    return dict(each for each in cls.registry.items() if each[1] not in components or compmgr.is_component_enabled(components[each[1]]))


class BoolOption(Option):
    pass


class IntOption(Option):
    pass


class PathOption(Option):
    pass


@app.command()
def set():
    pass


@app.command()
def list():
    pass


@app.command()
def remove():
    pass
