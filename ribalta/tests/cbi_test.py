from .data_load import FakeData
from .validators import CBIReferenceValidator

from ribalta.cbi import Document, Line


def test_riba_ok():

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test environment setup

    # Build the validation object
    validator = CBIReferenceValidator.build_from_reference_model('riba_ok')

    # Read data from json
    test_data = FakeData.build_from_test_data('riba_ok')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Emulate the real process using the test data

    # Build the CBI document object: use the test data
    # to perform the same steps of the real building process
    cbi_doc = Document(**test_data.head)
    for line in test_data.lines:
        cbi_doc.add_line(Line(**line))
    # end for

    # Render the cbi_doc as string
    cbi_doc = cbi_doc.render_cbi()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Validate the result against the reference document

    # Perform the validation against the reference model
    validator.validate_data(cbi_doc)

# end test_riba_ok
