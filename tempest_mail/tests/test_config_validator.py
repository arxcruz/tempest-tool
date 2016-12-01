import os
import unittest

from tempest_mail import tests

from tempest_mail.cmd.config_validator import ConfigValidator
from yaml.parser import ParserError
from voluptuous import MultipleInvalid


class TestConfigValidator(unittest.TestCase):

    def setUp(self):
        super(TestConfigValidator, self).setUp()

    def test_good_config_file(self):
        config = os.path.join(os.path.dirname(tests.__file__),
                              'config_validate', 'good.yaml')
        validator = ConfigValidator(config)
        validator.validate()

    def test_bad_config_file(self):
        config = os.path.join(os.path.dirname(tests.__file__),
                              'config_validate', 'bad.yaml')
        validator = ConfigValidator(config)
        self.assertRaises(ParserError, validator.validate)

    def test_ugly_config_file(self):
        config = os.path.join(os.path.dirname(tests.__file__),
                              'config_validate', 'ugly.yaml')
        validator = ConfigValidator(config)
        self.assertRaises(MultipleInvalid, validator.validate)
