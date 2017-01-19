from slackbot.bot import respond_to
from slackbot.bot import listen_to

import requests
from bs4 import BeautifulSoup as BS

@listen_to('babot subway')
@respond_to('subway')
def subway(message):
    URL = 'http://enelsubte.com/estado/'
    request = requests.get(URL)
    markup = BS(request.text, 'html.parser')

    status_table = markup.find('table', {'id': 'tabla-estado'})
    subway_status = []
    updated_at = ''
    for subway_line in status_table.findAll('tr'):
        try:
            name_markup, status_markup = subway_line.findAll('td')
            name = name_markup.find('div').text
            status = status_markup.findAll('div')[0].text
            subway_status.append((name, status))
        except ValueError:
            updated_at = subway_line.find('td').find('span')['title']

    output = 'Subway status for today!\n> '
    format_status = (lambda status: '`{}`'.format(status)
        if status != 'Normal' else status)

    output += '\n> '.join(
        ['*{}* => {}'.format(sl[0], format_status(sl[1]))
            for sl in subway_status])

    message.react('metro')
    message.reply(output)
