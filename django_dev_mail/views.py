from django.http import StreamingHttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from .parser import ParseMessage, get_directory_listing, get_file_path
from .settings import INLINE_SUBTYPES


def view_listing(request):
    '''
    Performs a directory listing of EMAIL_FILE_PATH and returns an Inbox-style
    listing of the messages found.

    Returns HTTP Response.
    '''

    messages = []
    parser = ParseMessage()
    for f in get_directory_listing():
        parser.parse(f, headersonly=True)
        messages.append(parser.get_headers())

    return render_to_response(
        'django_dev_mail/listing.html',
        {
            'messages': messages,
            'active': 'inbox'
        },
        context_instance=RequestContext(request)
    )


def view_message(request, filename=False):
    '''
    Shows the message headers and a set of links to the body parts.

    Returns HTTP Response.
    '''

    # If no filename passed, get the most recent message file.
    if not filename:
        active = 'latest'
        list = sorted(get_directory_listing(), reverse=True)
        if list:
            filename = list[0]
        else:
            filename = False

    else:
        active = 'inbox'

    parser = ParseMessage()
    parser.parse(filename)

    return render_to_response(
        'django_dev_mail/message.html',
        {
            'headers': parser.get_headers(),
            'body': parser.get_body(),
            'active': active,
            'inline_subtypes': INLINE_SUBTYPES
        },
        context_instance=RequestContext(request)
    )


def get_part(request, filename, part):
    '''
    Grab a specific MIME part with appropriate headers.
    Returns HTTP Response.
    '''

    parser = ParseMessage()
    parser.parse(filename)
    parsed_body = parser.get_body()
    part = int(part)

    charset = parsed_body[part]['charset']
    filename = parsed_body[part]['filename']
    content_type = parsed_body[part]['content_type']
    subtype = parsed_body[part]['content_subtype']

    # Fix for Safari not displaying image/jpg inline.
    if content_type == 'image/jpg':
        content_type = 'image/jpeg'

    # We ignore the Content-Disposition header in the email as we want to
    # override this.
    if subtype in INLINE_SUBTYPES:
        inline = 'inline'
    else:
        inline = 'attachment'

    if charset:
        content_type = '%s; charset=%s' % (content_type, charset)

    response = StreamingHttpResponse(
        parsed_body[part]['data'],
        mimetype=content_type
    )
    response['Content-Disposition'] = '%s; filename=%s' % (inline, filename)
    return response


def raw_data(request, filename):
    '''
    For the source view, just grabs the file contents.
    Returns HTTP Response.
    '''

    return StreamingHttpResponse(open(get_file_path(filename)),
                                 mimetype='text/plain')
