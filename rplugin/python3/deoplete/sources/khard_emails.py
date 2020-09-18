import re

from khard import khard, config, query
from deoplete.source.base import Base

COLON_PATTERN = re.compile(r':\s?')
COMMA_PATTERN = re.compile(r'.+,\s?')
HEADER_PATTERN = re.compile(r'^(Bcc|Cc|From|Reply-To|To):(\s?|.+,\s?)')


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'khard'
        self.mark = '[khard]'
        self.min_pattern_length = 2
        self.filetypes = ['mail']

        self.__cache = []

    def get_complete_position(self, context):
        colon = COLON_PATTERN.search(context['input'])
        comma = COMMA_PATTERN.search(context['input'])
        return max(
            colon.end() if colon is not None else -1,
            comma.end() if comma is not None else -1)

    def gather_candidates(self, context):
        if HEADER_PATTERN.search(context['input']):
            if not self.__cache:
                self.__fill_cache()
            return self.__cache

    def __fill_cache(self):
        khard_config = config.Config()
        khard_config.init_address_books()
        for vcard in khard.get_contacts(
                khard_config.abooks, query.AnyQuery(), False, False):
            for type, email_list in vcard.emails.items():
                for email in email_list:
                    self.__cache.append({'word': "{0} <{1}>".format(
                                vcard.get_first_name_last_name(), email)})
