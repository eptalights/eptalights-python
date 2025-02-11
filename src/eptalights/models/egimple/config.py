from pydantic import BaseModel
from typing import Optional


class ConfigModel(BaseModel):
    """Represents the configuration settings for a code analysis process.

    Attributes
    ----------
    name : str, optional
        The name of the configuration. Defaults to None.
    project_id : str, optional
        The unique identifier for the project. Defaults to None.
    extractor_output : str
        The path to the extractor's output directory.
    code_type : str
        The type of code being processed (e.g., source, intermediate representation).
    database_path : str, optional
        The path to the database storing extracted information. Defaults to None.
    decompiled_code : bool, optional
        Indicates whether to decompile code when lifting. Defaults to False.
    decompiled_code_dst_path : str, optional
        The destination path for storing decompiled code. Defaults to None.
    """

    name: Optional[str] = None
    project_id: Optional[str] = None
    extractor_output: str
    code_type: str
    database_path: Optional[str] = None
    decompiled_code: Optional[bool] = False
    decompiled_code_dst_path: Optional[str] = "./__eptalights_decompiled_code/"
