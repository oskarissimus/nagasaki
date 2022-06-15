from decimal import Decimal

from nagasaki.models.bitclude import AccountSummary


class DeribitUtils:
    @staticmethod
    def get_total_delta(account_summary: AccountSummary) -> Decimal:
        """
        D = get delta position from api delta_total
        MB = get margin balance from api margin_balance
        MB - sald BTC na deribicie
        grand_total_delta = MB + D
        """
        return account_summary.margin_balance + account_summary.delta_total

    @staticmethod
    def get_equity_usd(
        account_summary: AccountSummary, index_price_btc_usd: Decimal
    ) -> Decimal:
        """
        get private-get_account_summary equity number The account's current equity
        """
        equity_btc = account_summary.equity
        equity_usd = equity_btc * index_price_btc_usd
        return equity_usd
