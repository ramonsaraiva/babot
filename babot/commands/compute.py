import os
import re

from subprocess import (
    Popen,
    PIPE
)
from tempfile import NamedTemporaryFile

from slackbot.bot import respond_to
from slackbot.bot import listen_to

@listen_to(r'^babot compute (.*)', re.IGNORECASE)
def eval(message, string):
    string = string.encode('UTF-8')
    string = string.replace(
        b'\xe2\x80\x98', b"'").replace(b'\xe2\x80\x99', b"'")

    temp = NamedTemporaryFile(delete=False)
    temp.write(string)
    temp.close()

    command = 'python {}'.format(temp.name)
    process = Popen(command.split(), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    exploded = process.wait()

    os.unlink(temp.name)

    response = stderr if exploded else stdout
    message.reply(response)
