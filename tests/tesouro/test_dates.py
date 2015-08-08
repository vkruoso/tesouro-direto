import datetime
import pytest

from tesouro import dates


@pytest.fixture
def cupom_date(request):
    return request.param


class TestDates(object):

    @pytest.mark.parametrize("cupom_date,bank_days", [
        (datetime.date(2012, 7, 1), 121),
        (datetime.date(2013, 1, 1), 247),
        (datetime.date(2013, 7, 1), 370),
        (datetime.date(2014, 1, 1), 500),
        (datetime.date(2014, 7, 1), 622),
        (datetime.date(2015, 1, 1), 753),
        (datetime.date(2015, 7, 1), 875),
        (datetime.date(2016, 1, 1), 1003),
        (datetime.date(2016, 7, 1), 1127),
        (datetime.date(2017, 1, 1), 1254),
    ])
    def test_dates(self, cupom_date, bank_days):
        """Tests bank days implementation based on TD source.

        This test is based on the date table of the following document:
        http://www.tesouro.fazenda.gov.br/documents/10180/410323/NTN-F_novidades.pdf

        This can also be simulated by Excel. The document above tells you how.
        """
        buy_date = datetime.date(2012, 1, 6)
        assert dates.brazilian_bank_days(buy_date, cupom_date) == bank_days
