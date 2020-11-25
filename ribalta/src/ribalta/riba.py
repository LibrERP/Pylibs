from datetime import datetime
import importlib.resources

from mako.template import Template

from .utils.errors import FiscalcodeMissingError
from .utils.odoo_stuff import UserError, _
from .utils.validators import (
    validate_abi,
    validate_cab,
    validate_bank_account_number,
    validate_zip,
    validate_sia
)


# Name of the Mako template file
CBI_TEMPLATE_FILE = 'cbi.mako'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Receipt:

    def __init__(self, duedate_move_line, invoice, debtor_partner, debtor_bank):

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Fields initialization
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self._duedate_move_line = duedate_move_line
        self._invoice = invoice
        self._debtor_partner = debtor_partner
        self._debtor_bank = debtor_bank

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Sanity checks
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Cab and ABI required
        abi = self.debtor_bank.abi
        cab = self.debtor_bank.cab

        validate_abi(abi, self.debtor_name)
        validate_cab(cab, self.debtor_name)

        # At least one of VAT or fiscal code required
        if not self.debtor_vat_or_fiscode:
            raise FiscalcodeMissingError(
                _('No VAT or Fiscal Code specified for ') + self.debtor_name
            )
        # end if

        # Validate ZIP code
        validate_zip(self.debtor_zip)

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
    def debtor_name(self):
        return self._debtor_partner.name
    # end debtor_name

    @property
    def debtor_client_code(self):
        return self._debtor_partner.ref or ''
    # end debtor_client_code

    @property
    def debtor_fiscalcode(self):
        return self._debtor_partner.fiscalcode
    # end debtor_fiscalcode

    @property
    def debtor_vat_number(self):
        # Since CBI are used only in Italy remove the leading IT from VAT code
        if not self._debtor_partner.vat:
            return False
        elif self._debtor_partner.vat.lower().startswith('it'):
            return self._debtor_partner.vat[2:]
        else:
            return self._debtor_partner.vat
        # end if
    # end debtor_vat_number

    @property
    def debtor_vat_or_fiscode(self):
        return self.debtor_vat_number or self.debtor_fiscalcode
    # end debtor_vat_or_fiscode

    @property
    def debtor_address(self):
        return self._debtor_partner.street
    # end debtor_address

    @property
    def debtor_city(self):
        return self._debtor_partner.city
    # end debtor_city

    @property
    def debtor_state(self):
        if self._debtor_partner.state_id:
            return str(self._debtor_partner.state_id.code)
        else:
            return ''
        # end if
    # end debtor_state

    @property
    def debtor_zip(self):
        return self._debtor_partner.zip
    # end debtor_zip

    @property
    def debtor_bank(self):
        return self._debtor_bank
    # end debtor_bank

    @property
    def invoice_number(self):
        return self._invoice.number
    # end invoice_number

    @property
    def invoice_date(self):
        return self._invoice.date_invoice
    # end invoice_date
# end Receipt


class Document:
    """
    Class that represents a RiBa document with header record, trailing record
    and records for RiBa receipts.
    
    Attributes:
        creditor_company (res.company): Creditor's company object.
        creditor_company_name (str): Creditor's company name as string.
        creditor_fiscalcode (str): Creditor's company fiscal if set.
        creditor_vat_number (str): Creditor's company VAT number if set.
        creditor_vat_or_fiscode (str): Creditor's VAT number or the
                                       fiscalcode it the former is missing.
        creditor_company_ref (str): Creditor's company internal reference if set or ''
        creditor_company_addr_street (str)
        creditor_company_addr_zip (str)
        creditor_company_addr_city (str)
        creditor_company_addr_zip_and_city (str)
        creditor_bank_account (res.bank.account): Creditor's bank account
                                                  object.
        creation_date (datetime.datetime): Document creation timestamp.
        sia_code (str): Creditor's SIA code.
        name (str): Document name (aka nome supporto) obtained concatenating
                    the creation timestamp with the SIA code
        total_amount (float): Sum of the amount of the receipts added to
                              this document
    """

    def __init__(self, creditor_company, creditor_bank_account):
        """
        Constructior for Document.
        
        Parameters:
            creditor_company (res.company): Odoo object representing the credotor's company
            creditor_bank_account (res.bank.
        """

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Fields initialization
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self._creditor_company = creditor_company
        self._creditor_bank_account = creditor_bank_account
        self._creation_date = datetime.now()

        self._lines = list()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Sanity checks
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # CAB and ABI required
        abi = self.creditor_bank_account.abi
        cab = self.creditor_bank_account.cab

        validate_abi(abi, self.creditor_company_name)
        validate_cab(cab, self.creditor_company_name)

        validate_bank_account_number(self.creditor_bank_account.acc_number)

        validate_sia(self.sia_code)

        if not self.creditor_vat_or_fiscode:
            raise FiscalcodeMissingError(
                _('No VAT or Fiscal Code specified for ') + self.creditor_company_name
            )
        # end if

        # Validate ZIP code
        validate_zip(self.creditor_company_addr_zip)
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

    def add_receipt(self, line: Receipt):
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
