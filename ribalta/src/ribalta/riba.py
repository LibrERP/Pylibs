from datetime import datetime, date
import importlib.resources
import itertools
import logging
from mako import exceptions
from mako.template import Template
import re
import typing

from .utils.errors import FiscalcodeMissingError, FiscalcodeAndVATMissingError
from .utils.odoo_stuff import _
from .utils.validators import (
    validate_abi,
    validate_cab,
    validate_bank_account_number,
    validate_zip,
    validate_sia
)


# Name of the Mako template file
CBI_TEMPLATE_FILE = 'cbi.mako'

# Logging object initialization
_logger = logging.getLogger(__name__)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Receipt:
    """
    Class that represents a single RiBa receipt to be added to a RiBa document.

    :param payment_line: Odoo object representing the payment line or the payment order
    :type payment_line: class:`account.payment.line`
    """

    def __init__(self, payment_line):

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Fields initialization
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self._duedate_move_line = payment_line.move_line_id
        self._invoice = payment_line.move_line_id.invoice_id
        self._debtor_partner = payment_line.partner_id
        self._debtor_bank_account = payment_line.partner_bank_id

        if payment_line.move_line_id.invoice_id:
            self._communication = payment_line.communication
        else:
            self._communication = payment_line.move_line_id.name
        # end if

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Sanity checks
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # CAB and ABI required
        debtor_iban = self._debtor_bank_account.sanitized_acc_number.replace(
            ' ', ''
        ).upper()
        
        self._debtor_bank_abi = debtor_iban[5:10]
        self._debtor_bank_cab = debtor_iban[10:15]

        validate_abi(self.debtor_bank_abi, self.debtor_name)
        validate_cab(self.debtor_bank_cab, self.debtor_name)

        # Fiscal code required
        if not self.debtor_fiscode_or_vat:
            raise FiscalcodeMissingError(
                _(
                    'No Fiscal Code nor VAT number specified for '
                    f'{self.debtor_name} '
                    'At least one between Fiscal Code and VAT'
                    'must be set.'
                )
            )
        # end if

        # Validate ZIP code
        validate_zip(self.debtor_zip)

    # end __init__
    
    @property
    def is_group(self):
        return False
    # end is_group

    @property
    def duedate(self):
        return self._duedate_move_line.date_maturity
    # end duedate

    @property
    def amount(self):
        return self._duedate_move_line.amount_residual
    # end amount

    @property
    def debtor_partner(self):
        return self._debtor_partner
    # end duedate

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
        if not self._debtor_partner.vat:
            return False
        else:
            return self._debtor_partner.vat
        # end if
    # end debtor_vat_number

    @property
    def debtor_fiscode_or_vat(self):
        if not self.debtor_fiscalcode and not self.debtor_vat_number:
            raise FiscalcodeAndVATMissingError(
                f'Fiscalcode and VAT missing for debtor {self.debtor_name}'
            )
        # end if
        return self.debtor_fiscalcode or re.sub('^IT', '', self.debtor_vat_number)
    # end debtor_fiscode_or_vat

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
    def debtor_bank_abi(self):
        return self._debtor_bank_abi
    # end debtor_bank

    @property
    def debtor_bank_cab(self):
        return self._debtor_bank_cab
    # end debtor_bank

    @property
    def debtor_bank_name(self):
        return self._debtor_bank_account.bank_name
    # end debtor_bank

    @property
    def invoice_number(self):
        if self._invoice:
            return self._invoice.number
        else:
            return self._duedate_move_line.move_id.name
    # end invoice_number

    @property
    def invoice_date(self):
        if self._invoice:
            return self._invoice.date_invoice
        else:
            return self._duedate_move_line.move_id.invoice_date
    # end invoice_date

    @property
    def communication(self):
        return self._communication
    # end communication
    
    @property
    def grouping_key(self) -> typing.Tuple[str, str, str, date]:
        """
        Generate and return the grouping key used to group the class:`Receipt` objects when requested
        
        :returns: The grouping key
        :rtype: Tuple
        """
        
        return (
            str(self.debtor_partner.id),
            str(self.debtor_bank_abi),
            str(self.debtor_bank_cab),
            self.duedate
        )
    # end grouping_key

    @property
    def description(self):
        if self.invoice_date:
            desc = f'{self.invoice_number} ({self.invoice_date:%Y-%m-%d}) € {self.amount:.2f}'
        else:
            desc = f'{self.invoice_number} € {self.amount:.2f}'
        # end if

        return desc
    # end description
    
    def __str__(self):
        name = self.debtor_name[:25].ljust(25, ' ')
        vat = self.debtor_fiscode_or_vat
        inv_num = self.invoice_number
        inv_date = self.invoice_date
        due_date = self.duedate
        amount = self.amount

        inv_date_str = inv_date and f'del {inv_date:%Y-%m-%d} ' or ''

        return (
            f'{name} ({vat}) - '
            f'{inv_num} {inv_date_str}- '
            f'scad: {due_date:%Y-%m-%d} € {amount}'
        )
    # end __str__
    
    def __repr__(self):
        return self.__str__()
    # end __repr__
# end Receipt


class ReceiptGroup:
    """
    Class that represents a group of RiBa receipt to be rendered as a single line in the RiBa document.
    
    :param receipts: the list of class:`Receipt` objects to bo grouped together
    :type receipts: List of class:`Receipt`
    """

    def __init__(self, receipts: typing.List[Receipt]):
        
        if not receipts:
            raise ValueError(
                'There must be at least one Receipt object in the group'
            )
        # end if

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Fields initialization
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # List of receipts
        self._receipts = receipts
        
        # Reference object to get data common to all receipts in the group
        self._r_ref = self._receipts[0]
        
        # Description of the group listing the numbers of the invoices
        # referred by the grouped lines
        self._desc = ', '.join(
            map(lambda r: r.description, self._receipts)
        )
        
        # Total amount of the group
        self._amount = sum(
            map(lambda r: r.amount, self._receipts)
        )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Sanity checks
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        # Same debtor partner
        
        # Same debtor bank
    # end __init__
    
    @property
    def is_group(self):
        return len(self._receipts) > 1
    # end is_group
    
    @property
    def grouped_receipts(self):
        return self._receipts
    # end is_group

    @property
    def duedate(self):
        return self._r_ref.duedate
    # end duedate

    @property
    def amount(self):
        return self._amount
    # end amount

    @property
    def debtor_name(self):
        return self._r_ref.debtor_name
    # end debtor_name

    @property
    def debtor_client_code(self):
        return self._r_ref.debtor_client_code
    # end debtor_client_code

    @property
    def debtor_fiscalcode(self):
        return self._r_ref.debtor_fiscalcode
    # end debtor_fiscalcode

    @property
    def debtor_vat_number(self):
        return self._r_ref.debtor_vat_number
    # end debtor_vat_number

    @property
    def debtor_fiscode_or_vat(self):
        return self._r_ref.debtor_fiscode_or_vat
    # end debtor_fiscode_or_vat

    @property
    def debtor_address(self):
        return self._r_ref.debtor_address
    # end debtor_address

    @property
    def debtor_city(self):
        return self._r_ref.debtor_city
    # end debtor_city

    @property
    def debtor_state(self):
        return self._r_ref.debtor_state
    # end debtor_state

    @property
    def debtor_zip(self):
        return self._r_ref.debtor_zip
    # end debtor_zip
    
    @property
    def debtor_bank_abi(self):
        return self._r_ref.debtor_bank_abi
    # end debtor_bank

    @property
    def debtor_bank_cab(self):
        return self._r_ref.debtor_bank_cab
    # end debtor_bank

    @property
    def debtor_bank_name(self):
        return self._r_ref.debtor_bank_name
    # end debtor_bank

    @property
    def invoice_number(self):
        return self._r_ref.invoice_number
    # end invoice_number

    @property
    def invoice_date(self):
        return self._r_ref.invoice_date
    # end invoice_date

    @property
    def communication(self):
        # Merge the descriptions
        msg = ", ".join([r.communication for r in self.grouped_receipts])
        return msg
    # end communication
    
    def __str__(self):
        d_name = self.debtor_name[:25].ljust(25, ' ')
        return f'{d_name} ({self.debtor_fiscode_or_vat}) - ' \
               f'{self.duedate:%Y-%m-%d} - {self._desc} - {self.amount} €'
    # end __str__
    
    def __repr__(self):
        return self.__str__()
    # end __repr__
# end ReceiptGroup


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
        creditor_iban = self._creditor_bank_account.sanitized_acc_number.replace(
            ' ', ''
        ).upper()

        self._creditor_bank_abi = creditor_iban[5:10]
        self._creditor_bank_cab = creditor_iban[10:15]
        self._creditor_bank_acc = creditor_iban[-12:]

        validate_abi(self.creditor_bank_abi, self.creditor_company_name)
        validate_cab(self.creditor_bank_abi, self.creditor_company_name)

        validate_bank_account_number(self._creditor_bank_acc)

        validate_sia(self.sia_code)

        if not self.creditor_fiscode_or_vat:
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
        if not self._creditor_company.partner_id.vat:
            return False
        else:
            return self._creditor_company.partner_id.vat
        # end if
    # end creditor_vat_number

    @property
    def creditor_fiscode_or_vat(self):
        if self.creditor_fiscalcode:
            result = self.creditor_fiscalcode
        elif self.creditor_vat_number:
            result = self.creditor_vat_number
        else:
            result = ''
        # end if

        # Remove IT from the beginning of the VAT number ....some banks do not like it
        result = re.sub(pattern=r'^[iI][tT]', repl='', string=result)
        return result
    # end creditor_fiscode_or_vat

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
    def creditor_company_addr_state(self):
        state = self._creditor_company.partner_id.state_id or False
        return state and state.code or ''
    # end creditor_company

    @property
    def creditor_company_addr_zip_city_state(self):
        zip_code = self._creditor_company.partner_id.zip or ''
        city = self._creditor_company.partner_id.city or ''
        state = self._creditor_company.partner_id.state_id or False
        
        if state:
            return f'{zip_code} {city} {state.code}'
        else:
            return f'{zip_code} {city}'
        # end if
    # end creditor_company

    @property
    def creditor_bank_acc(self):
        return self._creditor_bank_acc
    # end creditor_bank_account

    @property
    def creditor_bank_abi(self):
        return self._creditor_bank_abi
    # end creditor_bank_account

    @property
    def creditor_bank_cab(self):
        return self._creditor_bank_cab
    # end creditor_bank_account

    @property
    def creditor_bank_name(self):
        return self._creditor_bank_account.bank_name
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
        """Return the "Nome supporto" as specified in the reference
         document CBI-ICI-001 Versione: v. 6.01"""
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

    def render_cbi(self, group: bool = False):
        """
        Render the RiBa document in the CBI format
        :return: the CBI document representing the RiBa document
        :rtype: str
        """
        
        # Load the Mako template
        cbi_template = Template(
            text=importlib.resources.read_text(__package__ + '.templates', CBI_TEMPLATE_FILE)
        )

        # Group the receipts if requested
        if group:
            receipt_groups = self._group_receipts()
            lines_for_template = receipt_groups
        else:
            lines_for_template = self._receipts
        # end if

        try:
            cbi_document = cbi_template.render(doc=self, lines=lines_for_template)
            return cbi_document

        except Exception as e:
            render_error_msg = exceptions.text_error_template().render()

            _logger.error(render_error_msg)
            print(render_error_msg)

            raise e

        # end try / except
    # end render
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Private methods
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _group_receipts(self):
        
        # Sort the receipts
        def key_f(x): return x.grouping_key
        
        # Sort the receipts
        rcpt_sorted = sorted(self._receipts, key=key_f)
        
        # Group the receipts (same debtor and same duedate)
        rcpt_groups = [
            # 'g' must be converted to a list because it's just an iterator
            ReceiptGroup(list(g))
            for _, g in itertools.groupby(rcpt_sorted, key=key_f)
        ]
        
        return rcpt_groups
    # end _group_receipts
# end Document
