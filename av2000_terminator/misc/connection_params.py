class ConnectionParams:

    # ATTENZIONE!!!!
    # CP437 è il codepage utilizzato dalla configurazione PuTTY fornita da Nicola Quargentan,
    # usando questo codepage i campi delle tabelle a terminale rimangono allineati anche se
    # alcuni caratteri non vengono visualizzati correttamente.
    # L'allineamento dei campi è più importante dei caratteri corretti.

    # encoding='utf-8',
    def __init__(
            self, host: str, port: int,
            username: str, password: str,
            company_id: int,
            read_delay_sec: float, encoding: str = 'CP437'
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._company_id = company_id
        self._read_delay_sec = read_delay_sec
        self._encoding = encoding
    # end __init__
    
    @property
    def host(self):
        return self._host
    # end host
    
    @property
    def port(self):
        return self._port
    # end port
    
    @property
    def username(self):
        return self._username
    # end username
    
    @property
    def password(self):
        return self._password
    # end password
    
    @property
    def company_id(self):
        return self._company_id
    # end company_id
    
    @property
    def read_delay_sec(self):
        return self._read_delay_sec
    # end read_delay_sec

    @property
    def encoding(self):
        return self._encoding
    # end encoding
    
# end ConnectionParams
