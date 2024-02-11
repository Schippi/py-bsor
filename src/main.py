from bsor.Bsor import make_bsor
from bsor.Scoring import calc_stats

if __name__ == '__main__':
    import os

    # example, read basic info from bsor file
    filename = 'D:/_TMP/easy.bsor'
    print(f'File name :    {os.path.basename(filename)}')
    with open(filename, "rb") as f:
        m = make_bsor(f)
        stats = calc_stats(m)
        print(f'BSOR Version:  {m.file_version}')
        print(f'BSOR notes: {len(m.notes)}')
        print(f'BSOR stats: {stats}')
