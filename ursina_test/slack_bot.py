import asyncio
import re
from slack import RTMClient
from slack import WebClient
from slack.errors import SlackApiError
import threading
from typing import Dict

SLACK_TOKEN = open('slack_bot_token.txt').read().strip()
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

objects = None

# A cached list of users for id->name lookup
users_list = {}

# The thread that the slack bot is running in
thread = None


def init(ursina_objects):
    global thread, objects, web_client, users_list
    objects = ursina_objects
    thread = SlackThread()
    thread.start()
    web_client = WebClient(SLACK_TOKEN)
    users = web_client.users_list()
    for member in users.data['members']:
        users_list[member['id']] = member
    return


def stop():
    global thread
    thread.stop()
    return


def user_info() -> Dict[str, str]:
    info = {}
    for user_id in users_list.keys():
        user = users_list[user_id]
        if 'real_name' in user and not user.get('deleted', True):
            info[user['name']] = user['real_name']
    return info


# It does not look like there is a way to have this be a member of SlackThread, since 'self' will never
# be passed to the method
@RTMClient.run_on(event='message')
@RTMClient.run_on(event='app_mention')
def handle_message(**payload):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    text = data.get('text', '')
    give_matches = re.search(r'give\s<@(?P<give_to>\S*)>\s(?P<how_much>[0-9]+)', text)
    if give_matches:
        name_from = users_list[data['user']]['name']
        name_to = users_list[give_matches.group('give_to')]['name']
        points = int(give_matches.group('how_much'))
        print(f'Giving {points} from {name_from} to {name_to}')
        objects['cheer_scoreboard'].transfer_points(name_from, name_to, points)
    return


class SlackThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._running = False
        self._bot_id = None
        self._loop = asyncio.new_event_loop()
        return

    def run(self):
        self._running = True
        asyncio.set_event_loop(self._loop)
        rtm_client = RTMClient(token=SLACK_TOKEN)
        # rtm_client.start() does not like being run in a thread,
        # so just do the parts of it that work in a thread manually....
        future = asyncio.ensure_future(rtm_client._connect_and_read(), loop=self._loop)
        self._loop.run_until_complete(future)
        return

    def stop(self) -> None:
        self._loop.stop()
        self.join()
        return
