import dateutil.parser
from types import SimpleNamespace


class BankAccountFake:
    def __init__(self, bank_name, iban):
        self.bank_name = bank_name
        self.acc_number = iban
        self.sanitized_acc_number = self.acc_number.replace(' ', '').upper()
    # end init
# end BankAccountFake


class InvoiceFake:
    def __init__(self, number, date_invoice):
        self.number = number
        self.date_invoice = dateutil.parser.parse(date_invoice)
    # end init
# end InvoiceFake


class MoveLineFake:
    def __init__(self, date_maturity, amount_residual, invoice_id):
        self.date_maturity = dateutil.parser.parse(date_maturity)
        self.amount_residual = amount_residual
        self.invoice_id = invoice_id
    # end init
# end InvoiceFake


class PartnerFake:
    def __init__(
            self,
            id, name, ref='',
            vat='', fiscalcode='',
            street='', city='', zip='', state_id=None
    ):
        self.id = id
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
    def __init__(self, partner, sia_code):
        self.partner_id = PartnerFake(**partner)
        self.sia_code = sia_code
    # end init
# end CompanyFake


class PaymentLineFake:
    def __init__(self, move_line_id, partner_id, partner_bank_id, communication):
        self.move_line_id = move_line_id
        self.partner_id = partner_id  # debtor_partner
        self.partner_bank_id = partner_bank_id  # debtor_bank_account
        self.communication = communication
    # end init
# end CompanyFake
