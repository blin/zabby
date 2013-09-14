import imp
import os.path
import logging
import logging.config
from zabby.core.exceptions import ConfigurationError
from zabby.core.six import string_types, integer_types

LOG = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self, config_path, config_loader):
        self._config_path = config_path
        self._config_loader = config_loader

        self._config = None
        self.listen_address = (None, None)
        self.items = dict()

    def update_config(self):
        """
        Reloads configuration from config_path binding

        :raises: ConfigurationError if configuration files are not valid python
        modules or if required module attributes are of wrong type
        """
        try:
            self._config = self._config_loader.load(self._config_path)
            logging.config.fileConfig(self._config.logging_conf,
                                      disable_existing_loggers=False)
            self._set_listen_address()
            self._load_items()
        except ConfigurationError as e:
            raise e
        except Exception as e:
            LOG.exception(e)
            raise ConfigurationError()

    def _set_listen_address(self):
        self._check_type(self._config.listen_host, string_types)
        self._check_type(self._config.listen_port, integer_types)
        self.listen_address = (self._config.listen_host,
                               self._config.listen_port)

    def _check_type(self, var, desired_type):
        """ Raises ConfigurationError if var is not of desired_type """
        if not isinstance(var, desired_type):
            raise ConfigurationError("{var} should be {type}".format(
                var=var, type=desired_type))

    def _load_items(self):
        items = dict()
        for item_file in self._config.item_files:
            LOG.debug("Loading items from {0}".format(item_file))
            item_module = self._config_loader.load(item_file)
            self._check_type(item_module.items, dict)
            items.update(item_module.items)

        self.items = items


class ModuleLoader():
    def load(self, module_path):
        """
        Returns module contained in module_path

        :raises: IOError if unable to access module_path
        :raises: SyntaxError, NameError, TypeError, ValueError
            if module contains invalid python code
        """
        try:
            module_name = os.path.split(module_path)[-1].split('.')[0]
            return imp.load_source(module_name, module_path)
        except (IOError, SyntaxError) as e:
            LOG.error("Unable to load {0}".format(module_path))
            raise e
