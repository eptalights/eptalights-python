from importlib.metadata import version

from eptalights.core.loader import LoaderAPI
from eptalights.core.db import DatabaseAPI
from eptalights.core.api import LocalAPI, RemoteAPI


__version__ = version("eptalights-python")

__all__ = [
    "LocalAPI",
    "RemoteAPI",
    "DatabaseAPI",
    "LoaderAPI",
]
