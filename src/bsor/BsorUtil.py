from .Decoder import *
from .Bsor import *
import json
import requests
import io
import logging

logger = logging.getLogger(__name__)
def download_Bsor(id: int) -> Bsor:
    # Download the file from the server
    with requests.get(f'https://api.beatleader.xyz/score/{id}') as r:
        r.raise_for_status()
        parsed = json.loads(r.content)
        replay_location = parsed['replay']
    with requests.get(replay_location) as replay:
        replay.raise_for_status()
        return make_bsor(io.BufferedReader(io.BytesIO(replay.content)))

"""
    Get the playlist for a clan
    :param clan: the clan tag
    :param count: the number of songs to get, standard is 20
    :param imageb64: the base64 encoded image for the playlist, if None, it the clan-icon will be downloaded
    :param unplayed_player: the selected songs should not have been played by this player, optional 
    :param stars_from: the minimum stars for the songs, optional
    :param stars_to: the maximum stars for the songs, optional
    :param include_to_hold: include the to hold maps, if False only toConquer maps will be included
"""
def clan_playlist(clan: str, count: int = 20, imageb64: str = None, unplayed_player: int = None, stars_from: int = None, stars_to: int = None, include_to_hold: bool = False) -> dict:
    clan = clan[:5]
    playlist = {
        'playlistTitle': f'contested maps for {clan}',
        'playlistAuthor': 'Schippi',
        'songs': [],
        'image': imageb64
    }

    def song_from_data(d):
        return {
            'songName': d['leaderboard']['song']['name'],
            'levelAuthorName': d['leaderboard']['song']['author'],
            'hash': d['leaderboard']['song']['hash'],
            'levelid': 'custom_level_' + d['leaderboard']['song']['hash'],
            'difficulties': [
                {
                    'characteristic': d['leaderboard']['difficulty']['modeName'],
                    'name': d['leaderboard']['difficulty']['difficultyName'],
                }
            ]
        }

    def check_song(d):
        if len(playlist['songs']) >= count:
            return False
        if stars_from and d['leaderboard']['difficulty']['stars'] < stars_from:
            return False
        if stars_to and d['leaderboard']['difficulty']['stars'] > stars_to:
            return False
        if unplayed_player:
            p_s = f'https://api.beatleader.xyz/player/{unplayed_player}/scorevalue/{d["leaderboard"]["song"]["hash"]}/{d["leaderboard"]["difficulty"]["difficultyName"]}/{d["leaderboard"]["difficulty"]["modeName"]}'
            logger.info(p_s)
            with requests.get(p_s) as pr:
                if pr.status_code == 200:
                    if int(pr.content) > 0:
                        return False
        return True

    def get_image(parsed_response):
        if not imageb64:
            img_url = parsed_response['data'][0]['clan']['icon']
            try:
                with requests.get(img_url) as img:
                    img.raise_for_status()
                    import base64
                    content = io.BytesIO(img.content)
                    return base64.b64encode(content.read()).decode('utf-8')
            except:
                pass

    # Get the playlist from the server
    divisor = 2 if include_to_hold else 1
    page = 1
    while len(playlist['songs']) < count:
        s = f'https://api.beatleader.xyz/clan/{clan}/maps?page={page}&count={count//divisor}&sortBy=toconquer&order=0'
        logger.info(s)
        with requests.get(s) as r:
            r.raise_for_status()
            # Parse the JSON response
            parsed = json.loads(r.content)
            playlist['image'] = get_image(parsed)

            for d in parsed['data']:
                if check_song(d):
                    playlist['songs'].append(song_from_data(d))

        if include_to_hold:
            s = f'https://api.beatleader.xyz/clan/{clan}/maps?page={page}&count={count//divisor}&sortBy=tohold&order=0'
            logging.info(s)
            with requests.get(s) as r:
                r.raise_for_status()
                # Parse the JSON response
                parsed = json.loads(r.content)
                for d in parsed['data']:
                    if check_song(d):
                        playlist['songs'].append(song_from_data(d))
        logger.info(f'songs in playlist after page {page}: {len(playlist["songs"])}')
        page += 1

    return playlist
    # and return the playlist
