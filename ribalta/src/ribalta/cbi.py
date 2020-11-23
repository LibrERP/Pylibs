from datetime import datetime
import importlib

from mako.template import Template
from odoo import _
from odoo.exceptions import UserError


CBI_TEMPLATE_FILE = 'cbi.mako'


class Line:

    def __init__(self, duedate_move_line, invoice, debitor_partner, debitor_bank):

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Fields initialization
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self._duedate_move_line = duedate_move_line
        self._invoice = invoice
        self._debitor_partner = debitor_partner
        self._debitor_bank = debitor_bank

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Sanity checks
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Cab and ABI required
        abi = self.debitor_bank.abi
        cab = self.debitor_bank.cab

        if not abi or not cab:
            raise UserError(
                _('No IBAN or ABI/CAB specified for ') + self.debitor_name
            )
        # end if

        # At least one of VAT or fiscal code required
        if not self.debitor_vat_or_fiscode:
            raise UserError(
                _('No VAT or Fiscal Code specified for ') + self.debitor_name
            )
        # end if

    # end __init__

    @property
    def duedate(self):
        return self._duedate_move_line.date_maturity
    # end duedate

    @property
    def amount(self):
        return self._duedate_move_line.amount_residual
    # end amount

    @property
    def debitor_name(self):
        return self._debitor_partner.name
    # end debitor_name

    @property
    def debitor_client_code(self):
        return self._debitor_partner.ref or ''
    # end debitor_client_code

    @property
    def debitor_fiscalcode(self):
        return self._debitor_partner.fiscalcode
    # end debitor_fiscalcode

    @property
    def debitor_vat_number(self):
        # Since CBI are used only in Italy remove the leading IT from VAT code
        if not self._debitor_partner.vat:
            return False
        elif self._debitor_partner.vat.lower().startswith('it'):
            return self._debitor_partner.vat[2:]
        else:
            return self._debitor_partner.vat
        # end if
    # end debitor_vat_number

    @property
    def debitor_vat_or_fiscode(self):
        return self.debitor_vat_number or self.debitor_fiscalcode
    # end debitor_vat_or_fiscode

    @property
    def debitor_address(self):
        return self._debitor_partner.street
    # end debitor_address

    @property
    def debitor_city(self):
        return self._debitor_partner.city
    # end debitor_city

    @property
    def debitor_state(self):
        if self._debitor_partner.state_id:
            return str(self._debitor_partner.state_id.code)
        else:
            return ''
        # end if
    # end debitor_state

    @property
    def debitor_zip(self):
        return self._debitor_partner.zip
    # end debitor_zip

    @property
    def debitor_bank(self):
        return self._debitor_bank
    # end debitor_bank_descr

    @property
    def invoice_number(self):
        return self._invoice.number
    # end invoice_number

    @property
    def invoice_date(self):
        return self._invoice.date_invoice
    # end invoice_date

# end Line


class Document:

    def __init__(self, creditor_company, creditor_bank_account, currency_code='E'):

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Fields initialization
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self._creditor_company = creditor_company
        self._creditor_bank_account = creditor_bank_account
        self._creation_date = datetime.now()
        self._currency_code = currency_code

        self._lines = list()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Sanity checks
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Cab and ABI required
        abi = self.creditor_bank_account.abi
        cab = self.creditor_bank_account.cab

        if not abi or not cab:
            raise UserError(
                _('No ABI/CAB specified for ')
                +
                self.creditor_company_name
            )
        # end if

        if not self.creditor_bank_account.acc_number:
            raise UserError(
                _('No IBAN specified for ') + self.creditor_company_name
            )
        # end if

        if not self.sia_code:
            raise UserError(
                _('No SIA Code specified for ') + self.creditor_company_name
            )
        # end if

        if not self.creditor_vat_or_fiscode:
            raise UserError(
                _('No VAT or Fiscal Code specified for ') + self.creditor_company_name
            )
        # end if

    # end __init__

    @property
    def creditor_company(self):
        return self._creditor_company
    # end creditor_company

    @property
    def creditor_company_name(self):
        return self._creditor_company.partner_id.name
    # end creditor_company

    @property
    def creditor_fiscalcode(self):
        return self._creditor_company.partner_id.fiscalcode
    # end creditor_fiscalcode

    @property
    def creditor_vat_number(self):
        # Since CBI are used only in Italy remove the leading IT from VAT code
        if not self._creditor_company.partner_id.vat:
            return False
        elif self._creditor_company.partner_id.vat.lower().startswith('it'):
            return self._creditor_company.partner_id.vat[2:]
        else:
            return self._creditor_company.partner_id.vat
        # end if
    # end creditor_vat_number

    @property
    def creditor_vat_or_fiscode(self):
        return self.creditor_vat_number or self.creditor_fiscalcode
    # end creditor_vat_or_fiscode

    @property
    def creditor_company_ref(self):
        return self._creditor_company.partner_id.ref or ''
    # end creditor_company

    @property
    def creditor_company_addr_street(self):
        return self._creditor_company.partner_id.street or ''
    # end creditor_company

    @property
    def creditor_company_addr_zip(self):
        zip_code = self._creditor_company.partner_id.zip or ''
        return zip_code
    # end creditor_company

    @property
    def creditor_company_addr_city(self):
        city = self._creditor_company.partner_id.city or ''
        return city
    # end creditor_company

    @property
    def creditor_company_addr_zip_and_city(self):
        zip_code = self._creditor_company.partner_id.zip or ''
        city = self._creditor_company.partner_id.city or ''
        return f'{zip_code} {city}'
    # end creditor_company

    @property
    def creditor_bank_account(self):
        return self._creditor_bank_account
    # end creditor_bank_account

    @property
    def creation_date(self):
        return self._creation_date
    # end creation_date

    @property
    def currency_code(self):
        return self._currency_code
    # end currency_code

    @property
    def sia_code(self):
        return str(self._creditor_company.sia_code).strip()
    # end sia_code

    @property
    def name(self):
        return self._creation_date.strftime('%d%m%y%H%M%S') + str(self.sia_code)
    # end support_name

    @property
    def total_amount(self):
        # Since this function will probably be called just one time the
        # computation can be done on the fly without any negative
        # performance impact
        lines_amounts = map(lambda line: line.amount, self._lines)
        total_amount = sum(lines_amounts)
        return total_amount
    # end total_amount

    def add_line(self, line: Line):
        self._lines.append(line)
    # end add_line

    def render_cbi(self):
        cbi_template = Template(
            text=importlib.resources.read_text(__package__ + '.templates', CBI_TEMPLATE_FILE)
        )
        cbi_document = cbi_template.render(doc=self, lines=self._lines)
        return cbi_document
    # end render

# end Document
