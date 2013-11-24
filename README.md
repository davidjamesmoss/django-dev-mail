#Django-Dev-Mail

A simple django mail app for use in development.

An alternative to sending test emails through your email server or using custom email servers and desktop clients such as MockSMTP.

![Screengrab](https://raw.github.com/davidjamesmoss/django-dev-mail/master/screengrab.png)

##Features
- Displays multipart messages (HTML, plain text and attachments, plus the raw source) in a lazy-loading tabbed interface.
- PDF, PNG, JPG, TIFF and GIF files are displayed inline. Other attachments are presented for download.
- Mimetypes to display inline are configurable in settings.
- Handles referenced attachments in IMG tags (cid:).
- Latest message view to save returning to the inbox list when testing.

##Designed to not get in the way of your other apps
- Uses files only - Does not pollute your database.
- Independent from the Django admin interface.
- Does not use sessions, messages or auth.
- No static content.
- Stores emails in your media folder (or anywhere you choose) for easy removal.

##More things
- Uses the standard Django email-to-file backend.
- Uses the standard Python email parsing libraries.
- Simple responsive Bootstrap 3 interface, loaded from CDN.
- Basic tests for each view and the parser.


##Requirements
- Django 1.5
- BeautifulSoup
- Some emails to send

##Installation
1. Install:

        pip install git+https://github.com/davidjamesmoss/django-dev-mail.git

2. In your settings/dev.py (or equivalent), specify the standard Django email-to-file backend and a location.

        EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
        EMAIL_FILE_PATH = MEDIA_ROOT + '/dev_email'

3. Add to your installed apps:

        INSTALLED_APPS = (
            ...
            'django_dev_mail',
        )

4. And add to your urls.py when DEBUG is True:

        if settings.DEBUG:
            urlpatterns += patterns('',
                ...
                url(r'^devmail/', include('django_dev_mail.urls')),
            )

5. Just runserver and go to http://localhost:8000/devmail/ (or your equivalent).


##Settings
Optionally set the mimetypes that are shown inline. Only the subpart is required.

    DEV_MAIL_INLINE_SUBTYPES = ['plain', 'html', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'tiff']


##Handling of multipart/mixed messages
Since this is designed to the types of messages sent by Django apps, I haven’t gone so far as to support multipart/mixed fully.
Inline images are handled, but if the HTML is split across multiple parts, they will be shown separately.

##ToDo
- Add to PyPi.


##Notes
- This app is intended for dev use only. Don’t enable it on a live deployment. There is no password protection and it exposes the filesystem.
- Intended for checking the nice clean emails you would send from your apps - this is not going to handle every quirk a regular mail client would.
- Contributions and bug reports welcome.
