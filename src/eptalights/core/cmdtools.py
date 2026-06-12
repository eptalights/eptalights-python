import argparse
import logging
import os
import pathlib
import time
import random
from datetime import datetime
from tabulate import tabulate
import eptalights
from eptalights import models

logging.basicConfig(level=logging.DEBUG)
_LOG = logging.getLogger(__name__)


def builder():
    parser = argparse.ArgumentParser(
        description="transform basic extracted models to function models"
    )
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    parser.add_argument("-n", "--name", required=False, default="")
    parser.add_argument("-w", "--wait", required=False, default="no")
    args = parser.parse_args()

    api = eptalights.LocalAPI(args.project)

    if not api.config.project_id:
        raise Exception("Project ID not set in config")

    proj_extract_path = pathlib.Path(api.config.extractor_output_path)

    if not proj_extract_path.is_dir():
        raise Exception(
            f"Extract Directory not found - {api.config.extractor_output_path}"
        )

    if not any(proj_extract_path.iterdir()):
        raise Exception(
            f"Extract Directory is empty - {api.config.extractor_output_path}"
        )

    build_resp = api.build_init(args.name)
    api.zip_and_upload_disk(proj_extract_path, build_resp["presigned_upload_filepath"])
    api.build_upload_done(api.config.project_id, build_resp["build_id"])

    if args.wait == "yes":
        while True:
            time.sleep(random.uniform(3, 7))

            build_status_resp = api.build_status(
                api.config.project_id, build_resp["build_id"]
            )
            _LOG.info(
                f"Build:{args.name} Build-Stage:{build_status_resp['build_stage']} "
                f"Processing Status:{build_status_resp['processing_status']}"
            )

            if build_status_resp["processing_status"] == "pending":
                continue

            if build_status_resp["processing_status"] == ["failed", "cancelled"]:
                if build_status_resp["build_stage"] == "completed":
                    build_dl_resp = api.build_download_database(
                        api.config.project_id, build_resp["build_name"]
                    )
                    api.download_and_extract_zip_disk(
                        pathlib.Path(
                            f"./{build_dl_resp['build_name']}"
                        ),  # ./build-id/eptalights.db
                        build_dl_resp["presigned_download_filepath"],
                    )
                break

            if build_status_resp["processing_status"] == "success":
                if build_status_resp["build_stage"] != "completed":
                    raise Exception("Something went wrong.")

                build_dl_resp = api.build_download_database(
                    api.config.project_id, build_resp["build_name"]
                )
                api.download_and_extract_zip_disk(
                    pathlib.Path(
                        f"./{build_dl_resp['build_name']}"
                    ),  # ./build-name/eptalights.db
                    build_dl_resp["presigned_download_filepath"],
                )
                break

    _LOG.info("done ...")


def downloader():
    parser = argparse.ArgumentParser(
        description="transform basic extracted models to function models"
    )
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    parser.add_argument("-b", "--name", required=True)
    args = parser.parse_args()

    api = eptalights.LocalAPI(args.project)

    if not api.config.project_id:
        raise Exception("Project ID not set in config")

    proj_extract_path = pathlib.Path(api.config.extractor_output_path)

    if not proj_extract_path.is_dir():
        raise Exception(
            f"Extract Directory not found - {api.config.extractor_output_path}"
        )

    if not any(proj_extract_path.iterdir()):
        raise Exception(
            f"Extract Directory is empty - {api.config.extractor_output_path}"
        )

    build_dl_resp = api.build_download_database(api.config.project_id, args.name)
    api.download_and_extract_zip_disk(
        pathlib.Path(f"./{build_dl_resp['build_name']}"),  # ./build-id/eptalights.db
        build_dl_resp["presigned_download_filepath"],
    )

    _LOG.info("done ...")


def search_function():
    parser = argparse.ArgumentParser(description="search function by name or filename")
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    parser.add_argument("-q", "--query", required=True)
    args = parser.parse_args()

    api = eptalights.LocalAPI(args.project)

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
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    parser.add_argument(
        "-d",
        "--decompiled_path",
        required=False,
        default="./__eptalights_decompiled/",
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


def dataflow_action_list():
    parser = argparse.ArgumentParser(description="List recent 100 dataflow actions")
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    parser.add_argument("-s", "--status", required=False, default=None)
    args = parser.parse_args()

    api = eptalights.LocalAPI(args.project)

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
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    parser.add_argument("-a", "--action-id", required=True)
    args = parser.parse_args()

    api = eptalights.LocalAPI(args.project)
    api.delete_dataflow_action(args.action_id)


def dataflow_actions_update():
    parser = argparse.ArgumentParser(description="Update dataflow actions")
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    args = parser.parse_args()

    api = eptalights.LocalAPI(args.project)
    api.dataflow_update()


def dataflow_actions_clear():
    parser = argparse.ArgumentParser(description="Update dataflow actions")
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    parser.add_argument("-s", "--status", required=False, default=None)
    args = parser.parse_args()

    api = eptalights.LocalAPI(args.project)

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
