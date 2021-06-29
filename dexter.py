import cmd

from xrpl.clients import JsonRpcClient
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions \
    import AccountSet, AccountSetFlag, TrustSet, Payment, OfferCreateFlag
from xrpl.models.transactions.offer_create import OfferCreate
from xrpl.transaction \
    import safe_sign_and_autofill_transaction, send_reliable_submission
from xrpl.utils import xrp_to_drops
from xrpl.wallet import Wallet, generate_faucet_wallet

client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")


class Dexter(cmd.Cmd):
    intro = "Welcome to Dexter!"
    prompt = '(dexter) '

    def do_issue(self, arg):
        """Issue a new testnet currency

Parameters:
- token (for example, USD)
- amount (for example, 1000)
- receiver seed (generate on XRPL TestNet Faucet)"""

        print("Issuing currency")

        args = arg.split()

        token = args[0]
        amount = args[1]
        receiver_seed = args[2]

        if len(token) > 3:
            token_bytes = token.encode("ASCII").hex().upper()
            token_symbol = '{:<040s}'.format(token_bytes)
        else:
            token_symbol = token.upper()

        receiver = Wallet(receiver_seed, 0)
        issuer = generate_faucet_wallet(client)
        account_set = AccountSet(account=issuer.classic_address,
                                 set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE)
        signed_account_set = safe_sign_and_autofill_transaction(
            account_set, issuer, client)

        send_reliable_submission(signed_account_set, client)

        trust_set = TrustSet.from_dict(
            {
                "account": receiver.classic_address,
                "limit_amount": {
                    "issuer": issuer.classic_address,
                    "currency": token_symbol,
                    "value": amount
                }
            }
        )

        signed_trust_set = safe_sign_and_autofill_transaction(
            trust_set, receiver, client)
        send_reliable_submission(signed_trust_set, client)

        usd_amount = IssuedCurrencyAmount(value=amount,
                                          issuer=issuer.classic_address,
                                          currency=token_symbol)
        payment = Payment(account=issuer.classic_address,
                          destination=receiver.classic_address,
                          amount=usd_amount)
        signed_payment = safe_sign_and_autofill_transaction(
            payment,
            issuer,
            client)
        send_reliable_submission(signed_payment, client)

        print("Issued " + amount + " " + token + "." + issuer.classic_address)

    def do_liquidity(self, arg):
        """Create orders on DEX

Parameters:
- token_with_address, format <token.issuer_address> (for example, USD.r4MHpHsaZnQ9L1F2Qh4YhXD1CaRA7SUz8v)
- amount (for example, 100)
- mid price (for example, 0.87)
- steps (for example, 3)
- interval - in bps of mid price - for example, 20
- receiver seed (use the same as in issuance)"""

        print("Creating liquidity on DEX")

        args = arg.split()

        token, issuer_address = args[0].split(".")

        token_amount = args[1]
        mid_price = float(args[2])  # Price of one XRP in token units
        steps = int(args[3])
        interval = float(args[4])
        receiver_seed = args[5]

        if len(token) > 3:
            token_bytes = token.encode("ASCII").hex().upper()
            token_symbol = '{:<040s}'.format(token_bytes)
        else:
            token_symbol = token.upper()

        amount_in_token = IssuedCurrencyAmount(value=token_amount,
                                               issuer=issuer_address,
                                               currency=token_symbol)

        receiver = Wallet(receiver_seed, 0)

        for i in range(1, steps+1):
            ask_price = mid_price * (1 + (interval * i) / 10000)
            ask_xrp_amount = float(token_amount) / ask_price

            place_order(amount_in_token,
                        xrp_to_drops(float(ask_xrp_amount)),
                        receiver,
                        None)

            bid_price = mid_price * (1 - (interval * i) / 10000)
            bid_xrp_amount = float(token_amount) / bid_price

            place_order(xrp_to_drops(float(bid_xrp_amount)),
                        amount_in_token,
                        receiver,
                        OfferCreateFlag.TF_SELL)

        print("Orders are created")


def place_order(amount_to_buy, amount_to_sell, receiver, flags):
    if flags is None:
        offer_create = \
            OfferCreate(account=receiver.classic_address,
                        taker_gets=amount_to_sell,
                        taker_pays=amount_to_buy)
    else:
        offer_create = \
            OfferCreate(account=receiver.classic_address,
                        taker_gets=amount_to_sell,
                        taker_pays=amount_to_buy,
                        flags=flags)

    signed_offer_create = safe_sign_and_autofill_transaction(
        offer_create,
        receiver,
        client)
    send_reliable_submission(signed_offer_create, client)


if __name__ == '__main__':
    Dexter().cmdloop()
