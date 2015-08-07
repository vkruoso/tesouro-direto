# coding: utf-8

import re
import requests
from lxml import html as lxml_html


__all__ = ['TDClient']


def clear_text(text):
    text = text.replace('R$', '').replace('.', '').replace(',', '.')
    text = text.replace('\r', '').replace('\n', '').strip()
    try:
        return float(text)
    except ValueError:
        return text


def calculate(title, data):
    if title.endswith('(LFT)'):
        return data['net_value'] - data['initial_value']
    return None


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

        # The logout URL
        self._logout_url = None

    def login(self, cpf, password):
        html = self.session.get(self.URL, verify=False, timeout=10).content
        info = lxml_html.fromstring(html)

        # Build post data
        post_data = self._build_base_post_data(info)
        post_data['ctl00$BodyContent$txtLogin'] = cpf
        post_data['ctl00$BodyContent$txtSenha'] = password
        post_data['ctl00$BodyContent$btnLogar'] = 'Entrar'

        # Submit login information (TODO: check if login succeeded)
        resp = self.session.post(self.URL, post_data)

        # Maintain the URL for logout
        self._logout_url = lxml_html.fromstring(resp.content).xpath(
            '//div[@id="user-logoff-desktop"]/p/a[last()]/@href')[0]

    def get_titles(self, month, year):
        # Get base statement page and build base post data
        statement = self.session.get(self.URL + 'extrato.aspx')
        statement = lxml_html.fromstring(statement.content)
        post_data = self._build_base_post_data(statement)

        # Add the query we are looking for
        post_data['ctl00$BodyContent$ddlMes'] = month
        post_data['ctl00$BodyContent$ddlAno'] = year
        post_data['ctl00$BodyContent$btnConsultar'] = 'Consultar'

        # Get data and parse the information
        statement = self.session.post(self.URL + 'extrato.aspx', post_data)
        statement = lxml_html.fromstring(statement.content)

        # The columns of the statement page
        columns = [
            'initial_titles', 'credit_titles', 'debit_titles',
            'bloqued_titles', 'current_titles',
            'initial_value', 'gross_value', 'net_value'
        ]
        keyre = re.compile("\('QS=(.*)'\)")

        # Find all brokerages available
        index = {}
        brokerages = statement.xpath('//p[@class="title doc"]')
        for brokerage in brokerages:
            name = brokerage.xpath('a/text()')[0]

            # Add an entry to this brokerage in the index
            calcs = {}
            data = {}
            index[name] = data

            # The data section that have information about all titles of
            # a brokerage is just above the paragraph with its title.
            section = brokerage.getparent()

            # Lets use the fact that the data we are looking for is in a
            # table line with 10 columns, so we can easily find it.
            rows = section.xpath('.//tr')
            for row in rows:
                tds = row.xpath('td')
                if len(tds) == 10:
                    values = map(lambda x: clear_text(x.text), tds[1:9])
                    table = dict(zip(columns, values))

                    # The first column is the title, that is inside a link
                    title = clear_text(tds[0].xpath('a/text()')[0])

                    # The last column has the key to get data for the title
                    value = tds[9].xpath('a/@onclick')[0]
                    table['key'] = keyre.search(value).group(1)

                    # Consolidate the information
                    data[title] = table

                    # Calculate information about the title
                    calcs[title] = calculate(title, table)
            from pprint import pprint
            pprint(calcs)
        return index

    def get_title_details(self, name, title):
        # Get data and parse the information
        resp = self.session.get(
            self.URL + 'extrato-analitico.aspx?QS=%s' % title['key']
        )
        details = lxml_html.fromstring(resp.content)

        # The columns of the details page
        columns = [
            'current_balance', 'initial_transaction', 'gross_value',
            'buy_unit', 'agreed_rate', 'days', 'ir_rate', 'ir_tax', 'iof_tax',
            'bvmf_tax', 'custody_tax', 'net_value',
            'gross_rate_month', 'gross_rate_year',
            'gross_rate_last_12_months', 'gross_rate_total'
        ]

        # Lets use the fact that the data we are looking for is in a table
        # line with 17 columns and class 'nowrap', so we can easily find it.
        index = {}
        rows = details.xpath('//tr[@class="nowrap"]')
        for row in rows:
            tds = row.xpath('td')
            if len(tds) == 17:
                values = map(lambda x: clear_text(x.text), tds[1:])
                data = dict(zip(columns, values))
                data['days'] = int(data['days'])

                # The first column is the buy date
                date = clear_text(tds[0].text)

                # Consolidate the information
                index[date] = data
        return index

    def logout(self):
        if self._logout_url:
            return self.session.get(self.URL + self._logout_url)
        return None

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
