import re

from slackbot.bot import respond_to
from slackbot.bot import listen_to

import requests
from bs4 import BeautifulSoup as BS

from models import (
    session,
    BairesUser
)

TT_LOGIN_URL = 'http://timetracker.bairesdev.com/default.aspx' 
TT_TRACK_URL = 'http://timetracker.bairesdev.com/CargaTimeTracker.aspx'

def no_tt_account(message):
    '''
    Message displayed when a command that needs a
    TimeTracker account is used by a unregistered user.
    '''
    message.reply(('You don\'t have any account registered yet\n'
                   '> Send me a private message with '
                   '`tt account user password` to create it'))


def timetracker_fetch_login_page(session):
    '''
    Gets all needed data to submit a login form.
    That includes hidden inputs and the usual login data, since
    if we don't send these hidden values, the server won't
    accept our POST request
    '''
    req = session.get(TT_LOGIN_URL)
    markup = BS(req.text, 'html.parser')

    HIDDEN_INPUT_NAMES = (
        '__EVENTTARGET',
        '__EVENTARGUMENT',
        '__VIEWSTATE',
        '__VIEWSTATEGENERATOR',
        '__EVENTVALIDATION'
    )

    FORM_INPUT_TYPE_VALUES = (
        'text',
        'password',
        'submit'
    )

    data = {}

    # resolve all values from hidden inputs
    for input in HIDDEN_INPUT_NAMES:
        try:
            data[input] = markup.find('input', {'name': input})['value']
        except TypeError:
            data[input] = ''

    # resolve all names from login input types
    for input_type in FORM_INPUT_TYPE_VALUES:
        element = markup.find('input', {'type': input_type})
        value = element.get('value', None)
        data[element['name']] = value or input_type

    return data


def timetracker_login(session, baires_user):
    '''
    Logs in to the timetracker application and returns
    the following request, unless it is the login page,
    meaning that the login failed.
    '''
    data = timetracker_fetch_login_page(session)
    username_key = [key for key in data if 'UserName' in key][0]
    password_key = [key for key in data if 'Password' in key][0]
    data[username_key] = baires_user.user
    data[password_key] = baires_user.password

    response = session.post(TT_LOGIN_URL, data=data)

    # ListaTimeTracker should be the redirect when logged in
    if 'ListaTimeTracker' not in response.url:
        return None
    return response


def login(slack_user):
    baires_user = BairesUser.get_slack_user(slack_user)
    if not baires_user:
        return None

    session = requests.session()
    response = timetracker_login(session, baires_user)

    if not response:
        return None

    return baires_user, session, response


def timetracker_check(markup):
    '''
    Checks the latest TimeTracker submission and the
    amount of hours submitted in the current month.
    If the number of rows is <= 1, means that no hours
    have been submitted for this month, cause the table
    will only output one row for a generic message.
    '''
    results_table = markup.find('table', {'class': 'tbl-respuestas'})
    rows = results_table.findAll('tr')

    if len(rows) > 1:
        last_submit = rows[-2].findAll('td')
        last_date = last_submit[0].find('font').text
        last_hours = last_submit[1].find('font').text
        last_description = last_submit[4].find('font').text
        hours_submitted = rows[-1].findAll('td')[1].text
        return (last_date, last_hours, last_description), hours_submitted
    return None


def timetracker_focalpoints(session):
    '''
    Returns a list of all focal points available
    in the track worked hours form
    '''
    response = session.get(TT_TRACK_URL)
    markup = BS(response.text, 'html.parser')
    select_name = 'ctl00$ContentPlaceHolder$idFocalPointClientDropDownList'

    options = markup.find('select', {'name': select_name}).findAll('option')
    import pdb; pdb.set_trace()
    return ((opt['value'], opt.text) for opt in options)


@respond_to(r'^tt account (.*) (.*)', re.IGNORECASE)
def tt_account(message, user, password):
    '''
    Creates or updates a TimeTracker account
    for a slack username.
    '''
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


@respond_to(r'^tt account$')
@listen_to(r'^babot tt account$')
def tt_account_info(message):
    '''
    Gives information about a TimeTracker account
    for a slack username.
    '''
    baires_user = BairesUser.get_slack_user(message.body['user'])
    if not baires_user:
        return no_tt_account(message)

    msg =  ('Your registered Baires account: `{}`\n'
            '> Send me a private message with '
            '`tt account user password` to update it')
    message.reply(msg.format(baires_user.user))


@respond_to(r'^tt check$')
@listen_to(r'^babot tt check$')
def tt_check(message):
    '''
    Checks the latest TimeTracker submission and the
    amount of hours submitted in the current month.
    '''
    login_response = login(message.body['user']) 
    if not login_response:
        return no_tt_account()

    user, session, response = login_response

    markup = BS(response.text, 'html.parser')
    check = timetracker_check(markup)

    if not check:
        message.reply('No tracked hours in this month!')
        return

    last_submit, hours_submitted = check

    msg = ('\n> Latest TimeTracker submission: *{}* | *{} hours* | *{}*\n'
           '> Tracked hours this month: *{}*')
    message.reply(msg.format(
        last_submit[0], last_submit[1], last_submit[2], hours_submitted))


@respond_to(r'^tt focalpoints$')
@listen_to(r'^babot tt focalpoints$')
def tt_focalpoints(message):
    '''
    Returns a list of all focal points available
    in the track worked hours form
    '''
    login_response = login(message.body['user'])
    if not login_response:
        return no_tt_account()

    user, session, response = login_response

    focalpoints = timetracker_focalpoints(session)
    msg = 'Available focalpoints:\n'
    msg += '\n'.join(
        ['> {} => {}'.format(fp[0], fp[1]) for fp in focalpoints])

    message.reply(msg)
