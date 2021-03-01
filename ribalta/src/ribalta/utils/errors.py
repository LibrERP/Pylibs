from .odoo_stuff import UserError


class AcctNumberMissingError(UserError):
    pass
# end AcctNumberMissingError


class AcctNumberInvalidError(UserError):
    pass
# end AcctNumberInvalidError


class AcctNumberTypeError(UserError):
    pass
# end AcctNumberTypeError


class ABIMissingError(UserError):
    pass
# end ABIMissingError


class ABIInvalidError(UserError):
    pass
# end ABIInvalidError


class ABITypeError(UserError):
    pass
# end ABITypeError


class CABMissingError(UserError):
    pass
# end CABMissingError


class CABInvalidError(UserError):
    pass
# end CABInvalidError


class CABTypeError(UserError):
    pass
# end CABTypeError


class DuedateMissingError(UserError):
    pass
# end DuedateMissingError


class DuedateTooEarlyError(UserError):
    pass
# end DuedateTooEarlyError


class DuedateTypeError(UserError):
    pass
# end DuedateMissingError


class FiscalcodeMissingError(UserError):
    pass
# end CABTypeError


class FiscalcodeAndVATMissingError(UserError):
    pass
# end CABTypeError


class SIAMissingError(UserError):
    pass
# end SIAMissingError


class SIATypeError(UserError):
    pass
# end SIATypeError


class SIAInvalidError(UserError):
    pass
# end SIAInvalidError


class ZIPInvalidError(UserError):
    pass
# end ZIPInvalidError


class ZIPTypeError(UserError):
    pass
# end ZIPTypeError
