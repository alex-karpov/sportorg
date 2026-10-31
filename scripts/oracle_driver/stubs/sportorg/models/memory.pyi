# [код: pysport@b548c35 sportorg/models/memory.py]: only what the oracle driver reads.
import uuid
from enum import Enum, IntEnum

from sportorg.common.otime import PythonOTime

class SystemType(Enum):  # :28-37
    NONE = 0
    MANUAL = 1
    SPORTIDENT = 2
    SFR = 3
    SPORTIDUINO = 4
    RFID_IMPINJ = 5
    SRPID = 6
    HUICHANG = 7

class RaceType(Enum):  # :67-71
    INDIVIDUAL_RACE = 0
    PURSUIT = 2
    RELAY = 3
    MULTI_DAY_RACE = 6

class ResultStatus(Enum):  # :74-93
    NONE = 0
    OK = 1
    FINISHED = 2
    DISQUALIFIED = 3
    MISSING_PUNCH = 4
    DID_NOT_FINISH = 5
    ACTIVE = 6
    INACTIVE = 7
    OVERTIME = 8
    SPORTING_WITHDRAWAL = 9
    NOT_COMPETING = 10
    MOVED = 11
    MOVED_UP = 12
    DID_NOT_START = 13
    DID_NOT_ENTER = 14
    CANCELLED = 15
    RESTORED = 16
    MISS_PENALTY_LAP = 17
    MULTI_DAY_ISSUE = 18

class Qualification(IntEnum):  # :2314-2324
    NOT_QUALIFIED = 0
    I_Y = 1
    II_Y = 2
    III_Y = 3
    I = 4
    II = 5
    III = 6
    KMS = 7
    MS = 8
    MSMK = 9

class Group:  # :303
    id: uuid.UUID

class Result:  # :493
    id: uuid.UUID

class RelayLeg:  # :2510
    leg: int
    result: Result | None

class RelayTeam:  # :2665
    group: Group | None
    legs: list[RelayLeg]
    bib_number: int | None
    place: int
    order: int
    def get_time(self) -> PythonOTime: ...
    def get_correct_lap_count(self) -> int: ...
    def get_is_status_ok(self) -> bool: ...

class RaceData:  # :1581
    race_type: RaceType

class Race:  # :1646
    data: RaceData
    relay_teams: list[RelayTeam]
    def to_dict(self) -> dict[str, object]: ...
    def rebuild_indexes(
        self, rebuild_person: bool = True, rebuild_course: bool = False
    ) -> None: ...

def races() -> list[Race]: ...  # :2897
def race(i: int | None = None) -> Race: ...  # :2901
def set_current_race_index(index: int) -> None: ...  # :2887
def get_current_race_index() -> int: ...  # :2893
