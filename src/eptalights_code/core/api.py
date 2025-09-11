from eptalights_code.core.db import DatabaseAPI
from eptalights_code.core.loader import LoaderAPI

from eptalights_code import models

import time
import random
import requests
import os
from pydantic import UUID4

EPTALIGHTS_CODE_GRAPHQL_API_ENDPOINT = "http://code.eptalights.com/graphql/"


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
        environment variables EPTALIGHTS_CODE_GRAPHQL_API_ENDPOINT
        and EPTALIGHTS_CODE_API_KEY.
        """
        self.endpoint = (
            endpoint
            or os.getenv("EPTALIGHTS_CODE_GRAPHQL_API_ENDPOINT")
            or EPTALIGHTS_CODE_GRAPHQL_API_ENDPOINT
        )
        self.api_key = api_key or os.getenv("EPTALIGHTS_CODE_API_KEY")

        if not self.endpoint:
            raise ValueError(
                "GraphQL endpoint must be provided or "
                "set in EPTALIGHTS_CODE_GRAPHQL_API_ENDPOINT env variable."
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
            mutation InitDataflow($action_id: String!, $dataflow_request: String!) {
                DataflowActionInit(
                    input: {
                        action_id: $action_id,
                        dataflow_request: $dataflow_request
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
                mutation,
                {
                    "action_id": str(df_action.action_id),
                    "dataflow_request": request_b64,
                },
            ).get("DataflowActionInit")

            if response_data["response"]["success"] is False:
                """
                send but if dataflow limit has reached, stop sending and break
                """
                if response_data["response"]["error_message"] == "Max Limit Reached":
                    break
                else:
                    raise Exception(response_data["response"]["error_message"])

    def _send_remove_dataflow_action(self, action_id):
        """
        send locally pending dataflow requests.
        """
        mutation = """
        mutation RemoveDataflow($action_id: String!) {
            DataflowActionRemove(
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
            mutation, {"action_id": str(action_id)}
        ).get("DataflowActionRemove")

        if response_data["response"]["success"] is False:
            raise Exception(response_data["response"]["error_message"])

    def _fetch_and_update_ongoing_dataflow_actions(self):
        query = """
        query FetchDataflowActions {
          DataflowActionFetchResult {
            response {
              success
              error_message
            }
            dataflow_actions {
              action_id
              status
              dataflow_response_bytes
            }
          }
        }
        """

        response_data = self.execute_graphql(query).get("DataflowActionFetchResult")

        if response_data["response"]["success"] is False:
            raise Exception(response_data["response"]["error_message"])

        for dataflow_action in response_data["dataflow_actions"]:
            if dataflow_action["status"] == "DONE":
                self.update_dataflow_action(
                    action_id=dataflow_action["action_id"],
                    status=models.DataflowActionStatusType.DONE,
                    response_b64=dataflow_action["dataflow_response_bytes"],
                )
                self._send_remove_dataflow_action(dataflow_action["action_id"])

            if dataflow_action["status"] == "REMOTE_PROCESSING":
                self.update_dataflow_action(
                    action_id=dataflow_action["action_id"],
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


class RemoteAPI:
    pass
