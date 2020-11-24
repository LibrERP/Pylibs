# Try importing odoo functions and classes,
# if import fails add define for the required
# functions and classes
try:

    from odoo import _
    from odoo.exceptions import UserError

except ModuleNotFoundError as mnfe:

    def _(val):
        return val
    # end if

    class UserError(Exception):
        pass
    # end UserError
# end try / except
