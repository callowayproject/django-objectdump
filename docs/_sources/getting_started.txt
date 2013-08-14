===============
Getting Started
===============

Installation
============

#. Installation is easy using ``pip``\ .

   .. code-block:: bash

      $ pip install django-objectdump

#. Add to ``INSTALLED_APPS``

#. Optionally add configuration information (``OBJECTDUMP_SETTINGS``\ )


Settings
========

Object Dump's settings currently consist of one item: ``MODEL_SETTINGS``\ . ``MODEL_SETTINGS`` is a ``dict`` with the keys as ``'app.model'`` strings and the values a dict with one or more key-value pairs.

If ``'app.model'`` key is not in ``MODEL_SETTINGS``\ , object dump uses the defaults.

If one of the fields is not in the ``'app.model'``\ s ``dict``\ , object dump uses the default for that field.


.. code-block:: python

   OBJECTDUMP_SETTINGS = {
       'MODEL_SETTINGS': {
           'app.model': {
               'ignore': False,
               'fk_fields': True,  # or False, or ['whitelist', 'of', 'fks']
               'm2m_fields': True,  # or False, or ['whitelist', 'of', 'm2m fields']
               'addl_relations': [],  # callable, or 'othermodel_set.all' strings
               'reverse_relations': True,  # or False, or ['whitelist', 'of', 'reverse_relations']
           }
       }
   }


MODEL_SETTINGS value fields
---------------------------

``ignore``
    **Default:** ``False``

    If ``True``\ , always ignore this model. Acts as if you used ``--exclude`` with this model.

``fk_fields``
    **Default:** ``True``

    If ``False``\ , do not include related objects through foreign keys. Otherwise, a white-list of foreign keys to include related objects.

``m2m_keys``
    **Default:** ``True``

    If ``False``\ , do not include related objects through many-to-many fields. Otherwise, a white-list of many-to-many field names to include related objects.

``reverse_relations``
    **Default:** ``True``

    If ``False``\ , do not include additional objects using the reverse relations from this model. Reverse relations are usually accessed by "othermodel_set".

``addl_relations``
    A list of callables, which get passed an object, or strings in Django template syntax (``'author_set.all.0'`` becomes ``'object.author_set.all.0'`` and evaluates to ``object.author_set.all()[0]``\ )


Options
=======

``--format``
    **Default:** ``json``

    Specifies the output serialization format for fixtures. Options depend on ``SERIALIZATION_MODULES`` settings. ``xml`` and ``json`` and ``yaml`` are built-in.

``--indent``
    **Default:** ``None``

    Specifies the indent level to use. The default will not do any pretty-printing or indenting of content.

``--database``
    **Default:** ``DEFAULT_DB_ALIAS``

    Nominates a specific database to dump fixtures from. Defaults to the "default" database.

``-e``\ , ``--exclude``
    **Default:** ``[]``

    An appname or appname.ModelName to exclude (use multiple ``--exclude`` to exclude multiple apps/models).

``-n``\ , ``--natural``
    **Default:** ``False``

    Use natural keys if they are available.

``--depth``
    **Default:** ``None``

    Max depth related objects to get. The initial object specified is considered level 0. The default will get all objects.

``--limit``
    **Default:** ``None``

    Max number of related objects to get. Default gets all related objects.

``-i``\ , ``--include``
    **Default:** all

    An appname or appname.ModelName to whitelist related objects included in the export (use multiple ``--include`` to include multiple apps/models).

``--idtype``
    **Default:** ``'int'``

    The natural type of the id(s) specified. Options are: ``int``, ``unicode``, ``long``

``--debug``
    **Default:** ``False``

    Output debug information. Shows what related objects each object generates. Use with ``--verbosity 2`` to also see which fields are the link.
