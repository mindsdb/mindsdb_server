set path=%1;%1/Scripts;%1/Lib/site-packages
python %2
pip install mindsdb_server
pip install torch==1.5.0+cpu torchvision==0.6.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install mindsdb