from django.conf import settings

default_inline_subtypes = ['plain', 'html', 'pdf', 'png', 'jpg', 'jpeg', 'gif',
                           'tiff']

INLINE_SUBTYPES = getattr(settings, 'DEV_MAIL_INLINE_SUBTYPES',
                          default_inline_subtypes)
