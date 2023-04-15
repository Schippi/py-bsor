from bsor.Bsor import *
from bsor.Scoring import *

if __name__ == '__main__':
    import os
    filename = 'D:/_TMP/76561198026425351-ExpertPlus-Standard-09FD6D30C55F6D721AB75A10FD412A1A1037F9A9.bsor'
    print('File name :    ', os.path.basename(filename))
    try:
        with open(filename, "rb") as f:
            m = make_bsor(f)
            stats = calc_stats(m)
            print('BSOR Version: %d' % m.file_version)
            print('BSOR notes: %d' % len(m.notes))
            print('BSOR stats: %s' % stats)
            bad,miss,bomb = [0,0],[0,0],0
            #print(str(m))
            #write it to file
            with open('D:/_TMP/76561198026425351-ExpertPlus-Standard-09FD6D30C55F6D721AB75A10FD412A1A1037F9A9.txt','w') as f:
                f.write(str(stats))

            for n in m.notes:
                if n.event_type == NOTE_EVENT_BAD:
                    bad[n.cut.saberType] = bad[n.cut.saberType] + 1
                    pass
                elif n.event_type == NOTE_EVENT_MISS:
                    miss[n.colorType] = bad[n.colorType] + 1
                    pass
                elif n.event_type == NOTE_EVENT_BOMB:
                    bomb = bomb + 1
                    pass
                if n.score > 0:
                    index = n.lineIndex + 4*n.noteLineLayer
                    if index > 11 or index < 0:
                        index = 0

            combo = 0
            score_events = [(n.event_time,n) for n in m.notes]
            score_events.extend([(w.time,w) for w in m.walls])
            sorted_events = sorted(score_events,key=lambda x: x[0])
            max_score = 0
            multiplier = 1
            mul_progress = 0
            mul_max_progress = 2
            score = 0
            note_cnt = 0
            #increases the mulpiplier
            def inc_mul(i, progress, max_progress):
                if i >= 8:
                    return i, progress, max_progress
                if progress < max_progress:
                    progress = progress + 1
                if progress >= max_progress:
                    i = i*2
                    progress = 0
                    max_progress = i * 2
                return i, progress, max_progress
            #decreases the mulpiplier
            def dec_mul(i, progress, max_progress):
                progress = 0
                if i > 1:
                    i = i//2
                max_progress = i * 2
                return i, progress, max_progress
            sco_x = []
            scores =[]
            for e in sorted_events:
                if isinstance(e[1],Note):
                    note_cnt = note_cnt + 1
                    max_mul = 8 if note_cnt > 8+4+2 else 4 if note_cnt > 4+2 else 2 if note_cnt > 2 else 1
                    if e[1].scoringType == NOTE_SCORE_TYPE_BURSTSLIDERELEMENT:
                        max_score = max_score + max_mul * 20
                    elif e[1].scoringType == NOTE_SCORE_TYPE_BURSTSLIDERHEAD:
                        max_score = max_score + max_mul * 85
                    else:
                        max_score = max_score + max_mul * 115
                if isinstance(e[1],Wall) or isinstance(e[1],Note) and e[1].score == 0:
                    multiplier,mul_progress,mul_max_progress = dec_mul(multiplier,mul_progress,mul_max_progress)
                    combo = 0
                else:
                    multiplier,mul_progress,mul_max_progress = inc_mul(multiplier,mul_progress,mul_max_progress)
                    combo = combo + 1
                    score = score + multiplier * e[1].score
                sco_x.append(e[1].event_time)
                scores.append(score)
            percent = score / max_score
            print('%d / %d' % (score, max_score))
            print('%.2f' %(percent*100))
            import plotly.graph_objects as go
            fig = go.Figure(data = [
                go.Scatter(x=sco_x, y=scores)
            ])
            fig.show()


    finally:
        pass
    n115 = [n for n in m.notes if n.acc_score == 15]
    n114 = [n for n in m.notes if n.acc_score == 15]
    n113 = [n for n in m.notes if n.acc_score == 15]
    import plotly
    cut = m.notes[1].cut
    import numpy as np
    centroid = np.array(cut.cutNormal)
    target = np.array([0,0,0])

    def parametric_line_equations(start_point, end_point):
        position_vector = start_point
        direction_vector = end_point - start_point
        print('Parametric line equation: [x, y, z, ...] = {} + t * {}'.format(position_vector, direction_vector))
        print('Normal vector : {}'.format(direction_vector))
        return position_vector, direction_vector

    position_vector, normal_vector = parametric_line_equations(centroid, target)

    def perpendicular_plane_equation(normal_vector, position_vector):
        weights = normal_vector
        bias = np.matmul(normal_vector, position_vector)
        return weights, bias

    import numpy as np
    weights, bias = perpendicular_plane_equation(cut.cutNormal, np.multiply(cut.cutNormal,cut.cutDistanceToCenter))
    import plotly.graph_objects as go


    x = np.linspace(-10,10,200)
    y = np.linspace(-10,10,200)

    X,Y = np.meshgrid(x,y)
    Z = (bias - weights[0]*X - weights[1]*Y) / weights[2]

    fig = go.Figure(data = [
        go.Surface(x = X,y = Y,z = Z)
        ,go.Scatter3d(x=[0], y=[0], z=[0])
    ])
    fig.update_layout(scene = dict(
        xaxis = dict(nticks=4, range=[-10,10],),
        yaxis = dict(nticks=4, range=[-10,10],),
        zaxis = dict(nticks=4, range=[-10,10],),),
    )
    fig.show()
