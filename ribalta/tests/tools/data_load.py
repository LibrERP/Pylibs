from collections import namedtuple
from pathlib import Path
import importlib.resources
import json

from .fakes import BankAccountFake, InvoiceFake, MoveLineFake, PartnerFake, CompanyFake, PaymentLineFake


TEST_DATA_PACKAGE = 'tests.data'


def load_data_as_text(filename: str):
    return importlib.resources.read_text(
        TEST_DATA_PACKAGE, filename
    )
# end load_data_as_text


def load_data_as_bytes(filename: str):
    return importlib.resources.read_binary(
        TEST_DATA_PACKAGE, filename
    )
# end load_data_as_bytes


class FakeData:
    def __init__(self, creditor_company, creditor_bank_account, receipts):
        self.head = {
            'creditor_company': CompanyFake(**creditor_company),
            'creditor_bank_account': BankAccountFake(**creditor_bank_account),
        }
        self.receipts = [
            PaymentLineFake(
                partner_id=PartnerFake(**rcpt['debtor_partner']),
                partner_bank_id=BankAccountFake(**rcpt['debtor_bank_account']),
                move_line_id=MoveLineFake(**rcpt['duedate_move_line'], invoice_id=InvoiceFake(**rcpt['invoice'])),
                communication=rcpt['communication']
            )
            for rcpt in receipts
        ]

    # end __init__

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Utility class methods to simplify data loading
    @classmethod
    def build_from_json(cls, json_data: str) -> 'FakeData':
        """Given a JSON as string parse it to a dictionary and
        build the RiBaData object"""
        json_dict = json.loads(json_data)
        new_instance = cls(**json_dict)
        return new_instance
    # end build_from_json_doc

    @classmethod
    def build_from_json_doc(cls, json_doc_path: Path) -> 'FakeData':
        """Given the path to a JSON file read it's data, parse it to a
        dictionary and build the RiBaData object"""

        # Load content from test JSON dataset specified by full path
        json_data = json_doc_path.read_text()

        new_instance = cls.build_from_json(json_data)
        return new_instance
    # end build_from_json_doc

    @classmethod
    def build_from_test_data(cls, dataset_name: str) -> 'FakeData':
        """Given the name (without the '.json' suffix) of a dataset stored
        in the tests.data package load the contained data and build the
        RiBaData object"""

        # Load content from test JSON dataset specified by it's name
        json_data = load_data_as_text(dataset_name + '.json')

        new_instance = cls.build_from_json(json_data)
        return new_instance
    # end build_from_json_doc
# end Dataset



