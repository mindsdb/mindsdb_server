set path=%1;%1/Scripts;%1/Lib/site-packages
python %2
pip install mindsdb_server
pip install mindsdb