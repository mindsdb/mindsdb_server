
cd "%SERVER_PATH%"

env\Scripts\pip.exe install --upgrade pip
env\Scripts\pip.exe install mindsdb --upgrade

echo import runpy > run_mindsdb_server.py
echo runpy.run_module('mindsdb') >> run_mindsdb_server.py
