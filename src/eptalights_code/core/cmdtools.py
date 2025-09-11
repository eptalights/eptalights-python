import argparse
import logging
import os
import pathlib
from datetime import datetime
from tabulate import tabulate
import eptalights_code
from eptalights_code import models

logging.basicConfig(level=logging.DEBUG)
_LOG = logging.getLogger(__name__)


def search_function():
    parser = argparse.ArgumentParser(description="search function by name or filename")
    parser.add_argument(
        "-p", "--project", required=False, default="./eptalights_code.toml"
    )
    parser.add_argument("-q", "--query", required=True)
    args = parser.parse_args()

    api = eptalights_code.LocalAPI(args.project)

    if not pathlib.Path(api.config.local_database_path).exists():
        raise Exception(f"transformed_output not found - {api.local_database_path}")

    table = []
    for fn in api.search_functions(filter_by_name=args.query):
        table.append(
            [
                fn.fid,
                fn.name,
                len(fn.steps),
            ]
        )

    table_headers = [
        "Function ID",
        "Name",
        "Number Of Steps",
    ]
    print(tabulate(table, table_headers, tablefmt="grid"))


def decompile_all():
    parser = argparse.ArgumentParser(description="search function by name or filename")
    parser.add_argument(
        "-p", "--project", required=False, default="./eptalights_code.toml"
    )
    parser.add_argument(
        "-d",
        "--decompiled_path",
        required=False,
        default="./__eptalights_code_decompiled/",
    )
    args = parser.parse_args()

    api = eptalights_code.LocalAPI(args.project)

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


def dataflow_action_list():
    parser = argparse.ArgumentParser(description="List recent 100 dataflow actions")
    parser.add_argument(
        "-p", "--project", required=False, default="./eptalights_code.toml"
    )
    parser.add_argument("-s", "--status", required=False, default=None)
    args = parser.parse_args()

    api = eptalights_code.LocalAPI(args.project)

    status = None
    if args.status is not None and args.status.upper() in [
        "LOCAL_PENDING",
        "REMOTE_PROCESSING",
        "DONE",
    ]:
        status = models.DataflowActionStatusType(args.status.upper())

    table = []
    for df_action in api.iter_dataflow_actions(status=status):
        table.append(
            [
                df_action.action_id,
                df_action.status.value,
                df_action.request_hash,
                datetime.fromtimestamp(float(df_action.data_created)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            ]
        )

    table_headers = ["Action ID", "status", "Request Hash", "Created On"]
    print(tabulate(table, table_headers, tablefmt="grid"))


def dataflow_action_delete():
    parser = argparse.ArgumentParser(description="Delete dataflow action")
    parser.add_argument(
        "-p", "--project", required=False, default="./eptalights_code.toml"
    )
    parser.add_argument("-a", "--action-id", required=True)
    args = parser.parse_args()

    api = eptalights_code.LocalAPI(args.project)
    api.delete_dataflow_action(args.action_id)


def dataflow_actions_update():
    parser = argparse.ArgumentParser(description="Update dataflow actions")
    parser.add_argument(
        "-p", "--project", required=False, default="./eptalights_code.toml"
    )
    args = parser.parse_args()

    api = eptalights_code.LocalAPI(args.project)
    api.dataflow_update()


def dataflow_actions_clear():
    parser = argparse.ArgumentParser(description="Update dataflow actions")
    parser.add_argument(
        "-p", "--project", required=False, default="./eptalights_code.toml"
    )
    parser.add_argument("-s", "--status", required=False, default=None)
    args = parser.parse_args()

    api = eptalights_code.LocalAPI(args.project)

    status = None
    if args.status is not None and args.status.upper() in [
        "LOCAL_PENDING",
        "REMOTE_PROCESSING",
        "DONE",
    ]:
        status = models.DataflowActionStatusType(args.status.upper())

    """
    delete existing actions
    """
    for df_action in api.iter_dataflow_actions(status=status):
        api.delete_dataflow_action(df_action.action_id)
