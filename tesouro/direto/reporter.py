# coding: utf-8

import argparse
import json
import re
import smtplib
import yaml

from datetime import date
from email.mime.text import MIMEText
from jinja2 import Environment, PackageLoader

from client import TDClient


images = {
    '114544':
        'https://www.rico.com.vc/Util/Image/cabecalho/logo-rico-main.png',
    '662481':
        ('https://www.itau.com.br/_arquivosestaticos/Itau/'
         'defaultTheme/img/logo-itau.png'),
}


def format(number):
    return '%.2f' % number


def get_image(brokerage):
    match = re.match('^(\d+) ', brokerage)
    if match:
        return images[match.group(1)]


def diff_color(new, old):
    # TODO: in some fields if the value goes down (lke taxes), we might
    # want to invert the colors.
    positive = new > old
    diff = '%s%.2f' % ('+' if positive else '', new-old)
    color = 'green' if positive else 'red'

    return '(<span style="color: %s">%s</span>)' % (color, diff)


def diff(field, new, old):
    assert field in new
    new = new[field]

    # Check if old value is valid, or return new value
    if old is None or field not in old:
        return format(new)
    old = old[field]

    # Compare both values to determine some difference
    if isinstance(new, float) and isinstance(old, float) and new != old:
        return '%.2f %s' % (new, diff_color(new, old))
    return format(new)


class Email(object):

    def __init__(self, config):
        self.config = config

    def send_diff(self, old, new):
        environment = Environment(loader=PackageLoader('td', 'templates'))
        environment.filters['diff'] = diff
        environment.filters['format'] = format
        environment.filters['get_image'] = get_image
        template = environment.get_template('email.html')

        text = template.render(new=new, old=old, images=images)

        # Create message container
        msg = MIMEText(text, 'html', 'utf-8')
        msg['Subject'] = "Atualizações Tesouro Direto"
        msg['From'] = self.config['from']
        msg['To'] = self.config['to']

        # Send the message via SMTP server
        port = self.config.get('port', 23)
        s = smtplib.SMTP(self.config['server'], port)
        s.login(self.config['username'], self.config['password'])
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()


class Reporter(object):

    def run_cli(self):
        # Parse arguments (config file location)
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--config", default="config.yml",
                            help="path to configuration file")
        args = parser.parse_args()

        # Load configuration
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)

        self.report(config)

    def report(self, config):
        # Get data
        prev = self._get_current_data()
        data = self._get_new_data(config['bmfbovespa'])

        # Build email
        email = Email(config['smtp'])
        email.send_diff(prev, data)

        # Save new data to disk
        self._save_data(data)

    def _get_current_data(self):
        """Returns the current saved data."""
        try:
            with open('data.json', 'r') as f:
                data = f.read()
            return json.loads(data)
        except IOError:
            return None

    def _get_new_data(self, config):
        # Build client and login
        client = TDClient()
        client.login(cpf=config['cpf'], password=config['password'])

        # Get titles and their details
        info = client.get_titles(date.today().month, date.today().year)
        for brokerage, titles in info.iteritems():
            for name, data in titles.iteritems():
                data['details'] = client.get_title_details(name, data)

        # Logout and return
        client.logout()
        return info

    def _save_data(self, titles):
        with open('data.json', 'w') as f:
            json.dump(titles, f)


if __name__ == '__main__':
    Reporter().run_cli()
