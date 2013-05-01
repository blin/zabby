import os

listen_host = '127.0.0.1'
listen_port = 10050

_config_dir = os.path.dirname(os.path.abspath(__file__))

_item_dir = os.path.join(_config_dir, 'items')
item_files = sorted([os.path.join(_item_dir, item_file)
                     for item_file in os.listdir(_item_dir)
                     if item_file.endswith('.py')])

logging_conf = os.path.join(_config_dir, 'logging.conf')
