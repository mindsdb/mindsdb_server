# Mindsdb Server

[![Build Status](https://travis-ci.org/mindsdb/mindsdb_server.svg?branch=master)](https://travis-ci.org/mindsdb/mindsdb_server)

This server uses flask_restplus to define the API.


## Development installation

To install and run mindsdb_server for development, activate your virtualenv and run:

```python
python setup.py develop
pip install -r requirements.txt
cd mindsdb_server
python3 server.py
```

## The code inside mindsdb_server

 * ```namespaces/<endpoint.py>```: these contains a file per API resource 
 * ```namespaces/configs```: these are the configs for the API resources
 * ```namespaces/entitites```: these are specs for the document objects that can be returned by the API resources
 
