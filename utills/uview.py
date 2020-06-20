# -*- coding: utf-8 -*-
import logging
import sys
from jinja2 import (Environment,
                    FileSystemLoader)
from jinja2 import exceptions as exp

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class ViewUtills:
    def __init__(self, dir_temp, file_template):
        self.dir_template = FileSystemLoader(dir_temp)
        self.file_template = file_template
    def view_unpackage(self, data_unpackage, additonal_dict=None):
        """This if render a templates
        TODO: We can delete it because the view component enough to direcly using jinja2
        """

        try:
            env = Environment(loader=self.dir_template)
            template = env.get_template(self.file_template)

            if additonal_dict is None:
                output = template.render(row=data_unpackage)
                return output
            else:
                output = template.render(row=data_unpackage,
                                         dict_row=additonal_dict)
                return output

            logger.info('File template: %s', template)

        except exp.TemplateNotFound as e:
            logger.error('\n\nFile Not Found:\n%s\n', e)
            return None

        except exp.TemplateSyntaxError as e:
            logger.error('\n\nSyntax ERROR template file:\n%s\n ', e)
            return None