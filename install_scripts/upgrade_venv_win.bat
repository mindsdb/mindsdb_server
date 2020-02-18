
cd "%SERVER_PATH%"

env\Scripts\pip.exe install --upgrade pip
env\Scripts\pip.exe install lightwood --upgrade
env\Scripts\pip.exe install mindsdb --upgrade
env\Scripts\pip.exe install mindsdb-server --upgrade

echo from mindsdb_server import start_server > run_mindsdb_server.py
echo if __name__ == '__main__': >> run_mindsdb_server.py
echo     start_server() >> run_mindsdb_server.py
