from .tools.data_load import FakeData
from .tools.validators import CBIReferenceModelValidator, CBIFormatValidator

from ribalta.riba import Document, Receipt


def test_reference_riba_ok():

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test environment setup

    # Read data from json
    test_data = FakeData.build_from_test_data('riba_ok')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Emulate the real process using the test data

    # Build the CBI document object: use the test data
    # to perform the same steps of the real building process
    riba_doc = Document(**test_data.head)
    for rcpt in test_data.receipts:
        riba_doc.add_receipt(Receipt(**rcpt))
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

# end test_reference_riba_ok


def test_reference_riba_debt_fiscode_empty_with_vat():
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test environment setup

    # Read data from json
    test_data = FakeData.build_from_test_data('riba_debt_fiscode_empty_str')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Emulate the real process using the test data

    # Build the CBI document object: use the test data
    # to perform the same steps of the real building process
    riba_doc = Document(**test_data.head)
    for rcpt in test_data.receipts:
        riba_doc.add_receipt(Receipt(**rcpt))
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

# end test_reference_riba_debt_fiscode_empty_with_vat


def test_reference_riba_debt_fiscode_false_with_vat():
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test environment setup

    # Read data from json
    test_data = FakeData.build_from_test_data('riba_debt_fiscode_false')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Emulate the real process using the test data

    # Build the CBI document object: use the test data
    # to perform the same steps of the real building process
    riba_doc = Document(**test_data.head)
    for rcpt in test_data.receipts:
        riba_doc.add_receipt(Receipt(**rcpt))
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

# end test_reference_riba_debt_fiscode_false_with_vat


def test_reference_riba_cred_no_fiscode():
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test environment setup

    # Read data from json
    test_data = FakeData.build_from_test_data('riba_cred_no_fiscode')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Emulate the real process using the test data

    # Build the CBI document object: use the test data
    # to perform the same steps of the real building process
    riba_doc = Document(**test_data.head)
    for rcpt in test_data.receipts:
        riba_doc.add_receipt(Receipt(**rcpt))
    # end for

    # Render the riba_doc as string
    riba_doc = riba_doc.render_cbi()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Validate the result against the reference document

    # Build the validation objects
    format_validator = CBIFormatValidator(riba_doc)
    model_validator = CBIReferenceModelValidator.build_from_reference_model('riba_cred_no_fiscode')

    # Check document format correctness
    format_validator.validate()

    # Perform the validation against the reference model
    model_validator.validate_data(riba_doc)

# end test_reference_riba_cred_no_fiscode


def test_riba_grouping():
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test environment setup

    # Read data from json
    test_data = FakeData.build_from_test_data('riba_collapsible_ok')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Emulate the real process using the test data

    # Build the CBI document object: use the test data
    # to perform the same steps of the real building process
    riba_doc = Document(**test_data.head)
    for rcpt in test_data.receipts:
        riba_doc.add_receipt(Receipt(**rcpt))
    # end for

    # Render the riba_doc as string
    cbi_doc = riba_doc.render_cbi()
    cbi_doc_grouped = riba_doc.render_cbi(group=True)
    
    # Ungrouped CBI document must have more records than grouped one
    # because the test data used permits grouping
    assert len(cbi_doc.split('\r\n')) > len(cbi_doc_grouped.split('\r\n'))
# end test_riba_ok
