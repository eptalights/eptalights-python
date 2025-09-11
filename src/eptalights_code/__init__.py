from importlib.metadata import version

from eptalights_code.core.loader import LoaderAPI
from eptalights_code.core.db import DatabaseAPI
from eptalights_code.core.api import LocalAPI, RemoteAPI


__version__ = version("eptalights-code-python")

__all__ = [
    "LocalAPI",
    "RemoteAPI",
    "DatabaseAPI",
    "LoaderAPI",
]
