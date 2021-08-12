from typing import Optional

from uiclasses import Model

from scraper_engine.util import get_config


class UserFriendlyException(Exception):
    """subclasses of this exception *MUST* provide error messages that can
    be "printed" to the user without need for full traceback"""

    def __init__(self, *args, **kwargs):
        self.config = get_config()
        super().__init__(*args, **kwargs)

    def to_dict(self, only_visible: bool = False):
        data = {"message": str(self)}
        for key in dir(self):
            value = getattr(self, key, Optional)
            if value is Optional:
                continue
            if isinstance(value, Model):
                data[key] = value.to_dict(only_visible=only_visible)
        return data

    def to_log_dict(self, only_visible: bool = False):
        data = self.to_dict(only_visible=only_visible)
        data.pop("message", None)
        return data


class ConfigMissing(UserFriendlyException):
    def __init__(self, key, filename, env: str = None):
        env = ""
        if env:
            env = f" or from env var {env}"

        msg = f"Config key {key} missing from {filename}{env}"
        super().__init__(msg)


class InvalidYamlConfig(UserFriendlyException):
    """raised when a yaml config has an invalid value"""
