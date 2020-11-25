from .tools.data_load import FakeData

from ribalta.riba import Document
from ribalta.utils.errors import ABIMissingError, CABMissingError, FiscalcodeMissingError, SIAInvalidError

import pytest


def test_cred_errors():
    
    with pytest.raises(ABIMissingError):
        test_data = FakeData.build_from_test_data('riba_cred_no_abi')
        Document(**test_data.head)
    # end with
    
    with pytest.raises(CABMissingError):
        test_data = FakeData.build_from_test_data('riba_cred_no_cab')
        Document(**test_data.head)
    # end with
    
    with pytest.raises(FiscalcodeMissingError):
        test_data = FakeData.build_from_test_data('riba_cred_no_fc')
        Document(**test_data.head)
    # end with
    
    with pytest.raises(SIAInvalidError):
        test_data = FakeData.build_from_test_data('riba_cred_bad_sia')
        Document(**test_data.head)
    # end with
    
# end test_cred_errors
