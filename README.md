# BS Open Replay Python parser

[Beat Saber Open Replay format](https://github.com/BeatLeader/BS-Open-Replay) parser written in Python

## Usage
```sh
pip install py-bsor
```

example - read bsor file and print some info:
```python
from bsor.Bsor import make_bsor
from bsor.Scoring import calc_stats
import os
import io

if __name__ == '__main__':
    filename = 'D:/something/easy.bsor'
    print('File name :    ', os.path.basename(filename))
    with open(filename, 'rb') as f:
        m = make_bsor(f)
        print(f'BSOR Version: {m.file_version}')
        print(f'BSOR notes: {len(m.notes)}')
        print(m.info)
        stats = calc_stats(m)
        print(stats)
        
        
        #change player and write to file
        m.info.playerId = 5
        m.info.playerName = 'testUser'
        with open('D:/_TMP/easy.testx', 'wb') as fo:
            m.write(fo)

```

build:
```sh
git tag x 
git push origin --tags
py build
py -m twine upload --repository pypi .\dist\*x*
```