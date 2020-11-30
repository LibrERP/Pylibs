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
    """
    Class that represents a single RiBa receipt to bhe added to a RiBa document.
    
    :param duedate_move_line: Odoo object representing the amount to be payed and it's maturity date
    :type duedate_move_line: class:`account.move.line`
    :param invoice: Odoo object representing the invoice of which this receipt is part
    :type invoice: class:`account.invoice`
    :param debtor_partner: Odoo object holding the name and address of the debtor
    :type debtor_partner: class:`res.partner`
    :param debtor_bank: Odoo object holding the name and address of the debtor's bank
    :type debtor_bank: class:`res.bank`
    """

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
    
    :param creditor_company: Odoo object representing the creditor's company
    :type creditor_company: class:`res.company`
    :param creditor_bank_account:
    :type creditor_company: class:`res.partner.bank`
    """

    def __init__(self, creditor_company, creditor_bank_account):
        """Constructor method"""

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Fields initialization
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self._creditor_company = creditor_company
        self._creditor_bank_account = creditor_bank_account
        self._creation_date = datetime.now()

        self._receipts = list()

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
        receipts_amounts = map(lambda line: line.amount, self._receipts)
        total_amount = sum(receipts_amounts)
        return total_amount
    # end total_amount

    def add_receipt(self, rcpt: Receipt):
        """
        Add a receipt to the RiBa document
        :return: nothing
        """
        self._receipts.append(rcpt)
    # end add_line

    def render_cbi(self):
        """
        Render the RiBa document in the CBI format
        :return: the CBI document representing the RiBa document
        :rtype: str
        """
        cbi_template = Template(
            text=importlib.resources.read_text(__package__ + '.templates', CBI_TEMPLATE_FILE)
        )
        cbi_document = cbi_template.render(doc=self, lines=self._receipts)
        return cbi_document
    # end render
# end Document