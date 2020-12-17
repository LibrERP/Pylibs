##
##
## Autore: Marco Tosato - Didotech Srl - 2020-11-20
##
##
## Template per generazione documenti CBI secondo lo standard tecnico
## descritto nel documento:
##    Nome: CBI-ICI-001
##    Versione: v. 6.01 - Pagine 21
##    Ultimo aggiornamento 15-12-2006
##    Autore: Segreteria Tecnica
##    Revisore: D.ssa Liliana Fratini Passi
##
##
<%
    import re
    from unidecode import unidecode

    # Enable debug messages
    debug_active = False

    # Block of convenience constants
    R_IB_START = ' IB'
    R_14_START = ' 14'
    R_20_START = ' 20'
    R_30_START = ' 30'
    R_40_START = ' 40'
    R_50_START = ' 50'
    R_51_START = ' 51'
    R_70_START = ' 70'
    R_EF_START = ' EF'

    R_END = '\r'

    RECORDS_IN_EACH_RIBA = 7
    BLANK_CHAR = ' '


    # Block of convenience functions

    def fldsz(first_char_index, last_char_index):
        """Compute the size of a field in characters given the index of the
        first and last characters of the field itself"""
        return (last_char_index - first_char_index) + 1
    # end fldsz

    def riferimento_al_debito(receipt):
        if receipt.is_group:

            # Build a description for each receipt
            descriptions = map(
                lambda r: f'{r.invoice_number} {r.amount:.2f}',
                receipt.grouped_receipts
            )

            # Merge the descriptions
            msg = unidecode(f'Fatt: {", ".join(descriptions)}')

        else:

            i_num = receipt.invoice_number
            i_date = receipt.invoice_date
            i_amount = receipt.amount

            msg = unidecode(f'PER LA FATTURA N. {i_num} DEL {i_date:%d/%m/%Y} IMP {i_amount}')

        # end if

        # Format the message and return the result
        msg_formatted = msg.ljust(80, ' ')[:80]
        return msg_formatted
    # end riferimento_al_debito

    def f_unidecode(content):
        return unidecode(content)
    # end f_unidecode

    def f_acct_num(account_number):
        # Take the last 12 characters of the supplied account number,
        # this way we can safely manage Italian IBAN codes ...even if
        # the supplied code is an IBAN code the account number will be
        # extracted correctly.
        # If the supplied number is less than 12 characters the whole
        # code will be used.
        return str(account_number).strip().rjust(12, '0')[-12:]
    # end f_acct_num

    def loop_num_to_num_progr(loop_itration_number):
        return str(loop_itration_number + 1).rjust(7, '0')[:7]
    # end loop_num_to_num_progr

    def f_num_of_records(num_of_records):
        return str(num_of_records).rjust(7, '0')[:7]
    # end f_num_of_records

    f_num_of_disposizioni = f_num_of_records

    def f_rjust_and_trim(content, width, fill_char):
        return unidecode(str(content)).strip().rjust(width, fill_char)[:width]
    # end ljust_and_trim

    f_zip_code = lambda content: f_rjust_and_trim(content, 5, '0')
    f_number_of_receipts = lambda content: f_rjust_and_trim(content, 10, '0')
    f_cab = lambda content: f_rjust_and_trim(content, 5, '0')
    f_abi = lambda content: f_rjust_and_trim(content, 5, '0')
    f_sia = lambda content: f_rjust_and_trim(content, 5, '!')

    def f_ljust_and_trim(content, width, fill_char):
        return unidecode(str(content)).strip().ljust(width, fill_char)[:width]
    # end f_ljust_and_trim

    f_ljust16 = lambda content: f_ljust_and_trim(content, 16, ' ')
    f_ljust20 = lambda content: f_ljust_and_trim(content, 20, ' ')
    f_ljust24 = lambda content: f_ljust_and_trim(content, 24, ' ')
    f_ljust25 = lambda content: f_ljust_and_trim(content, 25, ' ')
    f_ljust30 = lambda content: f_ljust_and_trim(content, 30, ' ')
    f_ljust50 = lambda content: f_ljust_and_trim(content, 50, ' ')
    f_ljust60 = lambda content: f_ljust_and_trim(content, 60, ' ')
    f_creditor_descr = f_ljust24
    f_creditor_fiscode = lambda content: f_rjust_and_trim(content, 24, ' ')

    def f_amount_line(amount):
        amount_cents = int(round(float(amount) * 100))
        return str(amount_cents).rjust(13, '0')
    # end f_amount_line

    def f_amount_total(amount):
        amount_cents = int(round(float(amount) * 100))
        return str(amount_cents).rjust(15, '0')
    # end f_amount_total

    def f_fiscode(fiscode):
        return fiscode.strip().ljust(16,' ')
    # end f_fiscode

    def f_docname(docname):
        return docname.ljust(20, ' ')
    # end f_doc_name

%>\
##
##
## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## ............................................................................
##                                Record IB
## ............................................................................
## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
<%debug_active and print('R_IB_START')%>\
## 1-3 - ' IB'
${R_IB_START}\
## 4-8 - Mittente: codice SIA dell'azienda mittente
${doc.sia_code | f_sia}\
## 9-13 - Ricevente: ABI banca assuntrice
${doc.creditor_bank_account.bank_abi | f_abi}\
## 14-19 - Data creazione: data creazione del flusso da parte dell'azienda (GGMMAA)
${doc.creation_date.strftime('%d%m%y')}\
## 20-39 - Nome supporto: composizione libera, ma deve essere univoco nell'ambito della data di creazione a parità di mittente e ricevente
${doc.name | f_docname}\
## 40-45 - Campo libero: a disposizione del mittente
${BLANK_CHAR * fldsz(40, 45)}\
## 46-104 - Filler
${BLANK_CHAR * fldsz(46, 104)}\
## 105-111 - Qualificatore di flusso: non utilizzato da questa implementazione, riempire con spazi
${BLANK_CHAR * fldsz(105, 111)}\
## 112-113 - Filler
${BLANK_CHAR * fldsz(112, 113)}\
## 114 - Codice divisa: assume valore fisso 'E'
${'E'}\
## 115 - Filler
${BLANK_CHAR}\
## 116-120 - Non disponibile (riempire con spazi)
${BLANK_CHAR * fldsz(116, 120)}\
${R_END}
##
##
##
##
## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Lines
## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
<%debug_active and print()%>\
% for line in lines:
<%
    # Numero progressivo della ricevuta (parte da '1')
    num_progr = loop_num_to_num_progr(loop.index)
    num_disposizioni = loop.index + 1
%>\
##
##
##
##
## ............................................................................
## .................... Record 14 .............................................
## ............................................................................
<%debug_active and print('\tR_14_START')%>\
## 1-3 - ' 14'
${R_14_START}\
## 4-10 - Numero progressivo: numero della disposizione all'interno del flusso
${num_progr}\
## 11-22 - Filler
${BLANK_CHAR * fldsz(11, 22)}\
## 21-28 - Data pagamento: data di scadenza (GGMMAA)
${line.duedate.strftime('%d%m%y')}\
## 29-33 - Causale: assume valore fisso '30000'
30000\
## 34-46 - Importo: importo della ricevuta in centesimi di Euro
${line.amount | f_amount_line}\
## 47 - Segno: assume valore fisso '-'
-\
## Coordinate banca assuntrice
##     48-52 - ABI assuntrice
##     53-57 - CAB assuntrice
##     58-69 - Numero di conto
${doc.creditor_bank_account.bank_abi | f_abi}\
${doc.creditor_bank_account.bank_cab | f_cab}\
${doc.creditor_bank_account.sanitized_acc_number | f_acct_num}\
## - - - - - - - - - -
## Coordinate banca domiciliataria
##     70-74 - ABI domiciliataria
##     75-79 - CAB domiciliataria
${line.debtor_bank.abi | f_abi}\
${line.debtor_bank.cab | f_cab}\
## - - - - - - - - - -
## 80-91 - Filler
${BLANK_CHAR * fldsz(80, 91)}\
## Coordinate azienda creditrice
##     92-96 - codice SIA del cliente ordinante
##     97 - Tipo codice: assume valore fisso '4'
##     98-113 - Codice cliente debitore: codice con il quale il debitore è conosciuto dal creditore
##     114 - Flag tipo debitore: nel caso il debitore sia una banca va valorizzato con 'B', altrimenti va lasciato in bianco
${doc.sia_code | f_sia}\
4\
${line.debtor_client_code | f_unidecode,f_ljust16}\
${BLANK_CHAR}\
## - - - - - - - - - -
## 115-119 - Filler
${BLANK_CHAR * fldsz(115, 119)}\
## 120 - Codice divisa: deve coincidere con l'omonimo campo del record 'IB' (valorizzato sempre a 'E')
${'E'}\
${R_END}
##
##
##
##
## ............................................................................
## .................... Record 20 .............................................
## ............................................................................
<%debug_active and print('\tR_20_START')%>\
## 1-3 - ' 20'
${R_20_START}\
## 4-10 - Numero progressivo: stesso valore omonimo campo del record 14
${num_progr}\
## Descrizione del creditore (4 segmenti da 24 caratteri)
##     11-34 - Descrizione del creditore: primo segmento, testo libero
##     35-58 - Descrizione del creditore: secondo segmento, testo libero
##     59-82 - Descrizione del creditore: terzo segmento, testo libero
##     83-106 - Descrizione del creditore: quarto segmento, testo libero
${doc.creditor_company_name                | f_creditor_descr}\
${doc.creditor_company_addr_street         | f_creditor_descr}\
${doc.creditor_company_addr_zip_city_state | f_creditor_descr}\
${doc.creditor_fiscode_or_vat              | f_creditor_fiscode}\
## - - - - - - - - - -
## 107-120 - Filler
${BLANK_CHAR * fldsz(107, 120)}\
${R_END}
##
##
##
##
## ............................................................................
## .................... Record 30 .............................................
## ............................................................................
<%debug_active and print('\tR_30_START')%>\
## 1-3 - ' 30'
${R_30_START}\
## 4-10 - Numero progressivo: stesso valore omonimo campo del record 14
${num_progr}\
## Descrizione debitore (2 segmenti da 30 caratteri)
##     11-40 + 41-70 - Descrizione del debitore: due segmenti da 30 caratteri accorpati
##     41-70 - Codifica fiscale: codice fiscale cliente debitore
${line.debtor_name | f_ljust60}\
${line.debtor_fiscalcode | f_fiscode}\
## - - - - - - - - - -
## 87-120 - Filler
${BLANK_CHAR * fldsz(87, 120)}\
${R_END}
##
##
##
##
## ............................................................................
## .................... Record 40 .............................................
## ............................................................................
<%debug_active and print('\tR_40_START')%>\
## 1-3 - ' 40'
${R_40_START}\
## 4-10 - Numero progressivo: stesso valore omonimo campo del record 14
${num_progr}\
## Indirizzo debitore
##     11-40 - Indirizzo: via, numero civico e/o nome della frazione
##     41-45 - CAP
##     46-70 - Comune e sigla della provincia
##     71-120 - Banca/sportello domiciliataria: eventuale denominazione in chiaro della banca/sportello domiciliataria/o
${line.debtor_address | f_unidecode,f_ljust30}\
${line.debtor_zip | f_zip_code}\
${f'{line.debtor_city} {line.debtor_state}' | f_ljust25}\
${(line.debtor_bank.name or '') | f_ljust50}\
## - - - - - - - - - -
${R_END}
##
##
##
##
## ............................................................................
## .................... Record 50 .............................................
## ............................................................................
<%debug_active and print('\tR_50_START')%>\
## 1-3 - ' 50'
${R_50_START}\
## 4-10 - Numero progressivo: stesso valore omonimo campo del record 14
${num_progr}\
## Riferimenti al debito (2 segmenti da 40 caratteri)
##     11-50 + 51-90 - Riferimento al debito
##     91-100 - Filler
##     101-116 - Codifica fiscale del creditore
${riferimento_al_debito(line)}\
${BLANK_CHAR * fldsz(91, 100)}\
${doc.creditor_fiscode_or_vat | f_ljust16}\
## - - - - - - - - - -
## 117-120 - Filler
${BLANK_CHAR * fldsz(117, 120)}\
${R_END}
##
##
##
##
## ............................................................................
## .................... Record 51 .............................................
## ............................................................................
<%debug_active and print('\tR_51_START')%>\
## 1-3 - ' 51'
${R_51_START}\
## 4-10 - Numero progressivo: stesso valore omonimo campo del record 14
${num_progr}\
## 11-20 - Numero ricevuta: numero ricevuta attribuito al cliente
${(loop.index + 1) | f_number_of_receipts}\
## 11-40 - Denominazione creditore
${doc.creditor_company_name | f_ljust20}\
## Bollo virtuale -- NON IMPLEMENTATO
##     41-55 - Provincia: provincia dell'Intendenza di Finanza che ha autorizzato il pagamento del bollo in modo virtuale
##     56-65 - Numero autorizzazione: numero dell'autorizzazione dall'Intendenza di Finanza
##     66-71 - Data autorizzazione: data (nel formato GGMMAA) di concessione dell'autorizzazione da parte della Intendenza di Finanza
${BLANK_CHAR * fldsz(41, 55)}\
${BLANK_CHAR * fldsz(56, 65)}\
${BLANK_CHAR * fldsz(66, 71)}\
## - - - - - - - - - -
## 72-120 - Filler
${BLANK_CHAR * fldsz(72, 120)}\
${R_END}
##
##
##
##
## ............................................................................
## .................... Record 70 .............................................
## ............................................................................
<%debug_active and print('\tR_70_START')%>\
## 1-3 - ' 70'
${R_70_START}\
## 4-10 - Numero progressivo: stesso valore omonimo campo del record 14
${num_progr}\
## 11-88 - Filler
${BLANK_CHAR * fldsz(11, 88)}\
## 89-100 - Indicatori di circuito - NON IMPLEMENTATO
${BLANK_CHAR * fldsz(89, 100)}\
## 101-103 - Indicatore richiesta di incasso - NON IMPLEMENTATO
${BLANK_CHAR * fldsz(101, 103)}\
## 104-120 - Chiavi di controllo - NON IMPLEMENTATO
${BLANK_CHAR * fldsz(104, 120)}\
${R_END}
##
##
##
##
<%debug_active and print()%>\
% endfor
<%num_of_records = num_disposizioni * RECORDS_IN_EACH_RIBA + 2%>\
##
##
##
##
## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## ............................................................................
##                               Record EF
## ............................................................................
## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
<%debug_active and print('R_EF_START')%>\
## 1-3 - ' EF'
${R_EF_START}\
## 4-8 - UGUALE A CAMPO CORRISPONDENTE NEL RECORD ' IB' -> Mittente: codice SIA dell'azienda mittente
${doc.sia_code| f_sia}\
## 9-13 - UGUALE A CAMPO CORRISPONDENTE NEL RECORD ' IB' -> Ricevente: ABI banca assuntrice
${doc.creditor_bank_account.bank_abi | f_abi}\
## 14-19 - UGUALE A CAMPO CORRISPONDENTE NEL RECORD ' IB' -> Data creazione: data creazione del flusso da parte dell'azienda (GGMMAA)
${doc.creation_date.strftime('%d%m%y')}\
## 20-39 - UGUALE A CAMPO CORRISPONDENTE NEL RECORD ' IB' -> Nome supporto: composizione libera, ma deve essere univoco nell'ambito della data di creazione a parità di mittente e ricevente
${doc.name| f_docname}\
## 40-45 - Campo libero: a disposizione del mittente
${BLANK_CHAR * fldsz(40, 45)}\
## 46-52 - Numero disposizioni: numero di ricevute Ri.Ba. contenute nel flusso
${num_progr | f_num_of_disposizioni}\
## 53-67 - Tot. importi negativi: totale (in centesimi di Euro) delle disposizioni contenute nel flusso
${doc.total_amount | f_amount_total}\
## 68-82 - Tot. importi positivi: riempire con zeri
${'0' * fldsz(68, 82)}\
## 83-89 - Numero record: numero totale di records che compongono il flusso, nel conteggio sono compresi i record IB ed EF
${num_of_records | f_num_of_records}\
## 90-113 - Filler
${BLANK_CHAR * fldsz(90, 113)}\
## 114 - Codice divisa: assume valore fisso 'E'
${'E'}\
## 115-120 - Campo riservato (riempire con spazi)
${BLANK_CHAR * fldsz(115, 120)}\
${R_END}
