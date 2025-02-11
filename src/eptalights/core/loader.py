import os
import tomllib
import pathlib
import msgpack
import json
from typing import Any

from eptalights.models import (
    ConfigModel,
    BasicGimpleFunctionModel,
    BasicOpcodeFunctionModel,
)

"""
for our experimental testing for upcomming support for new
IR or Bytecode
"""
CUSTOM_BASIC_CLASS = None


class LoaderAPI:
    def __init__(self, config_path: str):
        self.config = self._load_project_config(config_path)

    def _iter_files(self, dir_path: str) -> tuple[int, str]:
        index = 0
        for subdir, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(subdir, file)
                if not file_path.endswith(".msgpack") and not file_path.endswith(
                    ".json"
                ):
                    continue
                yield index, file_path
                index += 1

    def _read_file_content(self, filepath: str):
        if filepath.endswith("json"):
            with open(filepath, "r", errors="ignore") as fp:
                fp_content = fp.read()
                return json.loads(fp_content)

        if filepath.endswith(".msgpack"):
            with open(filepath, "rb") as fp:
                fp_content = fp.read()
                return msgpack.unpackb(fp_content)

        raise Exception(f"{filepath} must be json or msgpack type")

    def _load_filepath_to_basic_model(
        self, filepath, code_type
    ) -> BasicGimpleFunctionModel | BasicOpcodeFunctionModel | Any:

        function_data = self._read_file_content(filepath)

        if code_type == "gcc_gimple":
            fn = BasicGimpleFunctionModel(**function_data)
            return fn

        if code_type == "php_opcode":
            basic_model = BasicOpcodeFunctionModel(**function_data)
            return basic_model

        if code_type == "custom" and CUSTOM_BASIC_CLASS is not None:
            basic_model = CUSTOM_BASIC_CLASS(**function_data)
            return basic_model

        raise Exception(f"{code_type} not supported.")

    def _load_project_config(self, config_path: str):
        if not pathlib.Path(config_path).exists():
            raise Exception(f"config path doesn't exist - {config_path}")

        with open(config_path, "rb") as f:
            config_data = tomllib.load(f)

        return ConfigModel(**config_data.get("project"))

    def iter_basic_files(self) -> tuple[str, BasicGimpleFunctionModel]:
        dir_path = self.config.extractor_output
        code_type = self.config.code_type

        for findex, file_path in self._iter_files(dir_path):
            basic_model = self._load_filepath_to_basic_model(file_path, code_type)
            yield file_path, basic_model
