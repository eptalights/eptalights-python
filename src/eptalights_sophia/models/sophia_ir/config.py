from pydantic import BaseModel
from typing import Optional


class ConfigModel(BaseModel):
    """Represents the configuration settings for a code analysis process.

    Attributes
    ----------
    project_id : str, optional
        The unique identifier for the project. Defaults to None.
    extractor_output_path : str
        The path to the extractor's output directory.
    code_type : str
        The type of code being processed (e.g., source, intermediate
        representation).
    storage_backend : str, optional
        The storage backend used for extracted data. Defaults to sqLite3,
        with support for additional file-based databases planned.
    local_database_path : str, optional
        The path to the database storing extracted information. Defaults to None.
    output_decompiled_path : str, optional
        The destination path for storing decompiled code. Defaults to
        "./__eptalights_sophia_decompiled_code/".
    """

    project_id: Optional[str] = None
    extractor_output_path: str
    code_type: str  # Example values: gcc_gimple, php_opcode, jvm_jimple
    storage_backend: Optional[str] = "sqlite3"  # Default: sqLite3; extensible later
    local_database_path: Optional[str] = None
    output_decompiled_path: Optional[str] = "./__eptalights_sophia_decompiled_code/"
