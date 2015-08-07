
import requests
from lxml import html as lxml_html


def clear_text(text):
    return text.replace('R$', '').replace('.', '').replace(',', '.').strip()


base = 'http://www.tesouro.fazenda.gov.br/'
taxas = base + 'tesouro-direto-precos-e-taxas-dos-titulos'
index = {}

html = requests.get(taxas).content

rows = lxml_html.fromstring(html).xpath('//tr[@class="camposTesouroDireto"]')
for row in rows:
    # Get data from row:
    columns = [
        'title', 'due_date',
        'tax_aa_buy', 'tax_aa_sell',
        'daily_value_buy', 'daily_value_sell'
    ]
    values = map(lambda x: clear_text(x.text), row.xpath('td'))
    data = dict(zip(columns, values))

    title = data['title']
    del data['title']

    index[title] = data


from pprint import pprint
pprint(index)
