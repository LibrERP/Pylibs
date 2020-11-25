from pathlib import Path
import typing

from .data_load import load_data_as_bytes


CBI_RECORD_END = '\r\n'
CBI_RECORD_LENGTH = 120
MODEL_FILES_SUFFIX = '.cbi_reference'


class CBIReferenceModelValidator:
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
    def build_from_file(cls, cbi_doc_file: Path) -> 'CBIReferenceModelValidator':
        # Data gets loaded as bytes and then converted to a sting using
        # .decode() to avoid automatic conversion of '\r\n' sequences in
        # '\n' performed by the read_text() method
        cbi_data = cbi_doc_file.read_bytes().decode()

        return cls(cbi_data)
    # end build_from_test_file

    @classmethod
    def build_from_reference_model(
            cls, dataset_name: str
    ) -> 'CBIReferenceModelValidator':

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
# end CBIReferenceModelValidator


class CBIFormatValidator:
    
    def __init__(self, cbi_doc: str):
        self._cbi_doc = cbi_doc
        self._records = cbi_doc.split(CBI_RECORD_END)[:-1]
    # end __init__
    
    def validate(self):
        self._check_records_length()
        self._check_ib()
        self._check_ib()
        self._check_ib_ef()
        self._check_receipts()
    # end check
    
    def _check_records_length(self):
        for r in self._records:
            assert len(r) == CBI_RECORD_LENGTH
    # end _check_records_length
    
    def _check_ib(self):
        
        # Estrazione del record IB
        ib = self._records[0]
        
        print('----' + ib + '----')
        
        # Verifica correttezza inizio record
        assert ib[0] == ' '
        assert ib[1:3] == 'IB'
        assert ib[45:104] == ' ' * (104 - 45)
        assert ib[111:113] == ' ' * (113 - 111)
        assert ib[113:] == 'E' + ' ' * 6
    
    def _check_ef(self):
        
        # Estrazione del record EF
        ef = self._records[-1]
        
        assert ef[0] == ' '
        assert ef[1:3] == 'EF'
        assert ef[92:113] == ' ' * (92 - 113)
        assert ef[114:] == ' ' * 5 + 'E'
    
    def _check_ib_ef(self):
        
        # Estrazione dei record IB e EF
        ib = self._records[0]
        ef = self._records[-1]
        
        # Verifica correttezza dati comuni ad entrambi i record
        assert ib[3:39] == ef[3:39]
    # end _check_head_tail
    
    def _check_receipts(self):
        
        # Receipts records obtained removing first and last record from the
        # list of records
        receipts_records = self._records[1:-1]
        
        # Since each receipt is composed of 7 records let's check if
        # the number of records is correct: one removed the first and
        # the last record (IB and EF records) the number of remaining
        # record should be a multiple of 7
        assert len(receipts_records) % 7 == 0
        
        # Compute the number of receipts. In this line of code the integer
        # division is used since the previous assert instruction guarantee
        # that the number of records is an integer multiple of 7
        number_of_receipts = len(receipts_records) // 7
        
        for receipt_index in range(number_of_receipts):
            first_record = receipt_index * 7
            last_record = first_record + 6
            self._check_single_receipt(
                receipts_records[first_record:last_record + 1],
                receipt_index + 1
            )
        # end for
    # end _check_receipts
    
    @staticmethod
    def _check_single_receipt(receipt: typing.List[str], progressive_number):
        
        def check_record_14(r: str):
            assert r.startswith(' 14')
            assert r[3:10] == progressive_number_str
            assert r[10:22] == ' ' * (22 - 10)
            assert r[79:91] == ' ' * (91 - 79)
            assert r[114:119] == ' ' * (119 - 114)
            assert r[119] == 'E'
        # end
        
        def check_record_20(r: str):
            assert r.startswith(' 20')
            assert r[3:10] == progressive_number_str
            assert r[106:120] == ' ' * (120 - 106)
        # end
        
        def check_record_30(r: str):
            assert r.startswith(' 30')
            assert r[3:10] == progressive_number_str
            assert r[86:120] == ' ' * (120 - 86)
        # end
        
        def check_record_40(r: str):
            assert r.startswith(' 40')
            assert r[3:10] == progressive_number_str
        # end
        
        def check_record_50(r: str):
            assert r.startswith(' 50')
            assert r[3:10] == progressive_number_str
            assert r[90:100] == ' ' * (100 - 90)
            assert r[116:120] == ' ' * (120 - 116)
        # end
        
        def check_record_51(r: str):
            assert r.startswith(' 51')
            assert r[3:10] == progressive_number_str
            assert r[71:120] == ' ' * (120 - 71)
        # end
        
        def check_record_70(r: str):
            assert r.startswith(' 70')
            assert r[3:10] == progressive_number_str
            assert r[10:88] == ' ' * (88 - 10)
            assert r[100:103] == ' ' * (103 - 100)
            assert r[103:120] == ' ' * (120 - 103)
        # end

        progressive_number_str = str(progressive_number).rjust(7, '0')
        
        check_record_14(receipt[0])
        check_record_20(receipt[1])
        check_record_30(receipt[2])
        check_record_40(receipt[3])
        check_record_50(receipt[4])
        check_record_51(receipt[5])
        check_record_70(receipt[6])

# end CBIFormatValidator


class CBIReceiptValidator:
    pass
# end CBIReceiptValidator
