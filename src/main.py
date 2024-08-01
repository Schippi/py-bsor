from bsor.Bsor import make_bsor, encode_bsor
from bsor.Scoring import calc_stats
import os

if __name__ == '__main__':
    filename = 'test.bsor'
    output_filename = 'test_out.bsor'
    
    print('File name :    ', os.path.basename(filename))
    
    with open(filename, 'rb') as f:
        m = make_bsor(f)
        print(f'BSOR Version: {m.file_version}')
        print(f'BSOR notes: {len(m.notes)}')
        print(m.info)
        stats = calc_stats(m)
        print(stats)
    
    # Save the Bsor object to a new file
    with open(output_filename, 'wb') as f_out:
        m.info.platform = 'steam'
        encode_bsor(f_out, m)
    
    print(f'BSOR saved to {output_filename}')