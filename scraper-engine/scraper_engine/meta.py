import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from uiclasses import DataBag, UserFriendlyObject

from scraper_engine.exceptions import ConfigMissing
from scraper_engine.util import load_json, load_yaml

logger = logging.getLogger(__name__)


class ConfigProperty(UserFriendlyObject):
    name: str
    path: List[str]
    env: str
    default_value: Any
    deserialize: callable

    def __init__(self, *path: List[str], **kw):
        name = kw.pop("name", None)
        env = kw.pop("env", None)
        default_value = kw.pop("default_value", kw.pop("default", None))

        deserialize = kw.pop("deserialize", None)
        if deserialize:
            self.deserialize = deserialize
        else:
            self.deserialize = lambda x: x

        if not path and not env:
            raise SyntaxError(
                f"ConfigProperty requires at least one path name, or a env keyword-arg"
            )
        for k, v in dict(
            name=name or env,
            path=list(path),
            env=env,
            default_value=default_value,
            **kw,
        ).items():
            setattr(self, k, v)

    def resolve(self, config: DataBag, file_path: Optional[Path]):
        name = self.name or self.env
        attr = ".".join(self.path)
        value = None

        if not value and self.env:
            value = os.getenv(self.env)
            if value:
                logger.debug(f"resolved {name} via env var {self.env}")

        if not value and self.path:
            value = config.traverse(*self.path)
            if value:
                logger.debug(f"resolved {name} via config path {attr}")

        if not value and self.default_value is not None:
            value = self.default_value
            if value:
                logger.debug(f"resolved {name} to its default value {value}")

        if value is None:
            raise ConfigMissing(
                attr,
                file_path,
                self.env,
            )

        try:
            return self.deserialize(value)
        except Exception as e:
            logger.warning(
                f"failed to deserialize value {value} with {self.deserialize}: {e}"
            )
            return value


class MetaConfig(type):
    def __new__(cls, name, bases, attributes):
        config_properties = dict(
            [(k, v) for k, v in attributes.items() if isinstance(v, ConfigProperty)]
        )
        attributes["__fields__"] = config_properties
        return type.__new__(cls, name, bases, attributes)
        return cls


class BaseConfig(DataBag, metaclass=MetaConfig):
    """base class to the global config that automatically loads values
    from environment variables first, then falls back to yaml config or default values.
    """

    def __init__(
        self,
        path=None,
        path_location_env_var="SCRAPER_ENGINE_CONFIG_PATH",
        default_path="~/.drone-ci-butler.yml",
    ):
        self.path = (
            Path(path or os.getenv(path_location_env_var) or default_path)
            .expanduser()
            .absolute()
        )
        self.__data__ = {}
        self.__data__.update(self.resolve_values(self.path))
        logger.debug("config loaded")

    def to_env_vars(self) -> Dict[str, str]:
        env = {}
        for field in self.__fields__.values():
            if field.env:
                env[field.env] = self.resolve_property(field, data=dict(self))
        return env

    def to_shell_env_declaration(self) -> str:
        parts = [
            f"{key}={value}"
            for key, value in sorted(self.to_env_vars().items(), key=lambda kv: kv[0])
        ]
        return "\n".join(parts)

    def to_docker_env_declaration(self) -> str:
        parts = [
            f"ENV {key} {value}"
            for key, value in sorted(self.to_env_vars().items(), key=lambda kv: kv[0])
        ]
        return "\n".join(parts)

    def resolve_property(
        self,
        field: ConfigProperty,
        name: Optional[str] = None,
        data: DataBag = None,
        fail: bool = False,
    ) -> Any:
        name = name or field.name
        container = DataBag(data or {})
        try:
            value = field.resolve(container, file_path=self.path)
        except Exception as e:
            if fail:
                raise
            value = field.default_value

        if field.env:
            container[field.env] = value

        if name:
            container[name] = value

        # resolve nested value
        for attr in field.path[:-1]:
            if not container.get(attr):
                container[attr] = {}

        last = field.path[-1]
        container[last] = value
        return value

    def resolve_values(self, path: Path) -> Dict[str, Any]:
        data = load_yaml(path)
        for name, field in self.__fields__.items():
            value = self.resolve_property(field, name, data=data)
            setattr(self, name, value)
            logger.debug(f"[config] resolved property {name}")

        return data
