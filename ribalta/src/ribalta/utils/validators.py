import typing

from .odoo_stuff import UserError
# TODO: controllare che la data di pagamento (data di scadenza) delle linee sia NEL FUTURO (almeno domani, NON oggi)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def validate_sia(sia_code: typing.Union[str, int, bool, None]) -> None:
    # Verifica SIA: campo obbligatorio. Il formato sia prevede una
    # lettera seguita da 4 numeri

    if sia_code in (None, '', False):
        raise UserError(
            'Codice SIA del creditore mancante'
        )

    elif not isinstance(sia_code, str):
        raise UserError(
            'Tipo dato non valido per il codice SIA: '
            'il tipo deve essere stringa (str)'
        )

    elif not len(sia_code) == 5:
        raise UserError(
            'Codice SIA errato: il codice deve essere di lunghezza 5')

    elif not sia_code[0].isalpha():
        raise UserError(
            'Codice SIA errato: il primo componente deve essere una lettera')

    elif not sia_code[1:].isnumeric():
        raise UserError(
            'Codice SIA errato: gli ultimi 4 componenti devono essee numeri')

    else:
        # Codice SIA OK
        pass
    # end if
# end validate zip


def validate_zip(zip_code: typing.Union[str, int, bool, None]) -> None:
    # Verifica CAP: se c'è deve essere numerico e di 5 caratteri,
    # ma può tranquillamente non esserci!!

    if zip_code in (None, '', False):
        # Empty ZIP code is OK!
        return

    elif isinstance(zip_code, int):
        validate_zip(str(zip_code).rjust(5, '0'))

    elif isinstance(zip_code, str):
        if not zip_code.isnumeric():
            raise UserError(
                'CAP errato. Il CAP deve essere un numero di 5 cifre')

        elif len(zip_code) != 5:
            raise UserError(
                'CAP errato. Il CAP deve essere un numero di 5 cifre')

        elif int(zip_code) == 0:
            raise UserError(
                'CAP errato. Il CAP non può essere composto da 5 zeri (00000)')

        else:
            # Codice ZIP OK
            return
        # end if

    else:
        raise UserError(
            f'Tipo dato non valido per il CAP: {type(zip_code)}'
            f' - '
            f'Il tipo può essere stringa (str) o numero intero (int)'
        )
    # end if
# end validate zip


def validate_abi(abi: typing.Union[str, int, bool, None], nome_soggetto: str):

    if not abi:
        raise UserError(f'Codice ABI mancante per "{nome_soggetto}"')

    elif isinstance(abi, int):
        validate_abi(str(abi).rjust(5, '0'))

    elif isinstance(abi, str):
        if not abi.isnumeric():
            raise UserError(
                f'Codice ABI errato per "{nome_soggetto}".'
                f' - '
                f'Il codice ABI deve essere un numero di 5 cifre'
            )

        elif not len(abi) == 5:
            raise UserError(
                f'Codice ABI errato per "{nome_soggetto}".'
                f' - '
                f'Il codice ABI deve essere un numero di 5 cifre'
            )

        elif int(abi) == 0:
            raise UserError(
                f'Codice ABI errato per "{nome_soggetto}".'
                f' - '
                f'Il codice ABI non può essere composto da 5 zeri (00000)')

        else:
            # Codice ABI OK
            return
        # end if

    else:
        raise UserError(
            f'Tipo dato non valido ({type(abi)}) '
            f'per il codice ABI di "{nome_soggetto}".'
            f' - '
            f'Il tipo può essere stringa (str) o numero intero (int)'
        )
    # end if
# end validate_abi


def validate_cab(cab: typing.Union[str, int, bool, None], nome_soggetto: str):

    if not cab:
        raise UserError(f'Codice CAB mancante per "{nome_soggetto}"')

    elif isinstance(cab, int):
        validate_cab(str(cab).rjust(5, '0'))

    elif isinstance(cab, str):
        if not cab.isnumeric():
            raise UserError(
                f'Codice CAB errato per "{nome_soggetto}".'
                f' - '
                f'Il codice CAB deve essere un numero di 5 cifre'
            )

        elif not len(cab) == 5:
            raise UserError(
                f'Codice CAB errato per "{nome_soggetto}".'
                f' - '
                f'Il codice CAB deve essere un numero di 5 cifre'
            )

        elif int(cab) == 0:
            raise UserError(
                f'Codice CAB errato per "{nome_soggetto}".'
                f' - '
                f'Il codice CAB non può essere composto da 5 zeri (00000)')

        else:
            # Codice CAB OK
            return
        # end if

    else:
        raise UserError(
            f'Tipo dato non valido ({type(cab)}) '
            f'per il codice CAB di "{nome_soggetto}".'
            f' - '
            f'Il tipo può essere stringa (str) o numero intero (int)'
        )
    # end if
# end validate_cab


def validate_bank_account_number(account_number: typing.Union[str, int, bool, None]):

    if not account_number:
        raise UserError(f'Numero di conto corrente del creditore mancante')

    elif isinstance(account_number, int):
        validate_cab(str(account_number).rjust(12, '0'))

    elif isinstance(account_number, str):
        if not account_number.isnumeric():
            raise UserError(
                f'Numero di contro corrente del creditore errato'
                f' - '
                f'Il contro coorente deve essere un numero di 12 cifre'
            )

        elif not len(account_number) == 12:
            raise UserError(
                f'Numero di contro corrente del creditore errato'
                f' - '
                f'Il contro coorente deve essere un numero di 12 cifre'
            )

        elif int(account_number) == 0:
            raise UserError(
                f'Numero di contro corrente del creditore errato'
                f' - '
                f'Il numero del conto non può essere composto solo da zeri')

        else:
            # Codice CAB OK
            return
        # end if

    else:
        raise UserError(
            f'Tipo dato non valido ({type(account_number)}) '
            f'per il numero di conto corrente del creditore.'
            f' - '
            f'Il tipo può essere stringa (str) o numero intero (int)'
        )
    # end if
# end validate_bank_account_number
