from eptalights.core.db import DatabaseAPI
from eptalights.core.loader import LoaderAPI


class LocalAPI(DatabaseAPI, LoaderAPI):
    def __init__(self, config_path: str, connect_db: bool = True):
        LoaderAPI.__init__(self, config_path)
        if connect_db:
            self.db_init(self.config.database_path)


class RemoteAPI:
    pass
