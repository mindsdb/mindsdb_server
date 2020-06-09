import requests


class Clickhouse():
    def __init__(self, config):
        self.config = config
        self.host = config['interface']['clickhouse']['host']
        self.port = config['interface']['clickhouse']['port']
        self.user = config['interface']['clickhouse']['user']
        self.password = config['interface']['clickhouse']['password']

        self.type_mapping = {
            
        }

    def _query(self, query):
        params = {'user': user}
        if password is not None:
            params['password'] = password

        response = requests.post(f'{host}:{port}', data=query, params=params)

        return response

    def sync_predictor(self, name):
        self._query(f"""
                CREATE TABLE {name}
                (rental_price String , initial_price String)
                ENGINE=MySQL('127.0.0.1:3306', 'minds', 'home_rentals', 'root', 'test1')
                    """)
