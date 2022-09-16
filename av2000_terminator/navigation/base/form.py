import abc
import dataclasses
import logging
import time

from frozendict import frozendict
import heapq
import json
import numpy as np
from pathlib import Path
import typing

from future.moves import collections

from av2000_terminator.terminal import AV2000Terminal
from sshterminal import keys

from . page import AbstractPage


class FormModifiedFlag:

    def __init__(self):
        self._form_modified: bool = False
    # end_if

    @property
    def modified(self):
        return self._form_modified
    # end modified

    def signal_modified(self):
        self._form_modified = True
    # end signal_modified
# FormModifiedFlag


@dataclasses.dataclass
class FieldDescriptor:

    line: int
    start: int
    label: str
    size: int
    writable: bool = True
    screen: str = 'main'

    class JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, FieldDescriptor):
                return obj.as_dict
            else:
                return json.JSONEncoder.default(self, obj)
            # end if
        # end default
    # end FieldJSONEncoder

    @property
    def end(self):
        return self.start + self.size - 1
    # end end

    @property
    def as_dict(self):
        dct = dataclasses.asdict(self)
        dct['__class__'] = self.__class__.__name__
        return dct
    # end as_dict

    @staticmethod
    def json_decoder(dct: dict):
        if dct.get('__class__', '') == Field.__name__:
            del dct['__class__']
            return FieldDescriptor(**dct)
        else:
            return dct
        # end if
    # end if
# end FieldDescriptor


class Field:

    # - - - - - - - - - - - - - - - - -
    # Eccezioni
    class FieldException(Exception):
        pass
    # end NotReachableException

    class NotReachableException(FieldException):
        pass
    # end NotReachableException

    class LineNotReachableException(NotReachableException):
        pass
    # end LineNotReachableException

    class ColNotReachableException(NotReachableException):
        pass
    # end ColNotReachableException

    class ReadOnlyFieldException(FieldException):
        pass
    # end ReadOnlyFieldException

    class FieldValueError(FieldException):
        pass
    # end FieldValueError

    # - - - - - - - - - - - - - - - - -
    # Metodi
    def __init__(
            self,
            descriptor: FieldDescriptor,
            av2000: AV2000Terminal,
            form_modified_flag: FormModifiedFlag,
    ):

        cls = self.__class__
        self._logger = logging.getLogger(f'{cls.__module__}.{cls.__qualname__}')

        self._descriptor = descriptor
        self._av2000 = av2000
        self._form_modified_flag = form_modified_flag
        self._buffer = None
    # end __init__

    def _require_writable(method):

        def check_writable(self, *args, **kwargs):
            if not self.writable:
                raise self.ReadOnlyFieldException(self.label)
            # end if

            method(self, *args, **kwargs)
        # end check_writable

        return check_writable
    # end require_writable

    @property
    def flush_required(self):
        return self._buffer is not None
    # end commit_required

    @_require_writable
    def flush(self) -> None:
        if self._buffer is not None:

            self._logger.info(f'Flushing filed {self.label} >>>>{self._buffer}<<<<')

            # 1 - Move cursor
            self.move_cursor_here()
            # 2 - Clear field
            self.clear_field()
            # 3 - Write data
            self._av2000.cursor.write(self._buffer)  # TODO: CONTROLLARE METODO WRITE, per qualche motivo NON SCRIVE
            # 4 - Clear local buffer
            self._buffer = None
        # end if
    # end write

    @_require_writable
    def clear_field(self) -> None:
        self.move_cursor_here()
        self._av2000.cursor.write(keys.DELETE * self.size)
    # end clear_field

    @_require_writable
    def move_cursor_here(self):

        def move_cursor(
                move_while: typing.Callable[[], bool],
                move_method: typing.Callable[[], None],
                get_pos: typing.Callable[[], int]
        ):
            """
            Actually move the cursor, throw an exception if after
            calling the "move_method" the cursor has not changed
            it's position.
            """

            while move_while():
                max_updates = 50

                pos = get_pos()

                move_method()

                # The following while loop is here to ensure the terminal
                # emulator has been updated before checking for cursor
                # position
                while pos == get_pos() and max_updates > 0:
                    max_updates -= 1
                    self._av2000.send_seq('')
                    time.sleep(0.1)
                # end if

                if pos == get_pos():
                    self._av2000.print_screen()
                    error_msg = self._av2000.display_lines[-3].replace('q', '').strip()
                    raise self.FieldValueError(f'Field "{self.label}": {error_msg}')
                # end if
            # end while
        # end move

        def to_line():

            if crs.position.line == self.line:
                pass
            elif crs.position.line > self.line:
                move_cursor(
                    move_while=lambda: crs.position.line > self.line,
                    move_method=crs.up,
                    get_pos=lambda: crs.position.line
                )
            else:
                move_cursor(
                    move_while=lambda: crs.position.line < self.line,
                    move_method=crs.down,
                    get_pos=lambda: crs.position.line
                )
            # end if

            # Ensure cursor is at the desired line
            if crs.position.line != self.line:
                raise self.LineNotReachableException(
                    f'Was targeting line {self.line}, reached line {crs.position.line}'
                )
            # end if
        # end to_line

        def to_col():

            if crs.position.col == self.start:
                pass
            elif crs.position.col > self.start:
                move_cursor(
                    move_while=lambda: crs.position.col > self.start,
                    move_method=crs.tab_back,
                    get_pos=lambda: crs.position.col
                )
            else:
                move_cursor(
                    move_while=lambda: crs.position.col < self.start,
                    move_method=crs.tab_fwd,
                    get_pos=lambda: crs.position.col
                )
            # end if

            # Ensure cursor is at the desired line
            if crs.position.col != self.start:
                raise self.ColNotReachableException(
                    f'Was targeting column {self.start}, reached column {crs.position.col}'
                )
            # end if
        # end to_col

        # Main function code
        crs = self._av2000.cursor
        to_line()
        to_col()
    # end move_cursor_here

    @property
    def is_cursor_here(self) -> bool:
        crs = self._av2000.cursor
        return (
            crs.position.line == self. line
            and
            self.start <= crs.position.col <= self.start + self.end
        )
    # end is_cursor_here

    @property
    def is_cursor_at_start(self) -> bool:
        crs = self._av2000.cursor
        return (
            crs.position.line == self. line
            and
            crs.position.col == self.start
        )
    # end is_cursor_at_start

    @property
    def data_raw(self) -> str:
        return self._get_data(raw=True)
    # end data

    @property
    def data(self) -> typing.Union[str, None]:
        return self._get_data(raw=False)
    # end data

    @data.setter
    @_require_writable
    def data(self, value: str):
        self._buffer = str(value)
        self._form_modified_flag.signal_modified()
    # end data.setter

    @property
    def descriptor(self) -> FieldDescriptor:
        return self._descriptor
    # end descriptor

    @property
    def label(self) -> str:
        return self._descriptor.label
    # end label

    @property
    def line(self) -> int:
        return self._descriptor.line
    # end label

    @property
    def start(self) -> int:
        return self._descriptor.start
    # end label

    @property
    def size(self) -> int:
        return self._descriptor.size
    # end label

    @property
    def end(self) -> int:
        return self._descriptor.end
    # end label

    @property
    def writable(self):
        return self._descriptor.writable
    # end writable

    def _get_data(self, raw: bool) -> str:
        my_line = self._av2000.display_lines[self.descriptor.line]
        raw_data = my_line[self.descriptor.start:self.descriptor.end + 1]

        return raw and raw_data or raw_data.strip()
    # end if

    def __str__(self) -> str:
        return self._descriptor.__str__().replace(
            FieldDescriptor.__name__, self.__class__.__name__
        )
    # end def

    def __repr__(self) -> str:
        return self._descriptor.__repr__().replace(
            FieldDescriptor.__name__, self.__class__.__name__
        )
    # end def
# end Field


class AbstractForm(AbstractPage, abc.ABC):

    class FormError(Exception):
        pass
    # end FormError

    DATA_FILE_PATH = None

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._form_modified_flag: FormModifiedFlag = FormModifiedFlag()

        if self.DATA_FILE_PATH:
            self._my_fields = None
            self._fields_from_json()
        else:
            self._my_fields: typing.List[Field] = list()
        # end if
    # end __init__

    @property
    def modified(self) -> bool:
        return self._form_modified_flag.modified
    # end if

    @property
    def data(self) -> dict:
        return self.fields_values_collector(self._my_fields)
    # end

    @property
    def fields(self):
        return self._my_fields
    # end fields

    @property
    def fields_list(self) -> typing.List[Field]:
        return self.fields_collector(self._my_fields)
    # end

    @property
    def auto_fields_matrix(self) -> np.array:
        """
        Ritorna una matrice con le stesse dimensioni del terminale (righe e colonne) contenente
        in ogni cella il valore:
          - False se la cella è una cella ordinaria (testo o sfondo)
          - True se la cella è parte di un campo (porzione dello schermo per inserimento dati)
        """

        # 2 - Analisi matrice per creazione di una lista di campi. Il risultato dell'analisi è
        #     una lista di namedtuple di tipo FieldDescriptor
        fields_matrix = np.zeros(self._av2000.actual_size, np.bool)

        for row_key, row_data in sorted(self._av2000.terminal_buffer.items(), key=lambda x: x[0]):

            for col_key, col_data in sorted(row_data.items(), key=lambda x: x[0]):
                row_idx = int(row_key)
                col_idx = int(col_key)
                char = col_data

                fields_matrix[row_idx][col_idx] = char.reverse and True or False

                # end for
        # end for

        return fields_matrix
    # end fields_matrix

    @property
    def auto_fields_list(self) -> typing.List[FieldDescriptor]:
        """
        Analisi matrice per creazione di una lista di campi. Il risultato
        dell'analisi è una lista di namedtuple di tipo FieldDescriptor
        """
        fields_list = list()

        for line_idx, current_line in enumerate(self.auto_fields_matrix):

            label_start = 0
            current_field = None

            for char_idx, is_field in enumerate(current_line):

                is_last_char = char_idx == len(current_line) - 1

                if is_field:

                    # Se mi trovo su una posizione che appartiene ad un campo
                    # e non ho un oggetto Field attivo ne creo uno, lo assegno
                    # alla variabile current_field e lo aggiungo alla lista
                    # dei campi trovati
                    if current_field is None:
                        label = self._av2000.display_lines[line_idx][label_start:char_idx].strip()

                        current_field = FieldDescriptor(
                            line=line_idx,
                            start=char_idx,
                            label=label,
                            size=0,
                        )

                        fields_list.append(current_field)
                    # end if

                    # Se mi trovo sull'ultima posizione della righa chiudo
                    # l'oggetto Field attivo
                    if is_last_char:
                        assert current_field

                        current_field.size = char_idx - current_field.start + 1
                        fields_list.append(current_field)
                        current_field = None
                    # end if

                else:

                    # Se mi trovo su una posizione che NON appartiene ad un campo
                    # chiudo l'eventuale oggetto Field attivo assegnando la
                    # lunghezza e azzero la variabile current_field
                    if current_field is not None:
                        current_field.size = char_idx - current_field.start
                        current_field = None
                        label_start = char_idx
                    # end if
                # end if
            # end for
        # end for

        return fields_list
    # end fields_list

    @property
    def auto_fields_dict(self) -> typing.Dict[str, FieldDescriptor]:

        counters = collections.defaultdict(int)
        fields_dict = dict()

        for fld in self.auto_fields_list:

            normalized_key = fld.label.replace(' ', '_').lower()

            if normalized_key in counters:
                suffix = counters[normalized_key]
                dict_key = f'{normalized_key}_{suffix:02d}'
            else:
                dict_key = normalized_key
            # end if

            counters[normalized_key] += 1
            fields_dict[dict_key] = fld
        # end for

        return fields_dict
    # end auto_fields_dict

    def auto_fields_export(self, dst: typing.Union[str, Path], layout: str = 'dict') -> None:
        dst_path = Path(dst)

        with dst_path.open('w') as dst_file:
            if layout == 'dict':
                json.dump(self.auto_fields_dict, dst_file, indent=2, cls=FieldDescriptor.JSONEncoder)
            elif layout == 'list':
                json.dump(self.auto_fields_list, dst_file, indent=2, cls=FieldDescriptor.JSONEncoder)
            else:
                assert False, 'Invalid layout specified'
            # end if
        # end with
    # end fields_dict

    def _fields_from_json(self) -> None:

        def field_factory(dct: dict):
            if dct.get('__class__', '') == FieldDescriptor.__name__:
                del dct['__class__']
                return Field(
                    descriptor=FieldDescriptor(**dct),
                    av2000=self._av2000,
                    form_modified_flag=self._form_modified_flag
                )
            else:
                return dct
            # end if
        # end field_factory

        def freeze_data(data):
            if isinstance(data, dict):
                return frozendict({
                    k: freeze_data(v) for k, v in data.items()
                })
            elif isinstance(data, list):
                return tuple([freeze_data(i) for i in data])
            else:
                return data
            # end if
        # end freeze_data

        # Read data from JSON file
        with open(self.DATA_FILE_PATH, 'r') as json_file:
            loaded_data = json.load(json_file, object_hook=field_factory)
        # end with

        # Freeze the data structures
        frozen_data = freeze_data(loaded_data)

        # Set the _my_fields variable
        self._my_fields = frozen_data
    # end load_json

    def flush(self):
        # Write changes on the screen
        for field in self.fields_list:
            if field.flush_required:
                self._logger.debug(f'Flushing field {field.label}')
                field.flush()
            # end if
        # end for
    # end write

    def commit_changes(self):
        self.flush()
        self._save_and_back()
    # end commit

    @classmethod
    def fields_values_collector(cls, obj: typing.Union[dict, list, Field]) -> typing.Union[dict, list, str]:

        if isinstance(obj, frozendict):
            return {
                k: cls.fields_values_collector(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, tuple):
            result = [
                cls.fields_values_collector(i)
                for i in obj
            ]
            return any(result) and result or list()
        elif isinstance(obj, Field):
            return obj.data
        else:
            assert False
        # end if
    # end fields_values_collector

    @classmethod
    def fields_collector(cls, obj) -> typing.List[Field]:
        """
        obj: a frozendict of Field objects, a tuple of Field objects or a single Field object
        :returns list of Fields objects for this Form. Fields are sorted by (line, start_column) ascending
        """

        if isinstance(obj, frozendict):
            res = [
                cls.fields_collector(v)
                for v in obj.values()
            ]
            sorted_list = list(heapq.merge(*res, key=lambda fld: (fld.line, fld.start)))
        elif isinstance(obj, tuple):
            res = [
                cls.fields_collector(i)
                for i in obj
            ]
            sorted_list = list(heapq.merge(*res, key=lambda fld: (fld.line, fld.start)))
        elif isinstance(obj, Field):
            sorted_list = [obj]
        else:
            assert False, f'fields_collector found an unmanaged type: {type(obj)} --> {str(obj)}'
        # end if

        return sorted_list
    # end walk

    def _save_and_back(self):
        """Save data on the screen to the disk"""
        self._av2000.send_seq(self._av2000.RETURN_CHAR)
    # end commit
# end Form
