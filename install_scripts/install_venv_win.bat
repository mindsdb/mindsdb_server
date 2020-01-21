"%PYPATH%" -m pip install --user --upgrade pip
"%PYPATH%" -m pip install --user virtualenv

mkdir "%SERVER_PATH%"
cd "%SERVER_PATH%"
"%PYPATH%" -m virtualenv env

env\Scripts\pip.exe install --upgrade pip
env\Scripts\pip.exe install git+https://github.com/mindsdb/mindsdb.git@master
env\Scripts\pip.exe install torch===1.4.0 torchvision===0.5.0 -f https://download.pytorch.org/whl/torch_stable.html 
env\Scripts\pip.exe install mindsdb-server --no-cache-dir

echo from mindsdb_server import start_server > run_mindsdb_server.py
echo if __name__ == '__main__': >> run_mindsdb_server.py
echo     start_server() >> run_mindsdb_server.py
