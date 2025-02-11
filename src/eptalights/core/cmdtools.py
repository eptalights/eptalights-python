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

    if not pathlib.Path(api.config.database_path).exists():
        raise Exception(f"transformed_output not found - {api.database_path}")

    if not pathlib.Path(args.decompiled_path).exists():
        os.makedirs(args.decompiled_path)

    for fn in api.search_functions():
        fpath = fn.filepath
        if fn.filepath.startswith("/"):
            fpath = fn.filepath[1:]

        dec_path = pathlib.Path(os.path.abspath(args.decompiled_path))
        local_write_dir_path = dec_path / pathlib.Path(fpath + ".hh")

        if not pathlib.Path(local_write_dir_path).exists():
            try:
                directory = pathlib.Path(local_write_dir_path).parent
                directory.mkdir(parents=True, exist_ok=True)
            except FileExistsError:
                pass

        decompiled_code = fn.decompile()

        with open(local_write_dir_path, "a") as f:
            f.write(decompiled_code)


def build_callgraph():
    parser = argparse.ArgumentParser(description="Build a function call graph model")
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    args = parser.parse_args()

    api = eptalights.LocalAPI(args.project)

    if not pathlib.Path(api.config.database_path).exists():
        raise Exception(f"DB not found - {api.database_path}")

    """
    build all function graph calls
    """
    api.build_function_call_graph()


def print_calltree():
    from printree import ptree

    def call_printer(api, function, depth, max_depth, tracker):
        dct = {}

        if max_depth != -1:
            if depth >= max_depth:
                return dct

        for node_name, node_list in function.fgraph.next_nodes.items():
            for node in node_list:
                tedge = f"{function.fid}:{node.fid}"

                if node.fid is not None and tedge in tracker:
                    continue

                if node.fid is None:
                    fname = f"{" - "*depth} {node_name} (E)"
                    dct[fname] = {}
                else:
                    fname = f"{" - "*depth} {node_name} (F)"

                    tracker.append(tedge)
                    next_function = api.get_function_by_id(node.fid)
                    data = call_printer(
                        api, next_function, depth + 1, max_depth, tracker
                    )
                    dct[fname] = data
        return dct

    parser = argparse.ArgumentParser(description="call tree")
    parser.add_argument("-p", "--project", required=False, default="./eptalights.toml")
    parser.add_argument("-f", "--fid", required=True)
    parser.add_argument("-m", "--max_depth", required=False, type=int, default=-1)
    args = parser.parse_args()

    api = eptalights.LocalAPI(args.project)

    if not pathlib.Path(api.config.database_path).exists():
        raise Exception(f"database_path not found - {api.database_path}")

    current_depth = 1
    start_function = None

    try:
        start_function = api.get_function_by_id(args.fid)
    except Exception:
        _LOG.error(f"function not found - `{args.fid}`")
        return

    """
    track all called fid to prevent recursive calls
    """
    calls_tracker = []
    fname = f"{'-'*current_depth} {start_function.name} (start)"
    current_depth = +1

    data = call_printer(
        api, start_function, current_depth, args.max_depth, calls_tracker
    )
    dct = {fname: data}
    ptree(dct)
