from app.models import Account


class AccountsHelpers:
    types = ["asset", "equity", "liability", "revenue", "expense", "dividend"]
    @staticmethod
    def GetAccountNormalBalance(account: Account):
        if (account.type == "dividend"):
            return "debit"
        elif (account.type == "expense"):
            return "debit"
        if (account.type == "asset"):
            return "debit"
        elif (account.type == "liability"):
            return "credit"
        elif (account.type == "equity"):
            return "credit"
        elif (account.type == "revenue"):
            return "credit"
        
        