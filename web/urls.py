"""
This is the starting point when a user enters a url in their web browser.

The urls is matched (by regex) and mapped to a 'view' - a Python function or
callable class that in turn (usually) makes use of a 'template' (a html file
with slots that can be replaced by dynamic content) in order to render a HTML
page to show the user.

This file includes the urls in website, webclient and admin. To override you
should modify urls.py in those sub directories.

Search the Django documentation for "URL dispatcher" for more help.

"""

from django.urls import include, path
from django.shortcuts import redirect

# default evennia patterns
from evennia.web.urls import urlpatterns as evennia_default_urlpatterns

def redirect_to_wiki(request):
    return redirect('wiki:page_list')

# add patterns
urlpatterns = [
    # Add this at the top of your urlpatterns
    path('', redirect_to_wiki, name='index'),
    # website
    path("", include("web.website.urls")),
    # webclient
    path("webclient/", include("web.webclient.urls")),
    # web admin
    path("admin/", include("web.admin.urls")),
    # add any extra urls here:
    # path("mypath/", include("path.to.my.urls.file")),
    path('wiki/', include('wiki.urls', namespace='wiki')),
]

# 'urlpatterns' must be named such for Django to find it.
urlpatterns = urlpatterns + evennia_default_urlpatterns
