import os
import sys
import zipfile
import requests

assert os.name == 'nt'

PY_EMBED_URL = 'https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-amd64.zip'
GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'
PATH_FILENAME = 'python37._pth'
PYTHON_DIR = os.path.abspath('./python')


def download_file(url, dst='./'):
    filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(dst, filename), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return filename


# download & unzip python
python_zip_filename = download_file(PY_EMBED_URL)
with zipfile.ZipFile(python_zip_filename, 'r') as z:
    z.extractall(PYTHON_DIR)

# remove python.zip
os.remove(python_zip_filename)

# add "Lib\site-packages" to pythonXX._pth 
with open(os.path.join(PYTHON_DIR, PATH_FILENAME), 'a') as f:
    f.write('\nLib\site-packages')

# download get-pip.py
get_pip_filename = download_file(GET_PIP_URL)
get_pip_path = os.path.abspath(get_pip_filename)

# setup environment (pip & mindsdb_server & mindsdb_native)
try:
    os.system('setupenv.bat {} {}'.format(PYTHON_DIR, get_pip_path))
except Exception as e:
    sys.exit(e)

# remove get-pip.py
os.remove(get_pip_filename)

# TODO: other dependencies (pytorch, cuda)
