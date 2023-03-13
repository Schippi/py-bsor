from Bsor import *
import json


def inc_mul(i, progress, max_progress):
    if i >= 8:
        return i, progress, max_progress
    if progress < max_progress:
        progress = progress + 1
    if progress >= max_progress:
        i = i * 2
        progress = 0
        max_progress = i * 2
    return i, progress, max_progress


# decreases the mulpiplier
def dec_mul(i, progress, max_progress):
    progress = 0
    if i > 1:
        i = i // 2
    max_progress = i * 2
    return i, progress, max_progress

def get_at_time(time: float, stat: List[Tuple], default: Any =(0.0, 0)) -> Tuple[float, Any]:
    result = default
    for t, s in stat:
        if t > time:
            return result
        result = (time, s)


class ScoreStats:
    #all lists should be sorted by time
    events: List[Union[Note, Wall]] = []
    score_at_time: List[Tuple[float, int]] = []
    max_score_at_time: List[Tuple[float, int]] = []
    bomb_hit_at_time: List[Tuple[float, int]] = []
    wall_hit_at_time: List[Tuple[float, int]] = []
    miss_at_time: List[Tuple[float, List[int]]] = []
    bad_hit_at_time: List[Tuple[float, List[int]]] = []

    def __str__(self):
        return json.dumps({
            "score": self.end_score,
            "max_score": self.max_score,
            "score_percent": self.score_percent,
            "misses": {'left': self.misses[0], 'right': self.misses[1]},
            "bad_hits": {'left': self.bad_hits[0], 'right': self.bad_hits[1]},
            "bomb_hits": self.bomb_hits,
            "wall_hits": self.wall_hits
        })

    @property
    def end_score(self) -> float:
        return self.score_at_time[-1][1]

    @property
    def max_score(self) -> float:
        return self.max_score_at_time[-1][1]

    @property
    def score_percent(self) -> float:
        return self.end_score / self.max_score

    @property
    def bomb_hits(self) -> int:
        if len(self.bomb_hit_at_time) == 0:
            return 0
        return self.bomb_hit_at_time[-1][1]

    @property
    def wall_hits(self) -> int:
        if len(self.wall_hit_at_time) == 0:
            return 0
        return self.wall_hit_at_time[-1][1]

    @property
    def misses(self) -> List[int]:
        if len(self.miss_at_time) == 0:
            return [0, 0]
        return self.miss_at_time[-1][1]

    @property
    def bad_hits(self) -> List[int]:
        if len(self.bad_hit_at_time) == 0:
            return [0, 0]
        return self.bad_hit_at_time[-1][1]

    def get_score_at_time(self, time: float) -> Tuple[float, int]:
        return get_at_time(time, self.score_at_time)

    def get_max_score_at_time(self, time: float) -> Tuple[float, int]:
        return get_at_time(time, self.max_score_at_time)

    def get_bomb_hit_at_time(self, time: float) -> Tuple[float, int]:
        return get_at_time(time, self.bomb_hit_at_time)

    def get_wall_hit_at_time(self, time: float) -> Tuple[float, int]:
        return get_at_time(time, self.wall_hit_at_time)

    def get_miss_at_time(self, time: float) -> Tuple[float,List[int]]:
        return get_at_time(time, self.miss_at_time, (0.0, [0, 0]))

    def get_bad_hit_at_time(self, time: float) -> Tuple[float,List[int]]:
        return get_at_time(time, self.bad_hit_at_time, (0.0, [0, 0]))

    def get_percent_at_time(self, time: float) -> Tuple[float, float]:
        t, s = self.get_score_at_time(time)
        return t, s / self.get_max_score_at_time(time)[1]



def calc_stats(m: Bsor) -> ScoreStats:
    result = ScoreStats()
    bad, miss = [0, 0], [0, 0]
    bomb_hits = 0
    wall_hits = 0

    combo = 0
    score_events: list[tuple[float, Any]] = [(n.event_time, n) for n in m.notes]
    score_events.extend([(w.time, w) for w in m.walls])
    result.events = sorted(score_events, key=lambda x: x[0])
    max_score = 0
    multiplier = 1
    mul_progress = 0
    mul_max_progress = 2
    score = 0
    note_cnt = 0
    sco_x = []
    scores = []
    for e in result.events:
        if isinstance(e[1], Note):
            #calculate max score
            note_cnt = note_cnt + 1
            max_mul = 8 if note_cnt > 8 + 4 + 2 else 4 if note_cnt > 4 + 2 else 2 if note_cnt > 2 else 1
            if e[1].scoringType == NOTE_SCORE_TYPE_BURSTSLIDERELEMENT:
                max_score = max_score + max_mul * 20
            elif e[1].scoringType == NOTE_SCORE_TYPE_BURSTSLIDERHEAD:
                max_score = max_score + max_mul * 85
            else:
                max_score = max_score + max_mul * 115

            result.max_score_at_time.append((e[1].event_time, max_score))

            if e[1].event_type == NOTE_EVENT_BAD:
                bad[e[1].cut.saberType] = bad[e[1].cut.saberType] + 1
                result.bad_hit_at_time.append((e[1].event_time, bad.copy()))
            elif e[1].event_type == NOTE_EVENT_MISS:
                miss[e[1].colorType] = miss[e[1].colorType] + 1
                result.miss_at_time.append((e[1].event_time, miss.copy()))
            elif e[1].event_type == NOTE_EVENT_BOMB:
                bomb_hits = bomb_hits + 1
                result.bomb_hit_at_time.append((e[1].event_time, bomb_hits))
        elif isinstance(e[1], Wall):
            wall_hits = wall_hits + 1
            result.wall_hit_at_time.append((e[1].event_time, wall_hits))
        if isinstance(e[1], Wall) or isinstance(e[1], Note) and e[1].score == 0:
            multiplier, mul_progress, mul_max_progress = dec_mul(multiplier, mul_progress, mul_max_progress)
            combo = 0
        else:
            multiplier, mul_progress, mul_max_progress = inc_mul(multiplier, mul_progress, mul_max_progress)
            combo = combo + 1
            score = score + multiplier * e[1].score
        sco_x.append(e[1].event_time)
        scores.append(score)

    result.score_at_time = list(zip(sco_x, scores))

    return result
