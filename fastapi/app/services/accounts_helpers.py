from app.models import Account


class AccountsHelpers:
    
    @staticmethod
    def GetAccountNormalBalance(account: Account):
        if (account.type == "dividends"):
            return "debit"
        elif (account.type == "expenses"):
            return "debit"
        if (account.type == "assets"):
            return "debit"
        elif (account.type == "liabilities"):
            return "credit"
        elif (account.type == "equity"):
            return "credit"
        elif (account.type == "revenue"):
            return "credit"
        
        