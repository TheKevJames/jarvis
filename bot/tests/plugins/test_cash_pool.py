import mock
import pytest

import jarvis.db.users

import plugins.cash_pool.plugin as cash_pool
import plugins.cash_pool.helper as helper


class TestCashPool:
    @classmethod
    def setup_class(cls):
        def read_by_name(name):
            if name in ('i', 'me', 'himself', 'herself'):
                raise TypeError
            return name

        jarvis.db.users.UsersDal.is_admin = True
        jarvis.db.users.UsersDal.read_by_name = mock.MagicMock(
            side_effect=read_by_name)

        cls.db = helper.CashPoolDal = cash_pool.CashPoolDal = mock.MagicMock()
        cls.db_history = \
            helper.CashPoolHistoryDal = \
            cash_pool.CashPoolHistoryDal = \
            mock.MagicMock()
        cls.pool = cash_pool.CashPool(mock.MagicMock())

    # NOTE: create mock wrapped functions
    #
    #     cls.mocks = dict()
    #     for idx, fx in enumerate(cls.pool.response_fns):
    #         mocked = mock.Mock(spec=fx)
    #         if hasattr(fx, 'regex'):
    #             mocked.configure_mock(regex=fx.regex)
    #         if hasattr(fx, 'words'):
    #             mocked.configure_mock(words=fx.words)

    #         cls.mocks[fx.__name__] = (mocked, idx, fx)
    #         cls.pool.response_fns[idx] = mocked

    # @classmethod
    # def teardown_class(cls):
    #     for _mocked, idx, fx in cls.mocks.values():
    #         cls.pool.response_fns[idx] = fx

    def setup(self):
        self.db.reset_mock()
        self.db_history.reset_mock()

        # for fx in self.pool.response_fns:
        #     fx.reset_mock()


    @pytest.mark.parametrize('message,expected,history', [
        # currencies
        ('kevin paid $10 for dan', [
            mock.call('kevin', ['dan'], 1000, 'cad'),
        ], []),
        ('kevin paid $10 cad for dan', [
            mock.call('kevin', ['dan'], 1000, 'cad'),
        ], []),
        ('kevin paid $10 usd for dan', [
            mock.call('kevin', ['dan'], 1000, 'usd'),
        ], []),
        ('kevin paid $10 aus for dan', [], []),

        # reasons
        ('for testing purposes kevin paid $1 for dan', [
            mock.call('kevin', ['dan'], 100, 'cad'),
        ], [
            mock.call(mock.ANY, mock.ANY, mock.ANY, mock.ANY,
                      'for testing purposes', 'my_name'),
        ]),
        ('for testing purposes and other reasons kevin paid $1 for dan', [
            mock.call('kevin', ['dan'], 100, 'cad'),
        ], [
            mock.call(mock.ANY, mock.ANY, mock.ANY, mock.ANY,
                      'for testing purposes and other reasons', 'my_name'),
        ]),

        # parse even split
        ('kevin paid $10 for dan and lara', [
            mock.call('kevin', ['dan', 'lara'], 1000, 'cad'),
        ], []),
        ('kevin paid $10 for dan, lara and steven', [
            mock.call('kevin', ['dan', 'lara', 'steven'], 1000, 'cad'),
        ], []),
        ('kevin paid $10 for dan, lara, and steven', [
            mock.call('kevin', ['dan', 'lara', 'steven'], 1000, 'cad'),
        ], []),
        ('kevin paid $10 for dan and lara and steven', [
            mock.call('kevin', ['dan', 'lara', 'steven'], 1000, 'cad'),
        ], []),

        # parse multi-payer
        ('kevin paid $10 and dan paid $15 for kevin', [
            mock.call('kevin', ['kevin'], 1000, 'cad'),
            mock.call('dan', ['kevin'], 1500, 'cad'),
        ], []),
        ('kevin paid $10 and dan paid $15 for kevin and dan', [
            mock.call('kevin', ['kevin', 'dan'], 1000, 'cad'),
            mock.call('dan', ['kevin', 'dan'], 1500, 'cad'),
        ], []),
        ('kevin paid $10 and dan paid $15 for kevin, dan, and lara', [
            mock.call('kevin', ['kevin', 'dan', 'lara'], 1000, 'cad'),
            mock.call('dan', ['kevin', 'dan', 'lara'], 1500, 'cad'),
        ], []),
        ('kevin paid $10, dan paid $15, and lara paid $20 '
         'for kevin, lara, and dan', [
             mock.call('kevin', ['kevin', 'lara', 'dan'], 1000, 'cad'),
             mock.call('dan', ['kevin', 'lara', 'dan'], 1500, 'cad'),
             mock.call('lara', ['kevin', 'lara', 'dan'], 2000, 'cad'),
         ], []),

        # parse uneven-split
        ('kevin paid $10 for lara and kevin paid $15 for dan', [
            mock.call('kevin', ['lara'], 1000, 'cad'),
            mock.call('kevin', ['dan'], 1500, 'cad'),
        ], []),
        ('kevin paid $10 for lara and kevin paid $15 for dan and lara', [
            mock.call('kevin', ['lara'], 1000, 'cad'),
            mock.call('kevin', ['dan', 'lara'], 1500, 'cad'),
        ], []),
        ('kevin paid $15 for dan and lara and kevin paid $10 for lara', [
            mock.call('kevin', ['dan', 'lara'], 1500, 'cad'),
            mock.call('kevin', ['lara'], 1000, 'cad'),
        ], []),
        ('kevin paid $10 for lara, kevin paid $15 for dan, and '
         'kevin paid $100 for kevin, steven, and tyler', [
             mock.call('kevin', ['lara'], 1000, 'cad'),
             mock.call('kevin', ['dan'], 1500, 'cad'),
             mock.call('kevin', ['kevin', 'steven', 'tyler'], 10000, 'cad'),
         ], []),

        # documented
        ('tom paid $20 usd and dick paid $80 cad for tom, dick, and harry', [
            mock.call('tom', ['tom', 'dick', 'harry'], 2000, 'usd'),
            mock.call('dick', ['tom', 'dick', 'harry'], 8000, 'cad'),
        ], []),
        ('tom paid $40 for dick and tom paid $120 for tom and harry', [
            mock.call('tom', ['dick'], 4000, 'cad'),
            mock.call('tom', ['tom', 'harry'], 12000, 'cad'),
        ], []),
    ])
    def test_cash_pool_called_payment(self, message, expected, history):
        self.pool.respond(mock.MagicMock(), 'my_name', message)

        self.db.update.assert_has_calls(expected)
        assert self.db.update.call_count == len(expected)

        self.db_history.create.assert_has_calls(history)

    @pytest.mark.parametrize('message,expected,history', [
        # parse
        ('kevin sent $10 to dan', [
            mock.call('kevin', ['dan'], 1000, 'cad'),
        ], []),
        ('kevin sent $10 to dan and lara', [], []),
        ('kevin sent $10 to dan, lara, and steven', [], []),

        # currencies
        ('kevin sent $10 cad to dan', [
            mock.call('kevin', ['dan'], 1000, 'cad'),
        ], []),
        ('kevin sent $10 usd to dan', [
            mock.call('kevin', ['dan'], 1000, 'usd'),
        ], []),
        ('kevin sent $10 aus to dan', [], []),

        # reasons
        ('for testing purposes kevin sent $1 to dan', [
            mock.call('kevin', ['dan'], 100, 'cad'),
        ], [
            mock.call(mock.ANY, mock.ANY, mock.ANY, mock.ANY,
                      'for testing purposes', 'my_name'),
        ]),

        # parse multi-payer
        ('kevin sent $10 and dan sent $15 to lara', [
            mock.call('kevin', ['lara'], 1000, 'cad'),
            mock.call('dan', ['lara'], 1500, 'cad'),
        ], []),
        ('kevin sent $10, dan sent $15, and steven sent $20 to lara', [
            mock.call('kevin', ['lara'], 1000, 'cad'),
            mock.call('dan', ['lara'], 1500, 'cad'),
            mock.call('steven', ['lara'], 2000, 'cad'),
        ], []),
        ('kevin sent $10 and dan sent $15 to lara and steven', [], []),

        # parse multi-currency
        ('kevin sent $10 cad and kevin sent $15 usd to lara', [
            mock.call('kevin', ['lara'], 1000, 'cad'),
            mock.call('kevin', ['lara'], 1500, 'usd'),
        ], []),

        # parse multi-receiver
        ('kevin sent $10 to dan and dan sent $15 to lara', [
            mock.call('kevin', ['dan'], 1000, 'cad'),
            mock.call('dan', ['lara'], 1500, 'cad'),
        ], []),
        ('kevin sent $10 to dan, dan sent $15 to steven, and '
         'steven sent $20 to lara', [
             mock.call('kevin', ['dan'], 1000, 'cad'),
             mock.call('dan', ['steven'], 1500, 'cad'),
             mock.call('steven', ['lara'], 2000, 'cad'),
         ], []),

        ('for tofu i sent $10 cad to dan, dan sent $15 usd to steven, and '
         'steven sent $10 to me', [
             mock.call('my_name', ['dan'], 1000, 'cad'),
             mock.call('dan', ['steven'], 1500, 'usd'),
             mock.call('steven', ['my_name'], 1000, 'cad'),
         ],
         [
             mock.call(mock.ANY, mock.ANY, mock.ANY, mock.ANY, 'for tofu',
                       'my_name'),
         ]),
    ])
    def test_cash_pool_called_sent(self, message, expected, history):
        self.pool.respond(mock.MagicMock(), 'my_name', message)

        self.db.update.assert_has_calls(expected)
        assert self.db.update.call_count == len(expected)

        self.db_history.create.assert_has_calls(history)
