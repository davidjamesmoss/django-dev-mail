from django.conf.urls.defaults import *
from .views import view_listing, view_message, get_part, raw_data


urlpatterns = patterns('',
    url(
        r'^$',
        view_listing,
        name='view_listing'
    ),
    url(
        r'^file/(?P<filename>.*)/(?P<part>\d+)/$',
        get_part,
        name='get_part'
    ),
    url(
        r'^file/(?P<filename>.*)/raw/$',
        raw_data,
        name='raw_data'
    ),
    url(
        r'^latest/$',
        view_message,
        name='latest_message'
    ),
    url(
        r'^(?P<filename>.*)/$',
        view_message,
        name='view_message'
    ),

)
