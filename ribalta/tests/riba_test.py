from .tools.data_load import FakeData

from ribalta.riba import Document, Receipt
from ribalta.utils.errors import FiscalcodeMissingError, SIAInvalidError, FiscalcodeAndVATMissingError

import pytest


def test_cred_errors():
    
    with pytest.raises(FiscalcodeMissingError):
        test_data = FakeData.build_from_test_data('riba_cred_no_fiscode_no_vat')
        Document(**test_data.head)
    # end with
    
    with pytest.raises(SIAInvalidError):
        test_data = FakeData.build_from_test_data('riba_cred_bad_sia')
        Document(**test_data.head)
    # end with
    
# end test_cred_errors


def test_debt_errors():

    with pytest.raises(FiscalcodeAndVATMissingError):
        test_data = FakeData.build_from_test_data('riba_debt_no_fiscode_no_vat')

        riba_doc = Document(**test_data.head)

        for rcpt in test_data.receipts:
            riba_doc.add_receipt(Receipt(**rcpt))
        # end for
    # end with

# end test_cred_errors
