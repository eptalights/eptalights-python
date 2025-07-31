from importlib.metadata import version

from eptalights_sophia.core.loader import LoaderAPI
from eptalights_sophia.core.db import DatabaseAPI
from eptalights_sophia.core.api import LocalAPI, RemoteAPI


__version__ = version("eptalights-sophia-python")

__all__ = [
    "LocalAPI",
    "RemoteAPI",
    "DatabaseAPI",
    "LoaderAPI",
]
