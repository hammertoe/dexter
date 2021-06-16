import cmd

class Dexter(cmd.Cmd):
    intro = "Welcome to Dexter!"
    prompt = '(dexter) '

    def do_fetch(self, arg):
        "Fetch orderbooks for the specific currency pair"
        print("actually fetch order books...")

    def do_issue(self, arg):
        "Issue a new testnet currency"
        print("actually issue currency...")
        
if __name__ == '__main__':
    Dexter().cmdloop()
