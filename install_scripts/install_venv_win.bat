"%PYPATH%" -m pip install --user --upgrade pip
"%PYPATH%" -m pip install --user virtualenv

mkdir "%SERVER_PATH%"
cd "%SERVER_PATH%"
"%PYPATH%" -m virtualenv env

env\Scripts\pip.exe install --upgrade pip
env\Scripts\pip.exe install git+https://github.com/mindsdb/mindsdb.git@master --no-cache-dir
env\Scripts\pip.exe install mindsdb-server --no-cache-dir

echo from mindsdb_server import start_server > run_mindsdb_server.py
echo if __name__ == '__main__': >> run_mindsdb_server.py
echo     start_server() >> run_mindsdb_server.py
