from .tools.data_load import FakeData
from .tools.validators import CBIReferenceModelValidator, CBIFormatValidator

from ribalta.riba import Document, Receipt


def test_riba_with_model():

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test environment setup

    # Read data from json
    test_data = FakeData.build_from_test_data('riba_ok')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Emulate the real process using the test data

    # Build the CBI document object: use the test data
    # to perform the same steps of the real building process
    riba_doc = Document(**test_data.head)
    for line in test_data.lines:
        riba_doc.add_receipt(Receipt(**line))
    # end for

    # Render the riba_doc as string
    riba_doc = riba_doc.render_cbi()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Validate the result against the reference document

    # Build the validation objects
    format_validator = CBIFormatValidator(riba_doc)
    model_validator = CBIReferenceModelValidator.build_from_reference_model('riba_ok')
    
    # Check document format correctness
    format_validator.validate()

    # Perform the validation against the reference model
    model_validator.validate_data(riba_doc)

# end test_riba_ok
