# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic.list_detail import object_list, object_detail

from .models import SimpleModel


urlpatterns = [
    url(r'^$', object_list, {'queryset': SimpleModel.objects.all()},
        name="simplemodel_list"),
    url(r'^(?P<slug>[\w-]+)/', object_detail,
        {'queryset': SimpleModel.objects.all()}, name='simplemode_detail'),
    ]
