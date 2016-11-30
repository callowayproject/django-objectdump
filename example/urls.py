# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views.static import serve

admin.autodiscover()


urlpatterns = [
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^example/', include('example.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    ]

urlpatterns += [
    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT}),
    ] if settings.DEBUG else urlpatterns
