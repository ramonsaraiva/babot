import os

API_TOKEN = os.environ['BABOT_TOKEN']

DEFAULT_REPLY = 'Can\'t understand you :('
ERRORS_TO = 'babot-testing'

PLUGINS = [
    'slackbot.plugins',
    'commands.subway'
]
