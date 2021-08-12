import json
import logging
import re
from hashlib import sha1
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from chemist import Model as SQLModel
from uiclasses import Model as UIModel

logger = logging.getLogger(__name__)

GITHUB_PULL_REQUEST_REGEX = re.compile(
    r"github.com[/](?P<owner>[^/]+)[/](?P<repo>[^/]+)[/]pull[/](?P<pr_number>\d+)"
)


def prefix_dict_keys(doc: dict, key_prefix: Optional[str] = None):
    if isinstance(key_prefix, str) and len(key_prefix) > 0:
        for key in list(doc.keys()):
            doc[f"{key_prefix}_{key}"] = doc.pop(key)

    return doc


def get_config():
    from scraper_engine.config import config

    return config


def regex_match_to_dict(match: re.Match) -> dict:
    data = {}
    data["regex"] = regex_pattern_to_dict(match.re)
    data["pos"] = match.pos
    data["regs"] = match.regs
    data["string"] = match.string
    data["named_groups"] = match.groupdict()
    data["groups"] = match.groups()
    data["match"] = match.group()
    return data


def regex_pattern_to_dict(regex: re.Pattern) -> dict:
    data = {
        "pattern": regex.pattern,
        "flags": regex.flags,
    }
    return data


def try_parse_github_pull_request_url(url) -> Dict[str, str]:
    found = GITHUB_PULL_REQUEST_REGEX.search(url or "")
    if found:
        return found.groupdict()
    return {}


def try_parse_github_pull_request_number(url) -> Optional[int]:
    number = try_parse_github_pull_request_url(url).get("pr_number")
    if isinstance(number, str) and len(number) > 0:
        return int(number)


def slugify(value: str, repchar="-") -> str:
    return re.sub(r"\W+", repchar, value)


def ensure_json_serializable(obj):
    if isinstance(obj, (SQLModel, UIModel)):
        return obj.to_dict()

    if isinstance(obj, re.Match):
        return regex_match_to_dict(obj)

    if isinstance(obj, re.Pattern):
        return regex_pattern_to_dict(obj)

    return str(obj)


def dict_of_strings(data: dict) -> Dict[str, str]:
    result = {}
    for key, value in data.items():
        if isinstance(key, bytes):
            key = key.decode("utf-8")

        if isinstance(value, bytes):
            value = value.decode("utf-8")
        elif not isinstance(value, str):
            value = json_encode(value)
        result[key] = value

    return result


def json_encode(value):
    return json.dumps(value, default=ensure_json_serializable)


def unpacked_dict_of_strings(data: dict) -> Dict[str, Any]:
    result = {}
    for key, value in data.items():
        if isinstance(key, bytes):
            key = key.decode("utf-8")
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        result[key] = load_json(value, value)

    return result


def load_json(what, default=None) -> str:
    if isinstance(what, bytes):
        what = what.decode("utf-8")
    try:
        return json.loads(what or "{}") or default
    except (json.JSONDecodeError):
        return default


def load_yaml(path: Path) -> dict:
    try:
        path = path.expanduser().absolute()
        with path.open() as fd:
            return yaml.load(fd, Loader=yaml.FullLoader)
    except Exception as e:
        logger.warning(f"failed to load path {path}: {e}")
        return {}


def parse_bool(thing) -> bool:
    if not isinstance(thing, (str, bytes)):
        return bool(thing)

    if isinstance(thing, bytes):
        thing = thing.decode("utf-8")

    value = thing.lower().strip()
    if value == "no":
        return False

    if value == "yes":
        return True

    obj = load_json(value)
    return bool(obj)


def sha1_encode(value: Union[str, int]) -> str:
    return sha1(str(value).encode()).hexdigest()


def try_int(value: Union[str, int]) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return
