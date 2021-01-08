from datetime import date, timedelta

import pytest

from ribalta.utils.validators import (
    validate_abi,
    validate_cab,
    validate_bank_account_number,
    validate_duedate,
    validate_sia,
    validate_zip
)

from ribalta.utils.errors import (
    ABIMissingError, ABIInvalidError, ABITypeError,
    CABMissingError, CABInvalidError, CABTypeError,
    AcctNumberMissingError, AcctNumberInvalidError, AcctNumberTypeError,
    DuedateMissingError, DuedateTooEarlyError, DuedateTypeError,
    SIAMissingError, SIATypeError, SIAInvalidError,
    ZIPInvalidError, ZIPTypeError
)


def test_validate_abi():
    
    with pytest.raises(ABIMissingError):
        validate_abi('', 'test')
    # end with
    
    with pytest.raises(ABIMissingError):
        validate_abi(None, 'test')
    # end with
    
    with pytest.raises(ABIMissingError):
        validate_abi(False, 'test')
    # end with
    
    with pytest.raises(ABIInvalidError):
        validate_abi('00000', 'test')
    # end with
    
    with pytest.raises(ABIInvalidError):
        validate_abi(00000, 'test')
    # end with
    
    with pytest.raises(ABIInvalidError):
        validate_abi('256', 'test')
    # end with
    
    with pytest.raises(ABIInvalidError):
        validate_abi('2aA56', 'test')
    # end with
    
    with pytest.raises(ABITypeError):
        validate_abi(['a'], 'test')
    # end with
    
    validate_abi(513, 'test')
    validate_abi(67267, 'test')
    validate_abi('07267', 'test')
    
# end test_validate_abi


def test_validate_cab():
    
    with pytest.raises(CABMissingError):
        validate_cab('', 'test')
    # end with
    
    with pytest.raises(CABMissingError):
        validate_cab(None, 'test')
    # end with
    
    with pytest.raises(CABMissingError):
        validate_cab(False, 'test')
    # end with
    
    with pytest.raises(CABInvalidError):
        validate_cab('00000', 'test')
    # end with
    
    with pytest.raises(CABInvalidError):
        validate_cab(00000, 'test')
    # end with
    
    with pytest.raises(CABInvalidError):
        validate_cab('256', 'test')
    # end with
    
    with pytest.raises(CABInvalidError):
        validate_cab('2aA56', 'test')
    # end with
    
    with pytest.raises(CABTypeError):
        validate_cab(['a'], 'test')
    # end with
    
    validate_cab(513, 'test')
    validate_cab(67267, 'test')
    validate_cab('07267', 'test')
    
# end test_validate_cab


def test_validate_acctnumber():

    with pytest.raises(AcctNumberMissingError):
        validate_bank_account_number('')
    # end with

    with pytest.raises(AcctNumberMissingError):
        validate_bank_account_number(None)
    # end with

    with pytest.raises(AcctNumberMissingError):
        validate_bank_account_number(False)
    # end with

    with pytest.raises(AcctNumberInvalidError):
        validate_bank_account_number('00000')
    # end with

    with pytest.raises(AcctNumberInvalidError):
        validate_bank_account_number(0)
    # end with

    with pytest.raises(AcctNumberInvalidError):
        validate_bank_account_number('256')
    # end with

    with pytest.raises(AcctNumberInvalidError):
        validate_bank_account_number('2aA56')
    # end with

    with pytest.raises(AcctNumberTypeError):
        validate_bank_account_number(['a'])
    # end with

    validate_bank_account_number(513)
    validate_bank_account_number(67267)

# end test_validate_acctnumber


def test_validate_duedate():

    with pytest.raises(DuedateMissingError):
        validate_duedate(False, 'test')
    # end with

    with pytest.raises(DuedateMissingError):
        validate_duedate(None, 'test')
    # end with

    with pytest.raises(DuedateTooEarlyError):
        validate_duedate(date.today(), 'test')
    # end with

    with pytest.raises(DuedateTooEarlyError):
        validate_duedate(date(209, 6, 18), 'test')
    # end with

    with pytest.raises(DuedateTypeError):
        validate_duedate([436], 'test')
    # end with
    
    validate_duedate(date.today() + timedelta(days=1), 'test')
    validate_duedate(date(7865, 4, 4), 'test')

# end test_validate_test_validate_duedate


def test_validate_sia():
    
    # '00000' must be accepted as sia code
    validate_sia('00000')
    
    with pytest.raises(SIAMissingError):
        validate_sia('')
    # end with

    with pytest.raises(SIAMissingError):
        validate_sia(None)
    # end with

    with pytest.raises(SIAMissingError):
        validate_sia(False)
    # end with

    with pytest.raises(SIAInvalidError):
        validate_sia('256')
    # end with

    with pytest.raises(SIAInvalidError):
        validate_sia('2aA56')
    # end with

    with pytest.raises(SIAInvalidError):
        validate_sia('3536f')
    # end with

    with pytest.raises(SIAInvalidError):
        validate_sia('g3536f')
    # end with

    with pytest.raises(SIAInvalidError):
        validate_sia('A3544446')
    # end with

    with pytest.raises(SIATypeError):
        validate_sia(['a'])
    # end with

    with pytest.raises(SIATypeError):
        validate_sia(0)
    # end with

    validate_sia('T4555')
    validate_sia('Z0092')
    validate_sia('30092')
    validate_sia('AOIT9')
    validate_sia('AOITX')

# end test_validate_sia


def test_validate_zip():

    with pytest.raises(ZIPInvalidError):
        validate_zip('00000')
    # end with

    with pytest.raises(ZIPInvalidError):
        validate_zip('256')
    # end with

    with pytest.raises(ZIPInvalidError):
        validate_zip('2aA56')
    # end with

    with pytest.raises(ZIPInvalidError):
        validate_zip('AA356')
    # end with

    with pytest.raises(ZIPInvalidError):
        validate_zip('3536F')
    # end with

    with pytest.raises(ZIPInvalidError):
        validate_zip('3536f')
    # end with

    with pytest.raises(ZIPInvalidError):
        validate_zip('g3536f')
    # end with

    with pytest.raises(ZIPInvalidError):
        validate_zip('A3544446')
    # end with

    with pytest.raises(ZIPInvalidError):
        validate_zip(0)
    # end with

    with pytest.raises(ZIPTypeError):
        validate_zip(['a'])
    # end with

    validate_zip('35036')
    validate_zip(35036)
    validate_zip('00129')
    
# end test_validate_zip
