from .Decoder import *
from typing import *
import logging

from abc import ABC, abstractmethod

from json import JSONEncoder


class DefaultJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, JSONable):
            return o.json_dict()
        return o.__dict__


NOTE_EVENT_GOOD = 0
NOTE_EVENT_BAD = 1
NOTE_EVENT_MISS = 2
NOTE_EVENT_BOMB = 3
NOTE_SCORE_TYPE_NORMAL_1 = 0
NOTE_SCORE_TYPE_IGNORE = 1
NOTE_SCORE_TYPE_NOSCORE = 2
NOTE_SCORE_TYPE_NORMAL_2 = 3
NOTE_SCORE_TYPE_SLIDERHEAD = 4
NOTE_SCORE_TYPE_SLIDERTAIL = 5
NOTE_SCORE_TYPE_BURSTSLIDERHEAD = 6
NOTE_SCORE_TYPE_BURSTSLIDERELEMENT = 7

SABER_LEFT = 1
SABER_RIGHT = 0

MAX_SUPPORTED_VERSION = 1
MAGIC_HEX = '0x442d3d69'

lookup_dict_scoring_type = {
    NOTE_SCORE_TYPE_NORMAL_1: 'Normal',
    NOTE_SCORE_TYPE_IGNORE: 'Ignore',
    NOTE_SCORE_TYPE_NOSCORE: 'NoScore',
    NOTE_SCORE_TYPE_NORMAL_2: 'Normal',
    NOTE_SCORE_TYPE_SLIDERHEAD: 'SliderHead',
    NOTE_SCORE_TYPE_SLIDERTAIL: 'SliderTail',
    NOTE_SCORE_TYPE_BURSTSLIDERHEAD: 'BurstSliderHead',
    NOTE_SCORE_TYPE_BURSTSLIDERELEMENT: 'BurstSliderElement'
}

lookup_dict_event_type = {
    NOTE_EVENT_GOOD: 'cut',
    NOTE_EVENT_BAD: 'badcut',
    NOTE_EVENT_MISS: 'miss',
    NOTE_EVENT_BOMB: 'bomb'
}


def make_things(f, thing) -> List:
    cnt = decode_int(f)
    return [thing(f) for _ in range(cnt)]


class BSException(BaseException):
    pass


class JSONable(ABC):
    @abstractmethod
    def json_dict(self):
        pass

    def __str__(self):
        return DefaultJsonEncoder().encode(self.json_dict())


class Info(JSONable):
    version: str
    gameVersion: str
    timestamp: str

    playerId: str
    playerName: str
    platform: str

    trackingSystem: str
    hmd: str
    controller: str

    songHash: str
    songName: str
    mapper: str
    difficulty: str

    score: int
    mode: str
    environment: str
    modifiers: str
    jumpDistance: float
    leftHanded: bool
    height: float

    startTime: float
    failTime: float
    speed: float

    def json_dict(self):
        return self.__dict__

def make_info(f) -> Info:
    info_start = decode_byte(f)

    if info_start != 0:
        raise BSException(f'Info magic number must be 0, got "{info_start}" instead')
    info = Info()
    info.version = decode_string(f)
    info.gameVersion = decode_string(f)
    info.timestamp = decode_string(f)

    info.playerId = decode_string(f)
    info.playerName = decode_string_maybe_utf16(f)
    info.platform = decode_string(f)

    info.trackingSystem = decode_string(f)
    info.hmd = decode_string(f)
    info.controller = decode_string(f)

    info.songHash = decode_string(f)
    info.songName = decode_string_maybe_utf16(f)
    info.mapper = decode_string_maybe_utf16(f)
    info.difficulty = decode_string(f)

    info.score = decode_int(f)
    info.mode = decode_string(f)
    info.environment = decode_string(f)
    info.modifiers = decode_string(f)
    info.jumpDistance = decode_float(f)

    info.leftHanded = decode_bool(f)
    info.height = decode_float(f)

    info.startTime = decode_float(f)
    info.failTime = decode_float(f)
    info.speed = decode_float(f)

    return info


class VRObject(JSONable):
    x: float
    y: float
    z: float
    x_rot: float
    y_rot: float
    z_rot: float
    w_rot: float

    @property
    def position(self):
        return self.x, self.y, self.z

    @property
    def rotation(self):
        return self.x_rot, self.y_rot, self.z_rot, self.w_rot

    def json_dict(self):
        return {'position': {'x': self.x, 'y': self.y, 'z': self.z},
                'rotation': {'x': self.x_rot, 'y': self.y_rot, 'z': self.z_rot, 'w': self.w_rot}
                }


def make_vr_object(f) -> VRObject:
    v = VRObject()
    v.x = decode_float(f)
    v.y = decode_float(f)
    v.z = decode_float(f)
    v.x_rot = decode_float(f)
    v.y_rot = decode_float(f)
    v.z_rot = decode_float(f)
    v.w_rot = decode_float(f)
    return v


class Frame(JSONable):
    time: float
    fps: int
    head: VRObject
    left_hand: VRObject
    right_hand: VRObject

    def json_dict(self):
        return self.__dict__


def make_frames(f) -> List[Frame]:
    frames_start = decode_byte(f)
    if frames_start != 1:
        raise BSException(f'Frames magic number must be 1, got "{frames_start}" instead')
    result = make_things(f, make_frame)
    return result


def make_frame(f) -> Frame:
    fr = Frame()
    fr.time = decode_float(f)
    fr.fps = decode_int(f)
    fr.head = make_vr_object(f)
    fr.left_hand = make_vr_object(f)
    fr.right_hand = make_vr_object(f)
    return fr


class Cut(JSONable):
    speedOK: bool
    directionOk: bool
    saberTypeOk: bool
    wasCutTooSoon: bool
    saberSpeed: float
    saberDirection: typing.List
    saberType: int
    timeDeviation: float
    cutDeviation: float
    cutPoint: typing.List
    cutNormal: typing.List
    cutDistanceToCenter: float
    cutAngle: float
    beforeCutRating: float
    afterCutRating: float

    def json_dict(self):
        print_dict = self.__dict__.copy()
        print_dict['saberType'] = 'left' if self.saberType == SABER_LEFT else 'right'
        print_dict['saberDirection'] = {'x': self.saberDirection[0], 'y': self.saberDirection[1], 'z': self.saberDirection[2]}
        print_dict['cutPoint'] = {'x': self.cutPoint[0], 'y': self.cutPoint[1], 'z': self.cutPoint[2]}
        print_dict['cutNormal'] = {'x': self.cutNormal[0], 'y': self.cutNormal[1], 'z': self.cutNormal[2]}
        return print_dict


class Note(JSONable):
    # scoringType*10000 + lineIndex*1000 + noteLineLayer*100 + colorType*10 + cutDirection.
    # Where scoringType is game value + 2. Standard values:
    # Normal = 0,
    # Ignore = 1,
    # NoScore = 2,
    # Normal = 3,
    # SliderHead = 4,
    # SliderTail = 5,
    # BurstSliderHead = 6,
    # BurstSliderElement = 7
    note_id: int
    scoringType: int
    lineIndex: int
    noteLineLayer: int
    colorType: int
    cutDirection: int
    event_time: float
    spawn_time: float
    event_type: int  # good = 0,bad = 1,miss = 2,bomb = 3
    cut: Cut
    pre_score: int
    post_score: int
    acc_score: int
    score: int

    def json_dict(self):
        print_dict = self.__dict__.copy()
        print_dict['scoringType'] = lookup_dict_scoring_type[self.scoringType]
        print_dict['event_type'] = lookup_dict_event_type[self.event_type]
        return print_dict


def make_notes(f) -> List[Note]:
    notes_starter = decode_byte(f)
    if notes_starter != 2:
        raise BSException(f'Notes magic number must be 2, got "{notes_starter}" instead')

    result = make_things(f, make_note)
    return result


def make_note(f) -> Note:
    n = Note()
    n.note_id = decode_int(f)
    x = n.note_id
    n.cutDirection = int(x % 10)
    x = (x - n.cutDirection) / 10
    n.colorType = int(x % 10)
    x = (x - n.colorType) / 10
    n.noteLineLayer = int(x % 10)
    x = (x - n.noteLineLayer) / 10
    n.lineIndex = int(x % 10)
    x = (x - n.lineIndex) / 10
    n.scoringType = int(x % 10)
    x = (x - n.scoringType) / 10
    n.event_time = decode_float(f)
    n.spawn_time = decode_float(f)
    n.event_type = decode_int(f)
    if n.event_type in [NOTE_EVENT_GOOD, NOTE_EVENT_BAD]:
        n.cut = make_cut(f)
        score = calc_note_score(n.cut, n.scoringType)
        n.pre_score = score[0]
        n.post_score = score[1]
        n.acc_score = score[2]
    else:
        n.pre_score = 0
        n.post_score = 0
        n.acc_score = 0
    n.score = n.pre_score + n.post_score + n.acc_score
    return n


def clamp(n, smallest, largest):
    return sorted([smallest, n, largest])[1]


def round_half_up(f: float) -> int:
    a = f % 1
    if a < 0.5:
        return int(f)
    else:
        return int(f + 1)


def calc_note_score(cut: Cut, type: int):
    if not cut.directionOk or not cut.saberTypeOk or not cut.speedOK:
        return 0, 0, 0
    beforeCutRawScore = 0
    if type != NOTE_SCORE_TYPE_BURSTSLIDERELEMENT:
        if type == NOTE_SCORE_TYPE_SLIDERTAIL:
            beforeCutRawScore = 70
        else:
            beforeCutRawScore = 70 * cut.beforeCutRating
            beforeCutRawScore = round_half_up(beforeCutRawScore)
            beforeCutRawScore = clamp(beforeCutRawScore, 0, 70)

    afterCutRawScore = 0
    if type != NOTE_SCORE_TYPE_BURSTSLIDERELEMENT:
        if type == NOTE_SCORE_TYPE_BURSTSLIDERHEAD:
            afterCutRawScore = 0
        elif type == NOTE_SCORE_TYPE_SLIDERHEAD:
            afterCutRawScore = 30
        else:
            afterCutRawScore = 30 * cut.afterCutRating
            afterCutRawScore = round_half_up(afterCutRawScore)
            afterCutRawScore = clamp(afterCutRawScore, 0, 30)

    cutDistanceRawScore = 0
    if type == NOTE_SCORE_TYPE_BURSTSLIDERELEMENT:
        cutDistanceRawScore = 20
    else:
        cutDistanceRawScore = cut.cutDistanceToCenter / 0.3
        cutDistanceRawScore = 1 - clamp(cutDistanceRawScore, 0, 1)
        cutDistanceRawScore = round_half_up(15 * cutDistanceRawScore)

    return beforeCutRawScore, afterCutRawScore, cutDistanceRawScore


def make_cut(f) -> Cut:
    c = Cut()
    c.speedOK = decode_bool(f)
    c.directionOk = decode_bool(f)
    c.saberTypeOk = decode_bool(f)
    c.wasCutTooSoon = decode_bool(f)
    c.saberSpeed = decode_float(f)
    c.saberDirection = [decode_float(f) for _ in range(3)]
    c.saberType = decode_int(f)
    c.timeDeviation = decode_float(f)
    c.cutDeviation = decode_float(f)
    c.cutPoint = [decode_float(f) for _ in range(3)]
    c.cutNormal = [decode_float(f) for _ in range(3)]
    c.cutDistanceToCenter = decode_float(f)
    c.cutAngle = decode_float(f)
    c.beforeCutRating = decode_float(f)
    c.afterCutRating = decode_float(f)
    return c


class Wall(JSONable):
    id: int
    energy: float
    time: float
    spawnTime: float

    def json_dict(self):
        return self.__dict__


def make_walls(f) -> List[Wall]:
    wall_magic = decode_byte(f)
    if wall_magic != 3:
        raise BSException(f'Wall magic number must be 3, got "{wall_magic}" instead')
    return make_things(f, make_wall)


def make_wall(f) -> Wall:
    w = Wall()
    w.id = decode_int(f)
    w.energy = decode_float(f)
    w.time = decode_float(f)
    w.spawnTime = decode_float(f)
    return w


class Height(JSONable):
    height: float
    time: float

    def json_dict(self):
        return self.__dict__


def make_heights(f) -> List[Height]:
    height_magic = decode_byte(f)
    if height_magic != 4:
        raise BSException(f'Height magic number must be 4, got "{height_magic}" instead')
    return make_things(f, make_height)


def make_height(f) -> Height:
    h = Height()
    h.height = decode_float(f)
    h.time = decode_float(f)
    return h


class Pause(JSONable):
    duration: int
    time: float

    def json_dict(self):
        return self.__dict__


def make_pauses(f) -> List[Pause]:
    pause_magic = decode_byte(f)
    if pause_magic != 5:
        raise BSException(f'Pause magic number must be 5, got "{pause_magic}" instead')
    return make_things(f, make_pause)


def make_pause(f) -> Pause:
    p = Pause()
    p.duration = decode_long(f)
    p.time = decode_float(f)
    return p


class ControllerOffsets(JSONable):
    left: VRObject
    right: VRObject

    def json_dict(self):
        return self.__dict__

def make_controller_offsets(f) -> ControllerOffsets:
    controller_offset_magic = decode_byte(f)
    if controller_offset_magic != 6:
        raise BSException(f'ControllerOffsets magic number must be 6, got "{controller_offset_magic}" instead')
    c = ControllerOffsets()
    c.left = make_vr_object(f)
    c.right = make_vr_object(f)
    return c


class UserData(JSONable):
    key: str
    bytes: List[bytes]

    def json_dict(self):
        return self.__dict__


def make_user_datas(f) -> List[UserData]:
    user_data_magic = decode_byte(f)
    if user_data_magic != 7:
        raise BSException(f'UserData magic number must be 7, got "{user_data_magic}" instead')
    return make_things(f, make_user_data)


def make_user_data(f) -> UserData:
    u = UserData()
    u.key = decode_string(f)
    byte_count = decode_int(f)
    u.bytes = [f.read(decode_byte(f)) for _ in range(byte_count)]
    return u


class Bsor(JSONable):
    magic_numer: int
    file_version: int
    info: Info
    frames: List[Frame]
    notes: List[Note]
    walls: List[Wall]
    heights: List[Height]
    pauses: List[Pause]
    controller_offsets: ControllerOffsets
    user_data: List[UserData]

    def json_dict(self):
        return self.__dict__


def make_bsor(f: typing.BinaryIO) -> Bsor:
    m = Bsor()

    m.magic_numer = decode_int(f)
    if hex(m.magic_numer) != MAGIC_HEX:
        raise BSException(f'File magic number must be {MAGIC_HEX}, got "{hex(m.magic_numer)}" instead.')
    m.file_version = decode_byte(f)

    if m.file_version > MAX_SUPPORTED_VERSION:
        logging.warning(f'File is version {m.file_version} and might not be compatible or not use all features'
                        f', highest supported version is {MAX_SUPPORTED_VERSION}')
    m.info = make_info(f)
    m.frames = make_frames(f)
    m.notes = make_notes(f)
    m.walls = make_walls(f)
    m.heights = make_heights(f)
    m.pauses = make_pauses(f)
    if f.peek(1):
        m.controller_offsets = make_controller_offsets(f)
        m.user_data = make_user_datas(f)
    else:
        m.controller_offsets = []
        m.user_data = []
    return m

