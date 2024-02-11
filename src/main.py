from bsor.Bsor import make_bsor
from bsor.Scoring import calc_stats
import logging

if __name__ == '__main__':
    import os
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    logging.info('Started')

    # example, read basic info from bsor file
    filename = 'D:/_TMP/easy.bsor'
    print(f'File name :    {os.path.basename(filename)}')
    with open(filename, "rb") as f:
        m = make_bsor(f)
        stats = calc_stats(m)
        print(f'BSOR Version:  {m.file_version}')
        print(f'BSOR notes: {len(m.notes)}')
        print(f'BSOR stats: {stats}')

    from bsor.BsorUtil import *
    #my_score = download_Bsor(787433)
    #print(my_score)

    my_playlist = clan_playlist('GER', unplayed_player=76561198026425351, stars_from=3, stars_to=9, include_to_hold=False);
    with open('D:/_TMP/GER.bplist', 'w') as f:
        f.write(json.dumps(my_playlist, indent=2))
    print(my_playlist)
