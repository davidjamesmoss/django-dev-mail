import os
from datetime import datetime
from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django_dev_mail.parser import ParseMessage


@override_settings(EMAIL_FILE_PATH=os.path.dirname(__file__))
@override_settings(TIME_ZONE='Europe/London')
class ParserTests(TestCase):
    '''
        Overrides EMAIL_FILE_PATH and TIME_ZONE settings.
    '''

    def setUp(self):
        self.test_message_filename = 'test_email.eml'

    def test_headers(self):
        """
        Checks that expected dict of headers is retrieved and that the
        content matches the expected values.
        """

        parser = ParseMessage()
        parser.parse(self.test_message_filename, headersonly=True)
        result = parser.get_headers()

        self.assertEqual(type(result), dict)
        self.assertEqual(result['filename'], self.test_message_filename)
        self.assertEqual(result['subject'], 'Test email')
        self.assertEqual(result['from'], 'David Smith <david@example.com>')
        self.assertEqual(result['to'], 'David Smith <david@example.com>')
        self.assertEqual(result['cc'], 'Joe Smith <joe@example.com>')
        self.assertEqual(result['replyto'], 'David Smith <david@example.com>')
        self.assertEqual(result['date'], datetime(2013, 11, 24, 1, 2, 3))
        self.assertGreater(result['size'], 310000)

    def test_body_parts(self):
        """
        Checks that expected dict of mime parts is retrieved and that the
        content matches the expected values.
        """

        parser = ParseMessage()
        parser.parse(self.test_message_filename)
        result = parser.get_body()

        self.assertEqual(type(result), dict)
        self.assertEqual(len(result), 4)

        self.assertEqual(result[1]['content_type'], 'text/plain')
        self.assertEqual(result[1]['content_subtype'], 'plain')
        self.assertEqual(result[1]['charset'], 'us-ascii')

        self.assertEqual(result[2]['content_type'], 'application/pdf')
        self.assertEqual(result[2]['content_subtype'], 'pdf')
        self.assertEqual(result[2]['filename'], 'Example.pdf')

        self.assertEqual(result[3]['content_type'], 'image/jpeg')
        self.assertEqual(result[3]['content_subtype'], 'jpeg')
        self.assertEqual(result[3]['filename'], 'Image.jpg')

        self.assertEqual(result[4]['content_type'], 'application/msword')
        self.assertEqual(result[4]['content_subtype'], 'msword')
        self.assertEqual(result[4]['filename'], 'Word.doc')


@override_settings(EMAIL_FILE_PATH=os.path.dirname(__file__))
class ViewTests(TestCase):
    '''
        Overrides EMAIL_FILE_PATH setting.
    '''

    def setUp(self):
        self.test_message_filename = 'test_email.eml'

    def test_view_listing(self):
        """
        Checks that expected content is collected and shown.
        """
        response = self.client.get(reverse('view_listing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test email')
        self.assertContains(response, 'David Smith &lt;david@example.com&gt;')
        self.assertEqual(type(response.context['messages']), list)

    def test_view_message_file_not_found(self):
        """
        Checks that error message is shown when no file found.
        """
        response = self.client.get(reverse(
            'view_message',
            kwargs={'filename': 'file_that_does_not_exist'}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No headers.')
        self.assertEqual(response.context['headers'], False)

    def test_view_message(self):
        """
        Checks that expected content is collected and shown.
        """
        response = self.client.get(reverse(
            'view_message',
            kwargs={'filename': self.test_message_filename}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Plain Text')
        self.assertEqual(type(response.context['headers']), dict)
        self.assertQuerysetEqual(
            response.context['headers'],
            ["'size'", "'to'", "'replyto'", "'from'", "'date'", "'cc'",
             "'subject'", "'filename'"]
        )
        self.assertEqual(response.context['headers']['to'],
                         'David Smith <david@example.com>')

    def test_get_part(self):
        """
        Checks that expected content is collected and shown.
        """
        response = self.client.get(reverse(
            'get_part',
            kwargs={'filename': self.test_message_filename, 'part': '1'}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lorem ipsum')
        self.assertEqual(response['Content-Type'],
                         'text/plain; charset=us-ascii')

        response = self.client.get(reverse(
            'get_part',
            kwargs={'filename': self.test_message_filename, 'part': '2'}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'],
                         'inline; filename=Example.pdf')

    def test_raw_data(self):
        """
        Checks that expected content is collected and shown.
        """
        response = self.client.get(reverse(
            'raw_data',
            kwargs={'filename': self.test_message_filename}
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Message-Id: <B5870C9A-2236-4BE1-B574-ABCBCA1FC5C6@example.com>'
        )
        self.assertEqual(response['Content-Type'], 'text/plain')
