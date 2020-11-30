# Try importing odoo functions and classes, if import fails add define for
# the required functions and classes
try:
    from odoo.exceptions import UserError
except (ModuleNotFoundError, ImportError) as err:
    class UserError(Exception):
        pass
    # end UserError
# end try / except

try:
    from odoo import _
except (ModuleNotFoundError, ImportError) as err:
    def _(val):
        return val
    # end if
# end try / except
