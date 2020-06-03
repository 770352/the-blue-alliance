import py
from .pathlib import LOCK_TIMEOUT as LOCK_TIMEOUT, Path as Path, ensure_reset_dir as ensure_reset_dir, make_numbered_dir as make_numbered_dir, make_numbered_dir_with_cleanup as make_numbered_dir_with_cleanup
from _pytest.fixtures import FixtureRequest as FixtureRequest
from _pytest.monkeypatch import MonkeyPatch as MonkeyPatch
from typing import Any, Optional

class TempPathFactory:
    @classmethod
    def from_config(cls: Any, config: Any) -> TempPathFactory: ...
    def mktemp(self, basename: str, numbered: bool=...) -> Path: ...
    def getbasetemp(self) -> Path: ...
    def __init__(self, given_basetemp: Any, trace: Any, basetemp: Any) -> None: ...
    def __ne__(self, other: Any) -> Any: ...
    def __eq__(self, other: Any) -> Any: ...
    def __lt__(self, other: Any) -> Any: ...
    def __le__(self, other: Any) -> Any: ...
    def __gt__(self, other: Any) -> Any: ...
    def __ge__(self, other: Any) -> Any: ...

class TempdirFactory:
    def mktemp(self, basename: str, numbered: bool=...) -> py.path.local: ...
    def getbasetemp(self): ...
    def __init__(self, tmppath_factory: Any) -> None: ...
    def __ne__(self, other: Any) -> Any: ...
    def __eq__(self, other: Any) -> Any: ...
    def __lt__(self, other: Any) -> Any: ...
    def __le__(self, other: Any) -> Any: ...
    def __gt__(self, other: Any) -> Any: ...
    def __ge__(self, other: Any) -> Any: ...

def get_user() -> Optional[str]: ...
def pytest_configure(config: Any) -> None: ...
def tmpdir_factory(request: FixtureRequest) -> TempdirFactory: ...
def tmp_path_factory(request: FixtureRequest) -> TempPathFactory: ...
def tmpdir(tmp_path: Any): ...
def tmp_path(request: FixtureRequest, tmp_path_factory: TempPathFactory) -> Path: ...