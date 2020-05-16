import asyncio
import re
from slack import RTMClient
from slack import WebClient
from slack.errors import SlackApiError
import threading
from typing import Dict, List

SLACK_TOKEN = open('slack_bot_token.txt').read().strip()
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

objects = None

# A cached list of users for id->name lookup
users_list = {}

# The thread that the slack bot is running in
thread = None

# All of the available textures (set elsewhere)
cheers_textures = []


def init(ursina_objects, textures:List[str]):
    global thread, objects, web_client, users_list, cheers_textures
    objects = ursina_objects
    cheers_textures = textures
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


def help_text() -> str:
    s = 'Usage:\n'
    s += '@Scrum Bot give @<user> <points> <texture>\n'
    s += 'Currently available cheers textures:\n'
    for name in cheers_textures:
        s += f'- {name}\n'
    return s


# It does not look like there is a way to have this be a member of SlackThread, since 'self' will never
# be passed to the method
@RTMClient.run_on(event='message')
@RTMClient.run_on(event='app_mention')
def handle_message(**payload):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    text = data.get('text', '')
    give_matches = re.search(r'give\s<@(?P<give_to>\S*)>\s(?P<how_much>[0-9]+)\s*(?P<texture>\S*)?', text)
    if give_matches:
        name_from = users_list[data['user']]['name']
        name_to = users_list[give_matches.group('give_to')]['name']
        points = int(give_matches.group('how_much'))
        texture = give_matches.group('texture')
        print(f'Giving {points} from {name_from} to {name_to}')
        objects['cheer_scoreboard'].transfer_points(name_from, name_to, points, texture=texture)
    elif 'help' in text:
        text = help_text()
        channel_id = data['channel']
        thread_ts = data['ts']
        user = data['user']

        try:
            response = web_client.chat_postMessage(
                channel=channel_id,
                text=text,
                thread_ts=thread_ts
            )
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")

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
