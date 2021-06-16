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

    def do_fetch(self, arg):
        "Fetch orderbooks for the specific currency pair"
        print("actually fetch order books...")

    def do_issue(self, arg):
        "Issue a new testnet currency"
        print("actually issue currency...")

        args = arg.split()

        token = args[0]
        amount = args[1]
        receiver_seed = args[2]

        token_bytes = token.encode("ASCII").hex().upper()
        token_symbol = '{:<040s}'.format(token_bytes)

        receiver = Wallet(receiver_seed, 0)
        issuer = generate_faucet_wallet(client)
        account_set = AccountSet(account=issuer.classic_address,
                                 set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE)
        signed_account_set = safe_sign_and_autofill_transaction(
            account_set, issuer, client)

        response = send_reliable_submission(signed_account_set, client)

        print("account set response")
        print(response)

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
        response = send_reliable_submission(signed_trust_set, client)

        print("trust set response")
        print(response)

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
        response = send_reliable_submission(signed_payment, client)

        print("payment response")
        print(response)

    def do_liquidity(self, arg):
        "Create orders on DEX"
        print("actually create orders...")
        args = arg.split()

        token, issuer_address = args[0].split(".")

        print(token)
        print(issuer_address)

        token_amount = args[1]
        mid_price = float(args[2])  # Price of one XRP in token units
        steps = int(args[3])
        interval = float(args[4])
        receiver_seed = args[5]

        token_bytes = token.encode("ASCII").hex().upper()
        token_symbol = '{:<040s}'.format(token_bytes)

        amount_in_token = IssuedCurrencyAmount(value=token_amount,
                                               issuer=issuer_address,
                                               currency=token_symbol)

        receiver = Wallet(receiver_seed, 0)

        for i in range(1, steps):
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
    response = send_reliable_submission(signed_offer_create, client)

    print("order response")
    print(response)


if __name__ == '__main__':
    Dexter().cmdloop()
