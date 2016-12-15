# -*- coding: utf-8 -*-
try:
    from django.apps import apps

    def get_model(app_label, model_name):
        return apps.get_model(app_label, model_name)

    def get_app(app_label):
        return apps.get_app_config(app_label).models_module
except ImportError:
    from django.db.models import get_model, get_app

from django.core.exceptions import ImproperlyConfigured

from .settings import MODEL_SETTINGS


def get_key(obj, as_tuple=False, include_pk=True):
    key = [obj._meta.app_label, obj._meta.model_name, ]
    if include_pk:
        key.append(obj.pk)

    if as_tuple:
        return tuple(key)
    return '.'.join(map(str, key))


def get_reverse_relations(obj):
    """
    Return all the related fields for an object
    """
    # These are the reverse relations. Typically show up as `<model_name>_set`
    related_objs = obj._meta.get_all_related_objects()
    return [rel.get_accessor_name() for rel in related_objs]


def get_many_to_many(obj):
    return [m2m_rel.name for m2m_rel in obj._meta.many_to_many]


def get_apps_and_models(appmodel_list):
    """
    Given a list of 'appname' and 'appname.modelname' return sets of
    actual apps and models
    """
    appset = set()
    modelset = set()
    if appmodel_list is None:
        appmodel_list = []
    for item in appmodel_list:
        try:
            if '.' in item:
                app_label, model_name = item.split('.', 1)
                model_obj = get_model(app_label, model_name)
                if not model_obj:
                    raise Exception('Unknown model specified: %s' % item)
                modelset.add(model_obj)
            else:
                try:
                    app_obj = get_app(item)
                    appset.add(app_obj)
                except ImproperlyConfigured:
                    raise Exception('Unknown app specified: %s' % item)
        except Exception as e:
            print e
            continue
    return appset, modelset


class ObjectFilter(object):
    """
    Handles all the stuff for excluding/including models and apps
    """
    def __init__(self, primary_model, exclude_list=None, include_list=None):
        if isinstance(primary_model, basestring):
            self.primary_model = get_model(*primary_model.split("."))
        else:
            self.primary_model = primary_model

        if self.primary_model is None:
            raise Exception("Unknown primary model: %s" % primary_model)

        if exclude_list is None:
            exclude_list = []

        for model, attrs in MODEL_SETTINGS.items():
            if attrs.get('ignore', False):
                exclude_list.append(model)

        self.excluded_apps, self.excluded_models = get_apps_and_models(
            exclude_list)
        self.included_apps, self.included_models = get_apps_and_models(
            include_list)

    def skip(self, obj):
        # Skip ignored models.
        if obj.__class__ in self.excluded_models:
            return True

        if get_app(obj._meta.app_label) in self.excluded_apps:
            return True

        # Skip models not specifically being included.
        if ((self.included_apps or self.included_models) and
            not isinstance(obj, self.primary_model)):
            if obj.__class__ not in self.included_models:
                return True

            if get_app(obj._meta.app_label) not in self.included_apps:
                return True

        return False
