
import requests
from lxml import html as lxml_html


class TDClient(object):

    URL = 'https://tesourodireto.bmfbovespa.com.br/PortalInvestidor/'
    USER_AGENT = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'
    )

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': self.USER_AGENT,
            'Referer': self.URL
        }

    def login(self, cpf, password):
        html = self.session.get(self.URL, verify=False, timeout=10).content
        info = lxml_html.fromstring(html)

        # Build post data
        post_data = self._build_base_post_data(info)
        post_data['ctl00$BodyContent$txtLogin'] = cpf
        post_data['ctl00$BodyContent$txtSenha'] = password
        post_data['ctl00$BodyContent$btnLogar'] = 'Entrar'

        # Submit login information
        return self.session.post(self.URL, post_data)

    def get_titles(self):
        extrato = self.URL + 'extrato.aspx'
        resp = self.session.get(extrato)
        print resp.content

    def _build_base_post_data(self, current):
        """Generic post data builder with common fields in the forms."""
        post_data = {}
        fields = [
            '__VIEWSTATE',
            '__VIEWSTATEGENERATOR',
            '__EVENTVALIDATION',
            '__EVENTTARGET',
            '__EVENTARGUMENT',
            ('BodyContent_hdnCamposRequeridos',
             'ctl00$BodyContent$hdnCamposRequeridos')
        ]
        for field in fields:
            # Get input id and name
            try:
                (id_, name_) = field
            except ValueError:
                id_ = name_ = field

            # Get value and set in the post data
            input_ = current.xpath('//input[@id="%s"]' % id_)
            if input_:
                value = input_[0].value
                post_data[name_] = value
        return post_data


client = TDClient()
client.login(cpf='00000000000', password='secret')
client.get_titles()
