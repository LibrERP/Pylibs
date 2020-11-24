import dateutil.parser
from types import SimpleNamespace


class BankFake:
    def __init__(self, abi, cab, bank_name=''):
        self.bank_name = bank_name
        self.abi = abi
        self.cab = cab
    # end init


# end BankFake

class BankAccountFake:
    def __init__(self, abi, cab, number):
        self.acc_number = number
        self.abi = abi
        self.cab = cab
    # end init


# end BankAccountFake

class InvoiceFake:
    def __init__(self, number, date_invoice):
        self.number = number
        self.date_invoice = dateutil.parser.parse(date_invoice)
    # end init


# end InvoiceFake

class MoveLineFake:
    def __init__(self, date_maturity, amount_residual):
        self.date_maturity = dateutil.parser.parse(date_maturity)
        self.amount_residual = amount_residual
    # end init


# end InvoiceFake

class PartnerFake:
    def __init__(
            self,
            name, ref='',
            vat='', fiscalcode='',
            street='', city='', zip='', state_id=None
    ):
        self.name = name
        self.ref = ref
        self.vat = vat
        self.fiscalcode = fiscalcode
        self.street = street
        self.city = city
        self.zip = zip
        if state_id:
            self.state_id = SimpleNamespace(**state_id)
        else:
            self.state_id = None
        # end if
    # end init


# end PartnerFake

class CompanyFake:
    def __init__(self, partner_id, sia_code):
        self.partner_id = PartnerFake(**partner_id)
        self.sia_code = sia_code
    # end init


# end CompanyFake