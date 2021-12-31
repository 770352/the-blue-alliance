import datetime
from typing import Any

class Error(Exception): ...
class UnknownQueueError(Error): ...
class TransientError(Error): ...
class InternalError(Error): ...
class InvalidTaskError(Error): ...
class InvalidTaskNameError(InvalidTaskError): ...
class TaskTooLargeError(InvalidTaskError): ...
class TaskAlreadyExistsError(InvalidTaskError): ...
class TombstonedTaskError(InvalidTaskError): ...
class InvalidUrlError(InvalidTaskError): ...
class InvalidEtaError(InvalidTaskError): ...
class BadTaskStateError(Error): ...
class InvalidQueueError(Error): ...
class InvalidQueueNameError(InvalidQueueError): ...
class _RelativeUrlError(Error): ...
class PermissionDeniedError(Error): ...
class DuplicateTaskNameError(Error): ...
class TooManyTasksError(Error): ...
class DatastoreError(Error): ...
class BadTransactionStateError(Error): ...
class InvalidTaskRetryOptionsError(Error): ...
class InvalidLeaseTimeError(Error): ...
class InvalidMaxTasksError(Error): ...
class InvalidDeadlineError(Error): ...
class InvalidQueueModeError(Error): ...
class TransactionalRequestTooLargeError(TaskTooLargeError): ...
class TaskLeaseExpiredError(Error): ...
class QueuePausedError(Error): ...
class InvalidTagError(Error): ...
class InvalidDispatchDeadlineError(Error): ...
class _DefaultAppVersionSingleton: ...
class _UnknownAppVersionSingleton: ...
BadTransactionState = BadTransactionStateError
MAX_QUEUE_NAME_LENGTH: int
MAX_PULL_TASK_SIZE_BYTES: Any
MAX_PUSH_TASK_SIZE_BYTES: Any
MAX_TASK_NAME_LENGTH: int
MAX_TASK_SIZE_BYTES = MAX_PUSH_TASK_SIZE_BYTES
MAX_TASKS_PER_ADD: int
MAX_TRANSACTIONAL_REQUEST_SIZE_BYTES: Any
MAX_URL_LENGTH: int
MAX_TASKS_PER_LEASE: int
MAX_TAG_LENGTH: int
MAX_LEASE_SECONDS: Any
MAX_DISPATCH_DEADLINE: Any
MIN_DISPATCH_DEADLINE: Any
DEFAULT_APP_VERSION: Any

class _UTCTimeZone(datetime.tzinfo):
    ZERO: Any
    def utcoffset(self, dt): ...
    def dst(self, dt): ...
    def tzname(self, dt): ...

def create_rpc(deadline: Any | None = ..., callback: Any | None = ...): ...

class TaskRetryOptions:
    def __init__(self, **kwargs) -> None: ...
    @property
    def min_backoff_seconds(self): ...
    @property
    def max_backoff_seconds(self): ...
    @property
    def task_age_limit(self): ...
    @property
    def max_doublings(self): ...
    @property
    def task_retry_limit(self): ...

class Task:
    def __init__(self, payload: Any | None = ..., **kwargs) -> None: ...
    @property
    def dispatch_deadline_usec(self): ...
    @property
    def eta_posix(self): ...
    @property
    def eta(self): ...
    @property
    def headers(self): ...
    @property
    def method(self): ...
    @property
    def name(self): ...
    @property
    def on_queue_url(self): ...
    @property
    def payload(self): ...
    @property
    def queue_name(self): ...
    @property
    def retry_count(self): ...
    @property
    def retry_options(self): ...
    @property
    def size(self): ...
    @property
    def tag(self): ...
    @property
    def target(self): ...
    @property
    def url(self): ...
    @property
    def was_enqueued(self): ...
    @property
    def was_deleted(self): ...
    def add_async(self, queue_name=..., transactional: bool = ..., rpc: Any | None = ...): ...
    def add(self, queue_name=..., transactional: bool = ...): ...
    def extract_params(self): ...

class QueueStatistics:
    queue: Any
    tasks: Any
    oldest_eta_usec: Any
    executed_last_minute: Any
    in_flight: Any
    enforced_rate: Any
    def __init__(self, queue, tasks, oldest_eta_usec: Any | None = ..., executed_last_minute: Any | None = ..., in_flight: Any | None = ..., enforced_rate: Any | None = ...) -> None: ...
    def __eq__(self, o): ...
    def __ne__(self, o): ...
    @classmethod
    def fetch_async(cls, queue_or_queues, rpc: Any | None = ...): ...
    @classmethod
    def fetch(cls, queue_or_queues, deadline: int = ...): ...

class Queue:
    def __init__(self, name=...) -> None: ...
    def purge(self) -> None: ...
    def delete_tasks_by_name_async(self, task_name, rpc: Any | None = ...): ...
    def delete_tasks_by_name(self, task_name): ...
    def delete_tasks_async(self, task, rpc: Any | None = ...): ...
    def delete_tasks(self, task): ...
    def lease_tasks_async(self, lease_seconds, max_tasks, rpc: Any | None = ...): ...
    def lease_tasks(self, lease_seconds, max_tasks, deadline: int = ...): ...
    def lease_tasks_by_tag_async(self, lease_seconds, max_tasks, tag: Any | None = ..., rpc: Any | None = ...): ...
    def lease_tasks_by_tag(self, lease_seconds, max_tasks, tag: Any | None = ..., deadline: int = ...): ...
    def add_async(self, task, transactional: bool = ..., rpc: Any | None = ...): ...
    def add(self, task, transactional: bool = ...): ...
    @property
    def name(self): ...
    def modify_task_lease(self, task, lease_seconds) -> None: ...
    def fetch_statistics_async(self, rpc: Any | None = ...): ...
    def fetch_statistics(self, deadline: int = ...): ...
    def __eq__(self, o): ...
    def __ne__(self, o): ...

def add(*args, **kwargs): ...