from optparse import make_option
from collections import defaultdict, Iterable
from django.db import DEFAULT_DB_ALIAS

from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers import serialize
from django.db.models import ForeignKey, get_model
from django.db import models
from django.template import Variable

from objectdump.models import get_key, get_related_fields, ObjectFilter
from objectdump.settings import MODEL_SETTINGS


class Command(BaseCommand):
    help = ("Output the contents of one or more objects and their related "
            "items as a fixture of the given format.")
    args = "app_name.model_name [id1 [id2 [...]]]"

    option_list = BaseCommand.option_list + (
        make_option('--format',
            default='json',
            dest='format',
            help='Specifies the output serialization format for fixtures.'),
        make_option('--indent',
            default=None,
            dest='indent',
            type='int',
            help='Specifies the indent level to use when pretty-printing output'),
        make_option('--database',
            action='store',
            dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Nominates a specific database to dump '
                 'fixtures from. Defaults to the "default" database.'),
        make_option('-e', '--exclude',
            dest='exclude',
            action='append',
            default=[],
            help='An appname or appname.ModelName to exclude (use multiple '
                 '--exclude to exclude multiple apps/models).'),
        make_option('-n', '--natural',
            action='store_true',
            dest='use_natural_keys',
            default=False,
            help='Use natural keys if they are available.'),
        make_option('--depth',
            dest='depth',
            default=None,
            type='int',
            help='Max depth related objects to get'),
        make_option('--limit',
            dest='limit',
            default=None,
            type='int',
            help='Max number of related objects to get'),
        make_option('--include', '-i',
            dest='include',
            action='append',
            default=[],
            help='An appname or appname.ModelName to whitelist related objects '
                'included in the export (use multiple --include to include '
                'multiple apps/models).'),
        make_option('--idtype',
            dest='idtype',
            default='int',
            help='The natural type of the id(s) specified. [int, unicode, long]'),
        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False,
            help='Output debug information. Shows what additional objects each object generates.')
        )

    def process_additional_relations(self, obj, limit=None):
        key = ".".join([obj._meta.app_label, obj._meta.module_name])
        addl_relations = MODEL_SETTINGS.get(key, {}).get('addl_relations', [])
        output = []
        obj_key = get_key(obj)
        for rel in addl_relations:
            if callable(rel):
                rel_objs = rel(obj)
            else:
                rel_objs = Variable("object.%s" % rel).resolve({'object': obj})
            if not rel_objs:
                continue
            if not isinstance(rel_objs, Iterable):
                rel_objs = [rel_objs]
            for rel_obj in rel_objs:
                rel_key = get_key(rel_obj)
                self.depends_on[rel_key].add(obj_key)
                self.generates[obj_key].add(rel_key)
                if self.verbose:
                    print "%s.%s ->" % (obj_key, rel), rel_key
                output.append(rel_obj)
        return output

    def process_related_fields(self, obj, limit=None):
        related_fields = get_related_fields(obj)
        output = []
        obj_key = get_key(obj)
        key = ".".join([obj._meta.app_label, obj._meta.module_name])
        m2m_fields = MODEL_SETTINGS.get(key, {}).get('m2m_fields', related_fields)
        if m2m_fields == True:
            m2m_fields = related_fields
        elif m2m_fields == False:
            m2m_fields = []
        for rel in m2m_fields:
            try:
                related_objs = obj.__getattribute__(rel)
                #handle OneToOneField case for related object
                if isinstance(related_objs, models.Model):
                    related_objs = [related_objs]
                else:  # everything else uses a related manager
                    related_objs = related_objs.all()

                if limit:
                    related_objs = related_objs[:limit]
                for rel_obj in related_objs:
                    rel_key = get_key(rel_obj)
                    self.depends_on[rel_key].add(obj_key)
                    self.generates[obj_key].add(rel_key)
                    if self.verbose:
                        print "%s.%s ->" % (obj_key, rel), rel_key
                    output.append(rel_obj)
            except (FieldError, ObjectDoesNotExist):
                pass
        return output

    def process_foreignkeys(self, obj):
        output = []
        obj_key = get_key(obj)
        key = ".".join([obj._meta.app_label, obj._meta.module_name])
        all_field_names = obj._meta.get_all_field_names()
        fk_fields = MODEL_SETTINGS.get(key, {}).get('fk_fields', all_field_names)
        if fk_fields == True:
            fk_fields = all_field_names
        elif fk_fields == False:
            fk_fields = []
        for field in obj._meta.fields:
            if isinstance(field, ForeignKey) and field.name in fk_fields:
                fk_obj = obj.__getattribute__(field.name)
                if fk_obj:
                    fk_key = get_key(fk_obj)
                    self.depends_on[obj_key].add(fk_key)
                    self.generates[obj_key].add(fk_key)
                    if self.verbose:
                        print "%s.%s ->" % (obj_key, field.name), fk_key
                    output.append(fk_obj)
        return output

    def process_object(self, obj, obj_filter=None):
        # Abort cyclic references.
        if obj._meta.proxy:
            obj = obj._meta.proxy_for_model.objects.get(pk=obj.pk)

        if obj in self.priors:
            return
        self.priors.add(obj)

        if obj_filter is not None and obj_filter.skip(obj):
            return

        obj_key = get_key(obj)
        self.key_to_object[obj_key] = obj
        self.to_serialize.append(obj)
        return obj_key

    def process_queue(self, objs, obj_filter=None, limit=None, max_depth=None):
        """
        Generate a list of objects to serialize
        """
        self.depends_on = defaultdict(set)  # {key: set(keys being pointed to)}
        self.generates = defaultdict(set)
        self.key_to_object = {}
        self.to_serialize = []

        # Recursively serialize all related objects.
        self.priors = set()
        _queue = list(objs)
        self.queue = zip(_queue, [0] * len(_queue))  # queue is obj, depth
        while self.queue:
            obj, depth = self.queue.pop(0)

            obj_key = self.process_object(obj, obj_filter)
            if obj_key is None:
                continue

            if max_depth is None or depth <= max_depth:
                rel_objs = self.process_related_fields(obj, limit)
                for rel in rel_objs:
                    self.queue.append((rel, depth + 1))
            addl_rel_objs = self.process_additional_relations(obj)
            for ar_obj in addl_rel_objs:
                self.queue.append((ar_obj, depth + 1))
            fk_objs = self.process_foreignkeys(obj)
            for fk_obj in fk_objs:
                self.queue.append((fk_obj, depth + 1))

    def handle(self, *args, **options):
        format = options.get('format')
        indent = options.get('indent')
        using = options.get('database')
        excludes = options.get('exclude')
        includes = options.get('include')
        show_traceback = options.get('traceback')
        use_natural_keys = options.get('use_natural_keys')
        max_depth = options.get("depth")
        limit = options.get("limit")
        debug = options.get("debug")
        self.verbose = int(options.get('verbosity')) > 1
        id_cast = {
            'int': int,
            'unicode': unicode,
            'long': long,
        }[options.get('idtype')]

        if len(args) < 1:
            raise CommandError('You must specify the model.')
        if "." not in args[0]:
            raise CommandError('You must specify the model as "appname.modelname".')

        main_model = args[0]
        app_label, model_name = main_model.split('.')
        primary_model = get_model(app_label, model_name)
        obj_filter = ObjectFilter(primary_model, excludes, includes)

        ids = [id_cast(i) for i in args[1:]]

        # Lookup initial model records.
        if ids:
            objs = primary_model.objects.using(using).filter(pk__in=ids).iterator()
        else:
            objs = primary_model.objects.using(using).iterator()

        self.process_queue(objs, obj_filter, limit, max_depth)
        serialization_order = self.to_serialize

        # Order serialization so that dependents come after dependencies.
        def cmp_depends(a, b):
            if a in self.depends_on[b]:
                return -1
            elif b in self.depends_on[a]:
                return +1
            return cmp(get_key(a, as_tuple=True), get_key(b, as_tuple=True))
        serialization_order = list(serialization_order)
        serialization_order.sort(cmp=cmp_depends)
        try:
            # self.stdout.ending = None
            if debug:
                import pprint
                pprint.pprint(dict(self.generates), stream=self.stdout)
                return
            serialize(format,
                      [o for o in serialization_order if o is not None],
                      indent=indent,
                      use_natural_keys=use_natural_keys,
                      stream=self.stdout)
        except Exception as e:
            if show_traceback:
                raise
            raise CommandError("Unable to serialize database: %s" % e)
