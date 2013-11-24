from datetime import datetime
from os import path, listdir
from django.conf import settings
from BeautifulSoup import BeautifulSoup
from email.parser import Parser
from email.utils import parsedate_tz, mktime_tz


def get_directory_listing():
    if path.exists(settings.EMAIL_FILE_PATH):
        return listdir(settings.EMAIL_FILE_PATH)
    else:
        return []


def get_file_path(filename):
    filepath = path.join(settings.EMAIL_FILE_PATH, filename)
    if path.exists(filepath):
        return filepath
    else:
        return False


class ParseMessage():
    '''
    Wrapper around standard Python email parser.
    '''

    parsed_message = False
    filename = False
    filesize = False

    def parse(self, filename, headersonly=False):
        '''
        Gets the file path, gather data and provides an initial parse of the
        message.
        '''

        filepath = get_file_path(filename)
        if filepath:
            self.filesize = path.getsize(filepath)
            self.filename = filename
            self.parsed_message = Parser().parse(open(filepath),
                                                 headersonly=headersonly)

    def get_headers(self):
        '''
        Gathers the headers and other data into a dict.
        Parses the date with timezone.

        Returns a dict or False.
        '''
        if self.parsed_message:
            date = parsedate_tz(self.parsed_message.get('Date'))
            date = datetime.fromtimestamp(mktime_tz(date))

            return {
                'filename': self.filename,
                'subject': self.parsed_message.get('Subject'),
                'from': self.parsed_message.get('From'),
                'to': self.parsed_message.get('To'),
                'cc': self.parsed_message.get('Cc'),
                'replyto': self.parsed_message.get('Reply-To'),
                'date': date,
                'size': self.filesize
            }
        else:
            return False

    def get_body(self):
        '''
        Walks the mime parts and builds a multi-level dict.
        Dict keys are used to reference the parts in URLs.
        Handles rewriting IMG tags if inline attachments are used.

        We have to parse each part in order to provide the inline
        attachment support.

        Returns a dict or False.
        '''

        # This keeps track of parts with a Content-Id header.
        # Format: parts_with_cid[Content-Id value] = part_id
        parts_with_cid = {}

        if self.parsed_message:
            # Each mime part will go into a integer-keyed dict.
            body = {}
            i = 1

            for mimepart in self.parsed_message.walk():
                if not mimepart.get_content_type().startswith('multipart'):
                    parsed_part = {
                        'content_type': mimepart.get_content_type(),
                        'content_subtype': mimepart.get_content_subtype(),
                        # content_id for inline embedded images.
                        'content_id': mimepart.get('Content-Id'),
                        # Attachment filename
                        'filename': mimepart.get_filename(),
                        # decode=true handles base64 and quoted-printable.
                        'data': mimepart.get_payload(decode=True),
                        # charset is passed in HTTP headers when viewing parts.
                        'charset': mimepart.get_content_charset()
                    }

                    # If there was a content_id, we collect them into a dict
                    # for lookup by _embedded_images
                    if parsed_part['content_id']:
                        parts_with_cid[parsed_part['content_id']] = i

                    body[i] = parsed_part
                    i = i + 1

            # Now that we have all of the parts, we can look for embedded
            # attachments.
            if len(parts_with_cid):
                for k, v in body.iteritems():
                    if v['content_subtype'] == 'html':
                        v['data'] = self._embedded_images(v['data'],
                                                          parts_with_cid)

            return body

        else:
            return False

    def _embedded_images(self, html, parts_with_cid):
        '''
        Only called on HTML parts.
        Rewrites IMG tags to load the appropriate part URL.

        Returns string.
        '''
        soup = BeautifulSoup(html)
        for img in soup.findAll('img'):
            if img['src'].startswith('cid:'):
                id = '<%s>' % img['src'][4:]
                url = '../%d/' % parts_with_cid[id]
                img['src'] = url
        return str(soup)
