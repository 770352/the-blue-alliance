from .transports.base import CloudTasksTransport
from google.api_core import client_options as client_options_lib, gapic_v1, retry as retries
from google.auth import credentials
from google.cloud.tasks_v2.services.cloud_tasks import pagers
from google.cloud.tasks_v2.types import cloudtasks, queue, queue as gct_queue, task, task as gct_task
from google.iam.v1 import iam_policy_pb2 as iam_policy, policy_pb2 as policy
from google.protobuf import field_mask_pb2 as field_mask
from typing import Any, Dict, Optional, Sequence, Tuple, Type, Union

class CloudTasksClientMeta(type):
    def get_transport_class(cls: Any, label: str=...) -> Type[CloudTasksTransport]: ...

class CloudTasksClient(metaclass=CloudTasksClientMeta):
    DEFAULT_ENDPOINT: str = ...
    DEFAULT_MTLS_ENDPOINT: Any = ...
    @classmethod
    def from_service_account_file(cls: Any, filename: str, *args: Any, **kwargs: Any) -> Any: ...
    from_service_account_json: Any = ...
    @property
    def transport(self) -> CloudTasksTransport: ...
    @staticmethod
    def queue_path(project: str, location: str, queue: str) -> str: ...
    @staticmethod
    def parse_queue_path(path: str) -> Dict[str, str]: ...
    @staticmethod
    def task_path(project: str, location: str, queue: str, task: str) -> str: ...
    @staticmethod
    def parse_task_path(path: str) -> Dict[str, str]: ...
    @staticmethod
    def common_billing_account_path(billing_account: str) -> str: ...
    @staticmethod
    def parse_common_billing_account_path(path: str) -> Dict[str, str]: ...
    @staticmethod
    def common_folder_path(folder: str) -> str: ...
    @staticmethod
    def parse_common_folder_path(path: str) -> Dict[str, str]: ...
    @staticmethod
    def common_organization_path(organization: str) -> str: ...
    @staticmethod
    def parse_common_organization_path(path: str) -> Dict[str, str]: ...
    @staticmethod
    def common_project_path(project: str) -> str: ...
    @staticmethod
    def parse_common_project_path(path: str) -> Dict[str, str]: ...
    @staticmethod
    def common_location_path(project: str, location: str) -> str: ...
    @staticmethod
    def parse_common_location_path(path: str) -> Dict[str, str]: ...
    def __init__(self, *, credentials: Optional[credentials.Credentials]=..., transport: Union[str, CloudTasksTransport, None]=..., client_options: Optional[client_options_lib.ClientOptions]=..., client_info: gapic_v1.client_info.ClientInfo=...) -> None: ...
    def list_queues(self, request: cloudtasks.ListQueuesRequest=..., *, parent: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> pagers.ListQueuesPager: ...
    def get_queue(self, request: cloudtasks.GetQueueRequest=..., *, name: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> queue.Queue: ...
    def create_queue(self, request: cloudtasks.CreateQueueRequest=..., *, parent: str=..., queue: gct_queue.Queue=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> gct_queue.Queue: ...
    def update_queue(self, request: cloudtasks.UpdateQueueRequest=..., *, queue: gct_queue.Queue=..., update_mask: field_mask.FieldMask=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> gct_queue.Queue: ...
    def delete_queue(self, request: cloudtasks.DeleteQueueRequest=..., *, name: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> None: ...
    def purge_queue(self, request: cloudtasks.PurgeQueueRequest=..., *, name: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> queue.Queue: ...
    def pause_queue(self, request: cloudtasks.PauseQueueRequest=..., *, name: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> queue.Queue: ...
    def resume_queue(self, request: cloudtasks.ResumeQueueRequest=..., *, name: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> queue.Queue: ...
    def get_iam_policy(self, request: iam_policy.GetIamPolicyRequest=..., *, resource: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> policy.Policy: ...
    def set_iam_policy(self, request: iam_policy.SetIamPolicyRequest=..., *, resource: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> policy.Policy: ...
    def test_iam_permissions(self, request: iam_policy.TestIamPermissionsRequest=..., *, resource: str=..., permissions: Sequence[str]=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> iam_policy.TestIamPermissionsResponse: ...
    def list_tasks(self, request: cloudtasks.ListTasksRequest=..., *, parent: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> pagers.ListTasksPager: ...
    def get_task(self, request: cloudtasks.GetTaskRequest=..., *, name: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> task.Task: ...
    def create_task(self, request: cloudtasks.CreateTaskRequest=..., *, parent: str=..., task: gct_task.Task=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> gct_task.Task: ...
    def delete_task(self, request: cloudtasks.DeleteTaskRequest=..., *, name: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> None: ...
    def run_task(self, request: cloudtasks.RunTaskRequest=..., *, name: str=..., retry: retries.Retry=..., timeout: float=..., metadata: Sequence[Tuple[str, str]]=...) -> task.Task: ...