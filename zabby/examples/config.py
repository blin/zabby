import os

listen_host = '127.0.0.1'
listen_port = 10050

_config_dir = os.path.dirname(os.path.abspath(__file__))

item_files = [os.path.join(_config_dir, 'standard.py'), ]
