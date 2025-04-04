import argparse
import logging
import os
import pathlib
import eptalights

logging.basicConfig(level=logging.DEBUG)
_LOG = logging.getLogger(__name__)


def search_function():
    parser = argparse.ArgumentParser(description="search function by name or filename")
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    parser.add_argument("-q", "--query", required=True)
    args = parser.parse_args()

    api = eptalights.LocalAPI(args.project)

    if not pathlib.Path(api.config.database_path).exists():
        raise Exception(f"transformed_output not found - {api.database_path}")

    for fn in api.search_functions(filter_by_name=args.query):
        print(f"name={fn.name} -- fid={fn.fid}")


def decompile_all():
    parser = argparse.ArgumentParser(description="search function by name or filename")
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    parser.add_argument(
        "-d",
        "--decompiled_path",
        required=False,
        default="./__eptalights_decompiled_code/",
    )
    args = parser.parse_args()

    api = eptalights.LocalAPI(args.project)

    if not pathlib.Path(api.config.local_database_path).exists():
        raise Exception(f"transformed_output not found - {api.local_database_path}")

    if not pathlib.Path(args.decompiled_path).exists():
        os.makedirs(args.decompiled_path)

    for file_metadata in api.search_file_metadata():
        file_data = api.get_file_data_by_metadata(file_metadata)

        fpath = file_data.filepath
        if file_data.filepath.startswith("/"):
            fpath = file_data.filepath[1:]

        dec_path = pathlib.Path(os.path.abspath(args.decompiled_path))
        local_write_dir_path = dec_path / pathlib.Path(fpath + ".hh")

        if not pathlib.Path(local_write_dir_path).exists():
            try:
                directory = pathlib.Path(local_write_dir_path).parent
                directory.mkdir(parents=True, exist_ok=True)
            except FileExistsError:
                pass

        decompiled_code = file_data.decompile()

        with open(local_write_dir_path, "a") as f:
            f.write(decompiled_code)
