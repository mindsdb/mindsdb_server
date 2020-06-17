import os
import sys
import zipfile
import requests

assert os.name == 'nt'

PY_EMBED_URL = 'https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-amd64.zip'
GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'

if len(sys.argv) < 3:
    sys.exit('Usage: ./{} install_dir storage_dir'.format(__file__.split('.')[0]))


def make_dir(d):
    if not os.path.isdir(d):
        os.makedirs(d)


INSTALL_DIR = os.path.join(os.path.abspath(sys.argv[1]), 'mindsdb_server')
STORAGE_DIR = os.path.join(os.path.abspath(sys.argv[2]), 'mindsdb_storage')
PYTHON_DIR = os.path.join(INSTALL_DIR, 'python')

make_dir(INSTALL_DIR)
make_dir(STORAGE_DIR)
make_dir(PYTHON_DIR)

PTH_PATH = os.path.join(PYTHON_DIR, 'python37._pth')


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
with open(PTH_PATH, 'a') as f:
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

# create run_server.bat
with open(os.path.join(INSTALL_DIR, 'run_server.bat'), 'w') as f:
    cmds = ['set path={0};{0}/Scripts;{0}/Lib/site-packages'.format(PYTHON_DIR),
            'set MINDSDB_STORAGE_PATH={}'.format(STORAGE_DIR),
            'python -m mindsdb_server']
    f.write('\n'.join(cmds))
