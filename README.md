# BS Open Replay Python parser

[Beat Saber Open Replay format](https://github.com/BeatLeader/BS-Open-Replay) parser written in Python

## Usage
```python
from Bsor import make_bsor
import os

if __name__ == '__main__':
    filename = 'D:/something/easy.bsor'
    print('File name :    ', os.path.basename(filename))
    try:
      with open(filename, "rb") as f:
          m = Bsor.make_bsor(f)
          print('BSOR Version: %d' % m.file_version)
          print('BSOR notes: %d' % len(m.notes))
    except BSException as e:
      raise
