import json

def _in(ask,default):
    user_input = input(f'{ask} (Default: {default})')
    if user_input is None or user_input == '':
        user_input = default
    return user_input

def auto_config(python_path,pip_path,predictor_dir,datasource_dir):
    config = {
        "debug": False
        ,"config_version": 1
        ,"python_interpreter": python_path
        ,"pip_path": pip_path
        ,"api": {
        }
        ,"interface":{
          "clickhouse": {
              "enabled": False
          }
          ,"mindsdb_native": {
              "enabled": True
              ,"storage_dir": predictor_dir
          }
          ,"lightwood": {
               "enabled": True
          }
          ,"datastore": {
               "enabled": True
               ,"storage_dir": datasource_dir
          }
          ,"dataskillet": {
               "enabled": False
          }
        }
    }

def cli_config(python_path,pip_path,predictor_dir,datasource_dir,config_dir):
    config = auto_config(python_path,pip_path,predictor_dir,datasource_dir)

    http = _in('Enable HTTP API ? [Y/N]','Y')
    if http in ['Y','y']:
        config['api']['http'] = {}
        config['api']['http']['host'] = _in('HTTP interface host: ','0.0.0.0')
        config['api']['http']['port'] = _in('HTTP interface port: ','47334')

    mysql = _in('Enable MYSQL API ? [Y/N]','Y')
    if mysql in ['Y','y']:
        config['api']['mysql'] = {}
        config['api']['mysql']['host'] = _in('MYSQL interface host','127.0.0.1')
        config['api']['mysql']['port'] = _in('MYSQL interface port','3306')
        config['api']['mysql']['user'] = _in('MYSQL interface user','mindsdb')
        config['api']['mysql']['password'] = _in('MYSQL interface password','')

    clickhouse = _in('Connect to clickhouse ? [Y/N]','N')
    if clickhouse in ['Y','y']:
        config['interface']['clickhouse']['enabled'] = True
        config['interface']['clickhouse']['host'] = _in('Clickhouse host: ','localhost')
        config['interface']['clickhouse']['port'] = _in('Clickhouse port: ','8123')
        config['interface']['clickhouse']['user'] = _in('Clickhouse user: ','default')
        config['interface']['clickhouse']['password'] = _in('Clickhouse password: ','')

    config_path = os.path.join(config_dir,'config.json')
    with oepn(config_path, 'w') as fp:
        json.dump(config, fp)

    return config_path


def daemon_creator(python_path,config_path):
    service_txt = f"""
    [Unit]
    Description=Mindsdb

    [Service]
    WorkingDirectory=/home/ubuntu/mindsdb_server
    ExecStart={python_path} -m mindsdb_server --config={config_path}

    [Install]
    WantedBy=multi-user.target
    """.strip(' ')

    try:
        with open('/etc/systemd/system/mindsdb.service', 'w') as fp:
            fp.write(service_txt)
    except Exception as e:
        print(f'Failed to create daemon, error: {e}')

    try:
        os.ystem('systemctl daemon-reload')
    except Exception as e:
        print(f'Failed to load daemon, error: {e}')
