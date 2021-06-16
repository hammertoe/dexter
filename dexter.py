import cmd

from xrpl.clients import JsonRpcClient
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions \
    import AccountSet, AccountSetFlag, TrustSet, Payment
from xrpl.transaction \
    import safe_sign_and_autofill_transaction, send_reliable_submission
from xrpl.wallet import Wallet
from xrpl.wallet import generate_faucet_wallet

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


if __name__ == '__main__':
    Dexter().cmdloop()
