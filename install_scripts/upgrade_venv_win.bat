
cd "%SERVER_PATH%"

env\Scripts\pip.exe install --upgrade pip
env\Scripts\pip.exe install mindsdb --upgrade

echo import runpy > run_mindsdb_server.py
echo import torch.multiprocessing as mp >> run_mindsdb_server.py
echo if __name__ == '__main__': >> run_mindsdb_server.py
echo.    mp.freeze_support() >> run_mindsdb_server.py
echo.    runpy.run_module('mindsdb',run_name='__main__') >> run_mindsdb_server.py
