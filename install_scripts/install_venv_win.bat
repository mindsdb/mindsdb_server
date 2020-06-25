"%PYPATH%" -m pip install wheel --no-binary :all:
"%PYPATH%" -m pip install --user --upgrade pip
"%PYPATH%" -m pip install --user virtualenv

mkdir "%SERVER_PATH%"
cd "%SERVER_PATH%"
"%PYPATH%" -m virtualenv env

env\Scripts\pip.exe install --upgrade pip
env\Scripts\pip.exe install mindsdb --no-cache-dir

echo import runpy > run_mindsdb_server.py
echo runpy.run_module('mindsdb') >> run_mindsdb_server.py
