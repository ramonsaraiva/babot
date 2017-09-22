import arrow

from slackbot.bot import respond_to
from slackbot.bot import listen_to

import requests
from bs4 import BeautifulSoup as BS


def scrap_subway_lines():
    '''
    Scraps from enelsubte the current status for all
    subway lines in Buenos Aires.
    '''
    URL = 'http://enelsubte.com/estado/'
    request = requests.get(URL)
    markup = BS(request.text, 'html.parser')

    subway_status = []
    updated_at = None

    status_table = markup.find('table', {'id': 'tabla-estado'})
    for subway_line in status_table.findAll('tr'):
        try:
            name_markup, status_markup = subway_line.findAll('td')
            name = name_markup.find('div').text
            status = status_markup.findAll('div')[0].text
            subway_status.append((name, status))
        except ValueError:
            '''
            This exception occurs in the last <tr> that does not have
            two <td>'s to unpack, that means it is the update time row.
            '''
            updated_at = subway_line.find('td').find('span')['title']
    return subway_status, updated_at


@listen_to('babot subway')
@respond_to('subway')
def subway(message):
    '''
    Shows the current status for all subway lines
    in Buenos Aires
    '''
    subway_status, updated_at = scrap_subway_lines()

    # Highlights non-normal subway status
    format_status = (
        lambda status: '`{}`'.format(status)
        if status != 'Normal' else status)

    output = 'Subway status for now!\n> '

    # All subway lines should be blockquoted for better reading
    output += '\n> '.join(
        ['*{}* => {}'.format(subway_line[0], format_status(subway_line[1]))
            for subway_line in subway_status])

    output += '`\nUpdated {}'.format(arrow.get(updated_at).humanize())

    message.react('metro')
    message.reply(output)
