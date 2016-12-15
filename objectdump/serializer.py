from django.utils import six
from collections import defaultdict
from django.contrib.contenttypes.fields import GenericRelation


class PerObjectSerializer(object):
    """
    This will subclass the selected serializer to change the method of
    serialization
    """

    def get_selected_fields(self, obj, included_fields, excluded_fields):
        """
        Sort out all the included/excluded fields for an object

        Initial fields are either the white listed fields passed in with the
        ``fields`` option, or all fields

        Then remove anything listed in ``excluded_fields``
        """
        key = "%s.%s" % (obj._meta.app_label, obj._meta.model_name)
        if key in self.cached_selected_fields:
            return self.cached_selected_fields[key]
        if key not in included_fields and key not in excluded_fields and not self.use_gfks:
            self.cached_selected_fields[key] = None
            return None
        if key in included_fields:
            selected_fields = set(included_fields[key])
        else:
            concrete_obj = obj._meta.concrete_model
            names = [x.attname for x in
                                concrete_obj._meta.local_fields
                                if x.rel is None]
            names += [x.attname[:-3] for x in
                                concrete_obj._meta.local_fields
                                if x.rel is not None]
            names += [getattr(x, 'attname') for x in concrete_obj._meta.many_to_many if hasattr(x, 'attname')]
            selected_fields = set(names)
        if self.use_gfks:
            gfks = concrete_obj._meta.virtual_fields
            for gfk in gfks:
                if isinstance(gfk, GenericRelation):
                    continue
                try:
                    selected_fields.remove(gfk.fk_field)
                    selected_fields.remove(gfk.ct_field)
                except (AttributeError, ValueError, ):
                    pass
                selected_fields.add(gfk.name)
        if key in excluded_fields:
            # print "<!-- Excluding", excluded_fields[key], " -->"
            selected_fields -= set(excluded_fields[key])
            for i in excluded_fields[key]:
                # print "<!--", i, "-->"
                assert i not in selected_fields
        # print "<!-- ", type(obj), " fields: ", selected_fields, " -->"
        self.cached_selected_fields[key] = list(selected_fields)
        return self.cached_selected_fields[key]

    def serialize(self, queryset, **options):
        """
        Serialize a queryset.

        ``fields`` now accepts a dict of {'app_label.model': ['field1', ...]}
        ``exclude_fields`` accepts a dict in the above format. These fields
        are removed from all fields

        """
        self.options = options
        self.stream = options.pop("stream", six.StringIO())
        self.use_natural_keys = options.pop("use_natural_keys", False)
        self.use_natural_foreign_keys = options.pop('use_natural_foreign_keys', False)
        self.use_natural_primary_keys = options.pop('use_natural_primary_keys', False)
        self.use_gfks = hasattr(self, 'handle_gfk_field') and self.use_natural_keys

        included_fields = options.pop("fields", {})
        excluded_fields = options.pop("exclude_fields", {})
        self.cached_selected_fields = defaultdict(set)

        self.start_serialization()
        self.first = True
        for obj in queryset:
            self.selected_fields = self.get_selected_fields(obj, included_fields, excluded_fields)
            try:
                obj._get_pk_val()
            except:
                continue
            self.start_object(obj)
            # Use the concrete parent class' _meta instead of the object's _meta
            # This is to avoid local_fields problems for proxy models. Refs #17717.
            concrete_model = obj._meta.concrete_model
            for field in concrete_model._meta.local_fields:
                if field.serialize:
                    if field.rel is None:
                        if self.selected_fields is None or field.attname in self.selected_fields:
                            self.handle_field(obj, field)
                    else:
                        if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                            self.handle_fk_field(obj, field)
            for field in concrete_model._meta.many_to_many:
                if field.serialize:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_m2m_field(obj, field)
            if self.use_gfks:
                for field in concrete_model._meta.virtual_fields:
                    if self.selected_fields is None or field.name in self.selected_fields:
                            self.handle_gfk_field(obj, field)
            self.end_object(obj)
            if self.first:
                self.first = False
        self.end_serialization()
        return self.getvalue()


def get_serializer(format='json'):
    from django.core.serializers import get_serializer as dj_get_ser
    s = dj_get_ser(format)
    return type('CustomSerializer', (PerObjectSerializer, s), {})
