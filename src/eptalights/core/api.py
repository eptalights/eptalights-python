from eptalights.core.db import DatabaseAPI
from eptalights.core.loader import LoaderAPI

from eptalights import models

import time
import random
import requests
import os
from pydantic import UUID4
import zipfile
import io
from pathlib import Path
import tempfile

EPTALIGHTS_GRAPHQL_API_ENDPOINT = "http://platform.eptalights.com/graphql/"


class LocalAPI(DatabaseAPI, LoaderAPI):
    def __init__(
        self,
        config_path: str,
        connect_db: bool = True,
        endpoint: str = None,
        api_key: str = None,
    ):
        LoaderAPI.__init__(self, config_path)
        if connect_db:
            self.db_init(self.config.local_database_path)

        """
        Initialize the GraphQL client.

        If no endpoint or API key is provided, it will try to load them from
        environment variables EPTALIGHTS_GRAPHQL_API_ENDPOINT
        and EPTALIGHTS_API_KEY.
        """
        self.endpoint = (
            endpoint
            or os.getenv("EPTALIGHTS_GRAPHQL_API_ENDPOINT")
            or EPTALIGHTS_GRAPHQL_API_ENDPOINT
        )
        self.api_key = api_key or os.getenv("EPTALIGHTS_API_KEY")

        if not self.endpoint:
            raise ValueError(
                "GraphQL endpoint must be provided or "
                "set in EPTALIGHTS_GRAPHQL_API_ENDPOINT env variable."
            )

    def execute_graphql(self, query: str, variables: dict = None) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"query": query, "variables": variables or {}}

        response = requests.post(
            self.endpoint, json=payload, headers=headers, timeout=30
        )
        if response.status_code != 200:
            print(
                "Mutation failed with status code "
                f"{response.status_code}: {response.text}"
            )

        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")

        return data.get("data")

    def _send_local_pending_dataflow_actions(self):
        """
        send locally pending dataflow requests.
        """
        for df_action in self.iter_dataflow_actions(
            status=models.DataflowActionStatusType.LOCAL_PENDING
        ):
            request_b64 = self._encode_dataflow_action_request_to_b64(df_action.request)
            mutation = """
            mutation DataflowActionInit($input: DataflowActionInitInput!) {
                dataflowActionInit(input: $input) {
                response {
                  success
                  error_message
                }
                action_id
              }
            }
            """

            variables = {
                "input": {
                    "dataflow_request_bytes": request_b64,
                }
            }
            response_data = self.execute_graphql(mutation, variables).get(
                "dataflowActionInit"
            )

            if response_data["response"]["success"] is False:
                """
                send but if dataflow limit has reached, stop sending and break
                """
                if response_data["response"]["error_message"] == "Max Limit Reached":
                    break
                else:
                    raise Exception(response_data["response"]["error_message"])

            if response_data["response"]["success"] is True:
                self.update_dataflow_action_by_local_id(
                    action_id=df_action.action_id,
                    remote_action_id=response_data["action_id"],
                )

    def _send_remove_dataflow_action(self, remote_action_id):
        """
        send locally pending dataflow requests.
        """
        mutation = """
        mutation DataflowActionRemove($action_id: String!) {
            dataflowActionRemove(
                input: {
                    action_id: $action_id,
                }
            ) {
            response {
                success
                error_message
            }
            }
        }
        """

        response_data = self.execute_graphql(
            mutation, {"action_id": str(remote_action_id)}
        ).get("dataflowActionRemove")

        if response_data["response"]["success"] is False:
            raise Exception(response_data["response"]["error_message"])

    def _fetch_and_update_ongoing_dataflow_actions(self):
        query = """
        query {
          dataflowGetActionsResult {
            response {
              success
              error_message
            }
            dataflow_action_results {
              action_id
              status
              dataflow_stage
              dataflow_response_bytes
              init_at
              queued_at
              processing_at
              completed_at
            }
          }
        }
        """

        response_data = self.execute_graphql(query).get("dataflowGetActionsResult")

        if response_data["response"]["success"] is False:
            raise Exception(response_data["response"]["error_message"])

        for dataflow_action in response_data["dataflow_action_results"]:
            if dataflow_action["dataflow_stage"] == "completed":
                self.update_dataflow_action_by_remote_id(
                    remote_action_id=dataflow_action["action_id"],
                    status=models.DataflowActionStatusType.DONE,
                    response_b64=dataflow_action["dataflow_response_bytes"],
                )
                self._send_remove_dataflow_action(dataflow_action["action_id"])

            if dataflow_action["dataflow_stage"] in ["init", "queued", "processing"]:
                self.update_dataflow_action_by_remote_id(
                    remote_action_id=dataflow_action["action_id"],
                    status=models.DataflowActionStatusType.REMOTE_PROCESSING,
                )

    def dataflow_update(self):
        self._send_local_pending_dataflow_actions()
        self._fetch_and_update_ongoing_dataflow_actions()

    def dataflow_get(
        self,
        action_id: UUID4 | str,
        wait_for_response: bool = False,
    ):
        df_action = self.get_dataflow_action(action_id)
        if df_action.status == models.DataflowActionStatusType.DONE:
            return df_action

        if wait_for_response is True:
            while True:
                df_action = self.get_dataflow_action(df_action.action_id)
                if df_action.status == models.DataflowActionStatusType.DONE:
                    break

                self.dataflow_update()
                time.sleep(random.uniform(3, 7))

        return df_action

    def dataflow_run(
        self,
        datafow_request: models.DataflowRequestModel,
        wait_for_response: bool = False,
        delete_after_read: bool = False,
        use_cached_response: bool = True,
    ) -> models.DataflowActionModel:
        df_action = self.create_dataflow_action(datafow_request, delete_after_read)
        self.dataflow_update()

        if wait_for_response is True:
            while True:
                df_action = self.get_dataflow_action(df_action.action_id)
                if df_action.status == models.DataflowActionStatusType.DONE:
                    break

                self.dataflow_update()
                time.sleep(random.uniform(3, 7))

        return df_action

    def build_init(self, name=None) -> None:
        query = """
        mutation BuildClientInit($input: BuildClientInitInput!) {
            buildClientInit(input: $input) {
                response {
                    success
                    error_message
                }
                build_id
                build_name
                presigned_upload_filepath
            }
        }
        """

        variables = {"input": {"project_id": self.config.project_id, "name": name}}
        response_data = self.execute_graphql(query, variables).get("buildClientInit")
        if response_data["response"]["success"] is False:
            raise Exception(response_data["response"]["error_message"])

        return response_data

    def build_upload_done(self, project_id: str, build_id: str):
        query = """
        mutation BuildClientUploadDone($input: BuildClientUploadDoneInput!) {
            buildClientUploadDone(input: $input) {
                response {
                    success
                    error_message
                }
            }
        }
        """

        variables = {
            "input": {
                "project_id": project_id,
                "build_id": build_id,
            }
        }
        response_data = self.execute_graphql(query, variables).get(
            "buildClientUploadDone"
        )
        if response_data["response"]["success"] is False:
            raise Exception(
                f"http_error_message: {response_data['response']['error_message']}"
            )

    def build_status(self, project_id: str, build_id: str):
        query = """
        query ($project_id: String!, $build_id: String!) {
            buildClientStatus(project_id: $project_id, build_id: $build_id) {
                response {
                    success
                    error_message
                }
                build_stage
                processing_status
            }
        }
        """

        variables = {
            "project_id": project_id,
            "build_id": build_id,
        }
        response_data = self.execute_graphql(query, variables).get("buildClientStatus")
        if response_data["response"]["success"] is False:
            raise Exception(
                f"http_error_message: {response_data['response']['error_message']}"
            )
        return response_data

    def build_download_database(self, project_id, build_name) -> None:
        query = """
        mutation BuildClientDownloadDatabase(
            $input: BuildClientDownloadDatabaseInput!
        ) {
            buildClientDownloadDatabase(input: $input) {
                response {
                    success
                    error_message
                }
                build_id
                build_name
                download_filesize
                presigned_download_filepath
            }
        }
        """

        variables = {"input": {"project_id": project_id, "name": build_name}}
        response_data = self.execute_graphql(query, variables).get(
            "buildClientDownloadDatabase"
        )
        if response_data["response"]["success"] is False:
            raise Exception(response_data["response"]["error_message"])

        return response_data

    def zip_and_upload_mem(directory: Path, presigned_url: str) -> None:
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    zipf.write(file_path, file_path.relative_to(directory))

        buffer.seek(0)

        response = requests.put(presigned_url, data=buffer)

        if response.status_code not in (200, 204):
            raise RuntimeError("Upload to S3 failed")

    def zip_and_upload_disk(self, path: Path, presigned_url: str) -> None:
        if not path.exists():
            raise ValueError(f"{path} does not exist")

        with tempfile.NamedTemporaryFile(suffix=".zip") as tmp:
            with zipfile.ZipFile(
                tmp.name, "w", compression=zipfile.ZIP_DEFLATED
            ) as zipf:

                if path.is_file():
                    zipf.write(path, arcname=path.name)

                else:
                    for file_path in path.rglob("*"):
                        if file_path.is_file():
                            zipf.write(file_path, file_path.relative_to(path))

            tmp.seek(0)

            with open(tmp.name, "rb") as f:
                headers = {"Content-Type": "application/zip"}
                response = requests.put(presigned_url, data=f, headers=headers)
                response.raise_for_status()

    def download_and_extract_zip_mem(
        self, output_path: Path, presigned_url: str
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with requests.get(presigned_url, stream=True) as response:
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

    def download_and_extract_zip_disk(
        self, output_path: Path, presigned_url: str
    ) -> None:
        output_path.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(suffix=".zip") as tmp:
            # Stream download
            with requests.get(presigned_url, stream=True) as response:
                response.raise_for_status()

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp.write(chunk)

            tmp.flush()

            # Extract
            with zipfile.ZipFile(tmp.name, "r") as zipf:
                zipf.extractall(output_path)


class RemoteAPI:
    pass
