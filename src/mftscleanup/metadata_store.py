"""
Stores metadata about shares on the filesystem.
"""

from datetime import date
from logging import getLogger
from pathlib import Path
from typing import Iterator, Union

from addict import Dict
from yaml import parser, safe_dump, safe_load

from .email import Emailer
from .state import State, STATE_NAMES


logger = getLogger(__name__)


class MetadataStore:
    """
    Wraps the top-level directory, which contains the active shares, the archive,
    email configuration, and the mapping file from sponsor ID to sponsor email.
    """

    def __init__(self, metadata_root: Union[str, Path]) -> None:
        self.metadata_root = Path(metadata_root)
        self._active = self.metadata_root / "active"
        self._archive = self.metadata_root / "archive"

    @property
    def active(self) -> Path:
        if not self._active.is_dir():
            self._active.mkdir(parents=True, exist_ok=True)
        return self._active

    @property
    def archive(self) -> Path:
        if not self._archive.is_dir():
            self._archive.mkdir(parents=True, exist_ok=True)
        return self._archive

    def load_emailer(self, emailer_factory=Emailer) -> Emailer:
        email_config = load_config(self.metadata_root / "email_settings.yaml")
        emailer = emailer_factory(
            email_config.from_address,
            email_config.host,
        )
        return emailer

    def get_sponsor_email(self, sponsor_id) -> str:
        raise NotImplementedError  # TODO

    def write_event(self, payload: dict, share_id: str, event_id: str) -> None:
        destination = self.active / f"{share_id}_{event_id}.yaml"
        write_yaml(payload, destination)

    def get_active_shares(self) -> Iterator[str]:
        """
        Return the names (eg. "rt1234") of all the active shares.
        """
        shares = set()
        for yaml_file_path in self.active.glob("*.yaml"):
            share_name = yaml_file_path.name.rsplit("_", 1)[0]
            shares.add(share_name)
        return sorted(shares)

    def get_share_state(self, share_id: str) -> tuple[State, date]:
        yaml_file_path = max(self.active.glob(f"{share_id}_*.yaml"))
        with open(yaml_file_path, "r") as yaml_file:
            try:
                payload = safe_load(yaml_file)
            except parser.ParserError as e:
                raise EventFileCorruptError(
                    f"YAML file is corrupt: {yaml_file=}"
                ) from e
        if not isinstance(payload, dict):
            raise EventNotDictError(f"YAML file is not a dict: {yaml_file=}")
        if payload["share_id"] != share_id:
            raise InconsistentEventError(
                f"YAML file contents do not match the file name: "
                f"{share_id=} {yaml_file_path=}"
            )
        results = []
        for key, value in payload.items():
            attribute = str(key)
            if attribute.endswith("_date"):
                state_name = attribute.removesuffix("_date")
                if state_name not in STATE_NAMES:
                    raise BadStateError(f"bad {state_name=} in {yaml_file_path=}")
                state = State[state_name]
                state_date = date.fromisoformat(value)
                results.append((state, state_date))
        if not results:
            raise MissingStateError(f"no state found in {yaml_file_path}")
        if len(results) > 1:
            raise AmbiguousStateError(f"ambiguous state in {yaml_file_path=}")
        return results[0]


def write_yaml(payload: dict, destination: Path) -> None:
    if destination.is_file():
        logger.warning(f"overwriting {destination}")
    directory = destination.parent
    directory.mkdir(parents=True, exist_ok=True)
    yaml_text = safe_dump(payload, default_flow_style=False)
    destination.write_text(yaml_text, encoding="UTF-8")
    logger.info(f"wrote {destination}")


def load_config(config_file_path):
    with open(config_file_path) as f:
        config = Dict(safe_load(f))
    return config


class BadEventFileError(RuntimeError):
    """The YAML file for a share event is bad."""


class EventFileCorruptError(BadEventFileError):
    """File contents are not YAML."""


class EventNotDictError(BadEventFileError):
    """The YAML payload is something other than a dict."""


class InconsistentEventError(BadEventFileError):
    """The YAML payload does not match the file name."""


class BadStateError(BadEventFileError):
    """The YAML payload contains a bad (made-up) state name."""


class MissingStateError(BadEventFileError):
    """The YAML payload contains no state."""


class AmbiguousStateError(BadEventFileError):
    """The YAML payload contains more than one state."""
