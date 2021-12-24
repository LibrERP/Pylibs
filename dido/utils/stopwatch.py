import datetime


class Stopwatch:

    def __init__(self, start_now: bool = False):
        """

        :param start_now: boolean, immediatly start the stopwatch.
        """

        self._start_dt = None

        self._record_dt = None
        self._record_delta = None

        if start_now:
            self.start_timer()
        # end if
    # end __init__

    def start_timer(self):
        if self._start_dt is not None:
            raise RuntimeError('Stopwatch already started')
        # end if

        self._start_dt = datetime.datetime.now()
    # end start

    def record_time(self):
        """Record a new timestamp overriding the previous one.

        :returns (datetime.datetime, datetime.timedelta)
            Start datetime and the elapsed time of the last record
        """
        if self._start_dt is None:
            raise RuntimeError('Stopwatch NOT started')
        # end if

        self._record_dt = datetime.datetime.now()
        self._record_delta = self._record_dt - self._start_dt

        return self.last_record
    # end record

    @property
    def start(self):
        return self._start_dt
    # end last_record

    @property
    def last_record(self):
        """Returns the start datetime and the elapsed time of the last record
        returns: (datetime.datetime, datetime.timedelta)
        """
        if self._start_dt is None:
            raise RuntimeError('Stopwatch NOT started')
        # end if

        if self._record_dt is None:
            raise RuntimeError('No record created')
        # end if

        return self._record_dt, self._record_delta
    # end last_record

    @property
    def from_start(self):
        """Returns time elapsed from the call of method start

        :returns  datetime.timedelta
        """
        if self._start_dt is None:
            raise RuntimeError('Stopwatch NOT started')
        # end if

        now = datetime.datetime.now()
        elapsed = now - self._start_dt
        return now, elapsed
    # end from_start

    @property
    def from_record(self):
        """Returns time elapsed from the last call of record_time,
        if no record has been created returns the time from the start time.

        :returns  datetime.timedelta
        """
        if self._start_dt is None:
            raise RuntimeError('Stopwatch NOT started')
        # end if

        now = datetime.datetime.now()
        elapsed = now - self._start_dt
        return now, elapsed
    # end from_start


# end Stopwatch
