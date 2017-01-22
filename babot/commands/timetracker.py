import re

from slackbot.bot import respond_to
from slackbot.bot import listen_to

import requests
from bs4 import BeautifulSoup as BS

from models import (
    session,
    BairesUser
)

def no_baires_account(message):
    message.reply(('You don\'t have any account registered yet\n'
                   '> Send me a private message with '
                   '`baires account email password` to create it'))


@respond_to(r'^baires account <mailto:(.+)\|\1> (.*)', re.IGNORECASE)
def baires_account(message, email, password):

    user = BairesUser.get_slack_user(message.body['user'])
    if user:
        user.email = email
        user.password = password
        session.object_session(user).commit()
        message.reply(
            'Your Baires account `{}` was updated successfully'.format(email))
        return

    s = session()
    user = BairesUser(message.body['user'], email, password)
    s.add(user)
    s.commit()
    message.reply(
        'Your Baires account `{}` was created successfully'.format(email))


@respond_to(r'^baires account$')
@listen_to(r'^babot baires account$')
def baires_account_info(message):
    user = BairesUser.get_slack_user(message.body['user'])
    if user:
        msg =  ('Your registered Baires account: `{}`\n'
                '> Send me a private message with '
                '`baires account email password` to update it')
        message.reply(msg.format(user.email))
    else:
        no_baires_account(message)
