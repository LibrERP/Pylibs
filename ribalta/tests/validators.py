from pathlib import Path
import typing

from .data_load import load_data_as_bytes


CBI_RECORD_END = '\r\n'
MODEL_FILES_SUFFIX = '.cbi_reference'


class CBIReferenceValidator:
    """Validate CBI file against a reference file considered correct.
    IB and EF records are validated ignoring the creation date and the document
    name ("nome supporto"), but the validator checks that data that should be the
    same in the IB and EF records are actually the same
    NB: this class assumes the model file to be correct
    """

    # First and last character of various fields
    IB_DATE = (14, 19)
    IB_DOC_NAME = (20, 39)
    EF_DATE = IB_DATE
    EF_DOC_NAME = IB_DOC_NAME

    def __init__(self, cbi_doc: str):
        self._raw_data = cbi_doc

        # Simple data parsing
        self._ib, self._ef, self._receipts = self._cbi_data_splitter(
            self._raw_data
        )
    # end __init__

    def validate_data(self, data: str) -> None:
        # Simple data parsing
        ib, ef, receipts = self._cbi_data_splitter(data)

        # Start validation checks
        assert self._check_ib(ib)
        assert self._check_ef(ef)
        assert self._check_ib_ef_common_fields(ib, ef)
        assert len(self._receipts) == len(receipts)
        assert all(self._check_receipts(receipts))
    # end validate_data

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Utility class methods to simplify data loading
    @classmethod
    def build_from_file(cls, cbi_doc_file: Path) -> 'CBIReferenceValidator':
        # Data gets loaded as bytes and then converted to a sting using
        # .decode() to avoid automatic conversion of '\r\n' sequences in
        # '\n' performed by the read_text() method
        cbi_data = cbi_doc_file.read_bytes().decode()

        return cls(cbi_data)
    # end build_from_test_file

    @classmethod
    def build_from_reference_model(
            cls, dataset_name: str
    ) -> 'CBIReferenceValidator':

        # Load content from test dataset specified by it's name
        # Data gets loaded as bytes and then converted to a sting using
        # .decode() to avoid automatic conversion of '\r\n' sequences in
        # '\n' performed by the read_text() method
        cbi_data = load_data_as_bytes(
            dataset_name + MODEL_FILES_SUFFIX
        ).decode()

        return cls(cbi_data)
    # end build_from_test_model

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Private methods
    def _check_ib(self, ib: str) -> bool:

        whitened_ref_ib = self._fields_blanket(
            self._ib, [self.IB_DATE, self.IB_DOC_NAME]
        )

        whitened_ib = self._fields_blanket(
            ib, [self.IB_DATE, self.IB_DOC_NAME]
        )

        return whitened_ref_ib == whitened_ib
    # end _check_ib

    def _check_ef(self, ef: str) -> bool:

        whitened_ref_ef = self._fields_blanket(
            self._ef, [self.EF_DATE, self.EF_DOC_NAME]
        )

        whitened_ef = self._fields_blanket(
            ef, [self.EF_DATE, self.EF_DOC_NAME]
        )

        return whitened_ref_ef == whitened_ef
    # end _check_ef

    def _check_ib_ef_common_fields(self, ib: str, ef: str):

        ib_date = ib[self.IB_DATE[0] - 1:self.IB_DATE[1]]
        ib_name = ib[self.IB_DOC_NAME[0] - 1:self.IB_DOC_NAME[1]]

        ef_date = ib[self.IB_DATE[0] - 1:self.IB_DATE[1]]
        ef_name = ef[self.EF_DOC_NAME[0] - 1:self.EF_DOC_NAME[1]]

        return ib_date == ef_date and ib_name == ef_name
    # end _check_ib_ef_common_fields

    def _check_receipts(self, receipts: typing.List[str]) -> typing.List[bool]:

        checks = [False for _ in receipts]

        for i, ref_r, r in zip(
                range(0, len(self._receipts)), self._receipts, receipts
        ):
            print('----' + ref_r + '----')
            print('----' + r + '----')
            assert ref_r == r
            checks[i] = ref_r == r
        # end for

        return checks

    # end receipts

    @staticmethod
    def _fields_blanket(
            data: str,
            fields: typing.List[typing.Tuple[int, int]]
    ) -> str:

        new_data = data

        for field in fields:
            # Position of the first character of the field counting from 1
            field_s = field[0] - 1
            # Position of the character right after the field
            # counting from 1
            field_n = field[1]

            blacks = ' ' * (field_n - field_s)
            new_data = new_data[:field_s] + blacks + new_data[field_n:]
        # end for

        return new_data
    # end _fields_blanket

    @staticmethod
    def _cbi_data_splitter(
            data: str
    ) -> typing.Tuple[str, str, typing.List[str]]:
        records = data.split(CBI_RECORD_END)

        # Remove last element, it's just the empty line after the last "\r\n"
        records.pop(-1)

        ib = records.pop(0)
        ef = records.pop(-1)

        return ib, ef, records
    # end _cbi_data_splitter

# end CBIReferenceValidator
