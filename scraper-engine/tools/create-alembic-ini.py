import os
import socket
from pathlib import Path

path_to_module = Path(__file__).joinpath("..", "scraper_engine").absolute()


POSTGRES_HOST = socket.gethostbyname(os.getenv("POSTGRES_HOST") or "localhost")
POSTGRES_USER = os.getenv("POSTGRES_USER") or "scraper_engine"
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD") or "scraper_engine"
POSTGRES_DB = os.getenv("POSTGRES_DB") or "scraper_engine"

SQLALCHEMY_URI = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
)
ALEMBIC_CONFIG = os.getenv("ALEMBIC_CONFIG")
socket.gethostbyname


if not SQLALCHEMY_URI:
    print(f"the environment variable SQLALCHEMY_URI is not set")
    raise SystemExit(1)

if not ALEMBIC_CONFIG:
    print(f"the environment variable ALEMBIC_CONFIG is not set")
    raise SystemExit(1)

path_to_alembic_config = Path(ALEMBIC_CONFIG)
path_to_alembic_config.parent.mkdir(parents=True, exist_ok=True)

config = f"""
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = migrations

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = {path_to_module}

# timezone to use when rendering the date
# within the migration file as well as the filename.
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; this defaults
# to migrations/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path
# version_locations = %(here)s/bar %(here)s/bat migrations/versions

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = {SQLALCHEMY_URI}


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

if path_to_alembic_config.exists():
    print(f"WARNING: overwriting {path_to_alembic_config}")
elif path_to_alembic_config.is_dir():
    print(
        f"ERROR: the env var ALEMBIC_CONFIG points to {path_to_alembic_config} "
        "which is a directory rather than a file"
    )
    raise SystemExit(1)
else:
    print(f"INFO: creating file {path_to_alembic_config}")

with path_to_alembic_config.open("w") as fd:
    fd.write(config.strip())
