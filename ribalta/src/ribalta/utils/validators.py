import re
import typing
from datetime import date, timedelta

from .errors import (
    AcctNumberMissingError, AcctNumberInvalidError, AcctNumberTypeError,
    ABIMissingError, ABIInvalidError, ABITypeError,
    CABMissingError, CABInvalidError, CABTypeError,
    DuedateMissingError, DuedateTooEarlyError, DuedateTypeError,
    SIAMissingError, SIATypeError, SIAInvalidError,
    ZIPInvalidError, ZIPTypeError
)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def validate_abi(abi: typing.Union[str, int, bool, None], nome_soggetto: str):

    if abi == '' or abi is False or abi is None:
        raise ABIMissingError(f'Codice ABI mancante per "{nome_soggetto}"')

    elif isinstance(abi, int):
        validate_abi(str(abi).rjust(5, '0'), nome_soggetto)

    elif isinstance(abi, str):
        if not abi.isnumeric():
            raise ABIInvalidError(
                f'Codice ABI ({abi}) errato per "{nome_soggetto}".'
                f' - '
                f'Il codice ABI deve essere un numero di 5 cifre'
            )

        elif not len(abi) == 5:
            raise ABIInvalidError(
                f'Codice ABI ({abi}) errato per "{nome_soggetto}".'
                f' - '
                f'Il codice ABI deve essere un numero di 5 cifre'
            )

        elif int(abi) == 0:
            raise ABIInvalidError(
                f'Codice ABI ({abi}) errato per "{nome_soggetto}".'
                f' - '
                f'Il codice ABI non può essere composto da 5 zeri (00000)')

        else:
            # Codice ABI OK
            return
        # end if

    else:
        raise ABITypeError(
            f'Tipo dato non valido ({type(abi)}) '
            f'per il codice ABI di "{nome_soggetto}".'
            f' - '
            f'Il tipo può essere stringa (str) o numero intero (int)'
        )
    # end if
# end validate_abi


def validate_cab(cab: typing.Union[str, int, bool, None], nome_soggetto: str):

    if cab == '' or cab is False or cab is None:
        raise CABMissingError(f'Codice CAB mancante per "{nome_soggetto}"')
    
    elif isinstance(cab, int):
        validate_cab(str(cab).rjust(5, '0'), nome_soggetto)

    elif cab in ('', False, None):
        raise CABMissingError(f'Codice CAB mancante per "{nome_soggetto}"')

    elif isinstance(cab, str):
        if not cab.isnumeric():
            raise CABInvalidError(
                f'Codice CAB ({cab}) errato per "{nome_soggetto}".'
                f' - '
                f'Il codice CAB deve essere un numero di 5 cifre'
            )

        elif not len(cab) == 5:
            raise CABInvalidError(
                f'Codice CAB ({cab}) errato per "{nome_soggetto}".'
                f' - '
                f'Il codice CAB deve essere un numero di 5 cifre'
            )

        elif int(cab) == 0:
            raise CABInvalidError(
                f'Codice CAB ({cab}) errato per "{nome_soggetto}".'
                f' - '
                f'Il codice CAB non può essere composto da 5 zeri (00000)')

        else:
            # Codice CAB OK
            return
        # end if

    else:
        raise CABTypeError(
            f'Tipo dato non valido ({type(cab)}) '
            f'per il codice CAB di "{nome_soggetto}".'
            f' - '
            f'Il tipo può essere stringa (str) o numero intero (int)'
        )
    # end if
# end validate_cab


def validate_bank_account_number(
    account_number: typing.Union[str, int, bool, None]
):
    acct_num = account_number
    if acct_num == '' or acct_num is False or acct_num is None:
        raise AcctNumberMissingError(
            'Numero di conto corrente del creditore mancante'
        )
    
    elif isinstance(account_number, int):
        acc_number_str = str(account_number).rjust(12, '0')
        validate_bank_account_number(acc_number_str)

    elif isinstance(account_number, str):
        acc_number_str = str(account_number)
        
        # Pick the last 12 characters to correctly manage italian IBAN passed
        # as account numbers
        if len(acc_number_str) == 27 and acc_number_str.startswith('IT'):
            acc_number_str = acc_number_str[-12:]
        else:
            acc_number_str = account_number
        # end if
        
        if not acc_number_str.isnumeric():
            raise AcctNumberInvalidError(
                f'Numero di contro corrente del creditore errato'
                f' - '
                f'Il contro coorente deve essere un numero di 12 cifre'
            )

        elif not len(acc_number_str) == 12:
            raise AcctNumberInvalidError(
                f'Numero di contro corrente del creditore errato'
                f' - '
                f'Il contro coorente deve essere un numero di 12 cifre'
            )

        elif int(acc_number_str) == 0:
            raise AcctNumberInvalidError(
                f'Numero di contro corrente del creditore errato'
                f' - '
                f'Il numero del conto non può essere composto solo da zeri')

        else:
            # Codice CAB OK
            return
        # end if

    else:
        raise AcctNumberTypeError(
            f'Tipo dato non valido ({type(account_number)}) '
            f'per il numero di conto corrente del creditore.'
            f' - '
            f'Il tipo può essere stringa (str) o numero intero (int)'
        )
    # end if
# end validate_bank_account_number


def validate_duedate(duedate: typing.Union[date, bool, None], nome_soggetto: str):
    
    tomorrow = date.today() + timedelta(days=1)
    
    if not duedate:
        raise DuedateMissingError(
            f'Data di scadenza mancante per "{nome_soggetto}"'
        )
    
    elif not isinstance(duedate, date):
        raise DuedateTypeError(
            f'Tipo dato non valido ({type(duedate)}) '
            f'per la data di scadenza di "{nome_soggetto}".'
            f' - '
            f'Il tipo deve essere datetime.date'
        )
    
    elif not duedate >= tomorrow:
        raise DuedateTooEarlyError(
            f'Data scadenza pagamento ({duedate}) troppo vicina nel tempo '
            f'per "{nome_soggetto}".'
            f' - '
            f'La data discadenza non può essere prima di domani.'
        )
    
    else:
        pass
    # end if
# end validate_duedate


def validate_sia(sia_code: typing.Union[str, bool, None]) -> None:
    # Verifica SIA: campo obbligatorio. Il formato sia prevede una
    # lettera seguita da 4 numeri

    if sia_code == '' or sia_code is False or sia_code is None:
        raise SIAMissingError(
            'Codice SIA del creditore mancante'
        )

    elif not isinstance(sia_code, str):
        raise SIATypeError(
            'Tipo dato non valido per il codice SIA: '
            'il tipo deve essere stringa (str)'
        )

    elif not len(sia_code) == 5:
        raise SIAInvalidError(
            'Codice SIA errato: il codice deve essere di lunghezza 5')
    
    elif not re.match(r'[A-Z0-9]{5}', sia_code):
        raise SIAInvalidError(
            'Codice SIA errato: il codice può contenere solo lettere maiuscole e cifre')

    else:
        # Codice SIA OK
        pass
    # end if
# end validate zip


def validate_zip(zip_code: typing.Union[str, int, bool, None]) -> None:
    # Verifica CAP: se c'è deve essere numerico e di 5 caratteri,
    # ma può tranquillamente non esserci!!

    if zip_code == '' or zip_code is False or zip_code is None:
        # Empty ZIP code is OK!
        return

    elif isinstance(zip_code, int):
        validate_zip(str(zip_code).rjust(5, '0'))

    elif isinstance(zip_code, str):
        if not zip_code.isnumeric():
            raise ZIPInvalidError(
                'CAP errato. Il CAP deve essere un numero di 5 cifre')

        elif len(zip_code) != 5:
            raise ZIPInvalidError(
                'CAP errato. Il CAP deve essere un numero di 5 cifre')

        elif int(zip_code) == 0:
            raise ZIPInvalidError(
                'CAP errato. Il CAP non può essere composto da 5 zeri (00000)')

        else:
            # Codice ZIP OK
            return
        # end if

    else:
        raise ZIPTypeError(
            f'Tipo dato non valido per il CAP: {type(zip_code)}'
            f' - '
            f'Il tipo può essere stringa (str) o numero intero (int)'
        )
    # end if
# end validate zip
