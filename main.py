#!/bin/python

import requests
from datetime import datetime
import click
import logging
import subprocess

CAMBLY_URL = 'https://www.cambly.com/'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'

HEADERS = {
    'user-agent': UA,
    'referer': CAMBLY_URL,
}
CHATS_URL = CAMBLY_URL + 'api/chats'
TUTORS_URL = CAMBLY_URL + 'api/tutors'
USER_URL = CAMBLY_URL + 'api/users/current'
CHUNK_SIZE = 1 * 1024 * 1024 # 1MB

class CamblyDownloader(object):
    def __init__(self, session_id, dt, verbose):
        self._init_logger(verbose)
        self._debug("init")

        self.cookie = {'session': session_id}
        self.user_id = self._get_user_id()
        self.download_after = dt

    def _init_logger(self, verbose):
        self.logger = logging.getLogger(__name__)
        level = logging.DEBUG if verbose else logging.INFO
        self.logger.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)

    def _debug(self, msg):
        self.logger.debug(msg)

    def _get(self, url, params={}):
        r = requests.get(url, headers=HEADERS, cookies=self.cookie, params=params)
        if r.status_code == 200:
            return r.json()['result']

    def _get_user_id(self):
        self._debug("Get user id")
        r = self._get(USER_URL)
        return r['username']

    def get_chat_list(self):
        self._debug("Get chat list after {}".format(self.download_after))
        params = {
            'language': 'en',
            'userId': self.user_id, 
            'state': 2,
            'role': 'student',
            'sort': '-1',
            'limit': '50',
            'viewAs': 'student',
        }
    
        r = self._get(CHATS_URL, params)
        chats = []
        tutor_ids = []
        for chat in r:
            tutor_id = chat['tutor']
            start_time = datetime.fromtimestamp(chat['startTime'])
            video_url = chat['videoURL']

            if self.download_after and start_time < self.download_after:
                continue
    
            tutor_ids.append(tutor_id)
            chats.append({
                "tutor_id": tutor_id,
                "video_url": video_url,
                "start_time": start_time,
            })
        return tutor_ids, chats

    def get_tutors(self, ids):
        self._debug("Get tutor list")
        params = "&".join(["ids[]={}".format(id) for id in ids])
        tutors = {}
        r = self._get(TUTORS_URL, params)
        for tutor_id, tutor in r.items():
            tutors[tutor_id] = tutor['displayName']
    
        return tutors

    def _save_video(self, file_name, video_url):
        self._debug("Save video {}".format(video_url))
        click.secho(file_name, fg='green')
        p = subprocess.run(["wget", "-t", "0", "-q", "-O", file_name, "-c", video_url, '--show-progress', '-T', '30', '--user-agent', UA])
        p.check_returncode()


    def _save_video2(self, file_name, video_url):
        self._debug("Save video {}".format(video_url))
        with requests.get(video_url, stream=True, headers=HEADERS) as r:
            r.raise_for_status()
            total_size = int(r.headers['Content-length'])
            with open(file_name, 'wb') as f:
                current_size = 0
                with click.progressbar(length=total_size,
                       label='Downloading {}'.format(file_name)) as bar:
                    for chunk in r.iter_content(): 
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        #if chunk: 
                        f.write(chunk)
                        bar.update(len(chunk))
                        # bar.update(CHUNK_SIZE)

    
    def download_videos(self):
        self._debug("Downloading videos")
        tutor_ids, chats = self.get_chat_list()
        tutors = self.get_tutors(tutor_ids)
        idx_dict = {}
        self._debug("{} videos need to download".format(len(chats)))
        for chat in chats:
            tutor = tutors[chat['tutor_id']].replace(" ", '.')
            video_url = chat['video_url']
            start_time = chat['start_time'].strftime("%Y-%m-%d")

            tutor_key = "{}.{}".format(tutor, start_time)

            if tutor_key not in idx_dict:
                idx_dict[tutor_key] = 0
            else:
                idx_dict[tutor_key] = idx_dict[tutor_key] + 1

            idx = idx_dict.get(tutor_key)
            suffix = "" if idx == 0 else ".{}".format(idx)
            file_name = "{date}_{tutor}{suffix}.mp4".format(
                    tutor=tutor,
                    date=start_time,
                    suffix=suffix)
            self._save_video(file_name, video_url)


@click.command()
@click.option('-s', '--session', 'session_id', help='Your session id', required=True, type=str)
@click.option('-d', '--date', help='Download videos after this date', type=click.DateTime(formats=["%Y%m%d", "%Y-%m-%d"]))
@click.option('-v', '--verbose', help='Show debug messages.', is_flag=True)
def cli(session_id, date, verbose):
    d = CamblyDownloader(
        session_id=session_id,
        dt=date,
        verbose=verbose
    )
    d.download_videos()


if __name__ == '__main__':
    cli()
