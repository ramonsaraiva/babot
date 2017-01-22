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
                   '`baires account user password` to create it'))


@respond_to(r'^baires account (.*) (.*)', re.IGNORECASE)
def baires_account(message, user, password):

    baires_user = BairesUser.get_slack_user(message.body['user'])
    if baires_user:
        baires_user.user = user
        baires_user.password = password
        session.object_session(baires_user).commit()
        message.reply(
            'Your Baires account `{}` was updated successfully'.format(
                baires_user.user))
        return

    s = session()
    baires_user = BairesUser(message.body['user'], user, password)
    s.add(baires_user)
    s.commit()
    message.reply(
        'Your Baires account `{}` was created successfully'.format(
            baires_user.user))


@respond_to(r'^baires account$')
@listen_to(r'^babot baires account$')
def baires_account_info(message):
    baires_user = BairesUser.get_slack_user(message.body['user'])
    if baires_user:
        msg =  ('Your registered Baires account: `{}`\n'
                '> Send me a private message with '
                '`baires account user password` to update it')
        message.reply(msg.format(baires_user.user))
    else:
        no_baires_account(message)
