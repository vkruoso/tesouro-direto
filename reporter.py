
import yaml
import json
import smtplib
import argparse

from jinja2 import Template
from email.mime.text import MIMEText
from datetime import date

from client import TDClient


class Email(object):

    def __init__(self, config):
        self.config = config

        with open('email.html', 'r') as f:
            self.template = f.read()

    def send_diff(self, old, new):
        template = Template(self.template)
        text = template.render(new=new, old=old)

        # Create message container
        msg = MIMEText(text, 'html')
        msg['Subject'] = "Atualizacoes Tesouro Direto"
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

    def _get_current_data(self):
        """Returns the current saved data."""
        return None

    def _get_new_data(self, config):
        # Build client and login
        client = TDClient()
        client.login(cpf=config['cpf'], password=config['password'])

        # Get titles and their details
        titles = client.get_titles(date.today().month, date.today().year)
        for name, data in titles.iteritems():
            data['details'] = client.get_title_details(name, data)

        # Logout and return
        client.logout()
        return titles

    def _save_latest(self, titles):
        with open('data.json', 'w') as f:
            json.dump(titles, f)


if __name__ == '__main__':
    Reporter().run_cli()
