========
Tutorial
========

The goal is to export an object and all related objects. This export might be used as test fixtures, sample data, or for transferring to a duplicate system.

We start out exporting a tagged article, and we'll use the debug and verbose mode to see what will get included:

.. code-block:: bash

   $ ./manage.py object_dump simpleapp.taggedarticle 1 --debug -v2

::

   simpleapp.taggedarticle.1.categories -> simpleapp.category.1
   simpleapp.taggedarticle.1.author -> simpleapp.author.1
   simpleapp.author.1.taggedarticle_set -> simpleapp.taggedarticle.1
   simpleapp.author.1.taggedarticle_set -> simpleapp.taggedarticle.4
   simpleapp.author.1.authorprofile -> simpleapp.authorprofile.1
   simpleapp.taggedarticle.4.categories -> simpleapp.category.2
   simpleapp.taggedarticle.4.categories -> simpleapp.category.1
   simpleapp.taggedarticle.4.author -> simpleapp.author.1
   simpleapp.authorprofile.1.author -> simpleapp.author.1

   ----------------------------------------------
   Which models cause which others to be included
   ----------------------------------------------
   {'simpleapp.author.1': set(['simpleapp.authorprofile.1',
                               'simpleapp.taggedarticle.1',
                               'simpleapp.taggedarticle.4']),
    'simpleapp.authorprofile.1': set(['simpleapp.author.1']),
    'simpleapp.taggedarticle.1': set(['simpleapp.author.1',
                                      'simpleapp.category.1']),
    'simpleapp.taggedarticle.4': set(['simpleapp.author.1',
                                      'simpleapp.category.1',
                                      'simpleapp.category.2'])}

   ----------------------------------------------
   Dependencies
   ----------------------------------------------
   simpleapp.taggedarticle.4
        categories
            simpleapp.category.1
            simpleapp.category.2
        author
            simpleapp.author.1
   simpleapp.taggedarticle.1
        categories
            simpleapp.category.1
        author
            simpleapp.author.1
   simpleapp.authorprofile.1
        author
            simpleapp.author.1

   ----------------------------------------------
   Serialization order
   ----------------------------------------------
   [<Author: Obi Wan>,
    <Category: Nation>,
    <Category: World>,
    <TaggedArticle: Stars at war>,
    <TaggedArticle: The Empire returns fire>,
    <AuthorProfile: Profile of Obi Wan>]


This shows that the original object's categories many-to-many field added one category object and the author foreign key added an author object.

The author object is related to two articles: the one we want, and another one. This additional article is now added. The author's profile is also added.

The additional article added another category to the list of objects.

So far we have an extra article, an extra category, and no tags. We will have to configure Object Dump to modify how it follows relations.


Excluding Relations
===================

The cause of one of our issues is the Author model. It has a foreign key named ``authorprofile``\ , and a reverse relation attribute named ``taggedarticle_set``. ``Author.taggedarticle_set`` brings in another article by the same author, which in turn brings in an additional category.

We need to prevent object_dump from following that reverse relation. We can do this easily through the configuration:

.. code-block:: python

   OBJECTDUMP_SETTINGS = {
       'MODEL_SETTINGS': {
           'simpleapp.author': {'reverse_relations': False},
       }
   }

``reverse_relations`` can be either ``False`` to exclude all reverse relations, or a white-list of relations to follow.


Running the management command again reveals fewer objects:

.. code-block:: bash

   $ ./manage.py object_dump simpleapp.taggedarticle 1 --debug -v2

::

   simpleapp.taggedarticle.1.categories -> simpleapp.category.1
   simpleapp.taggedarticle.1.author -> simpleapp.author.1

   ----------------------------------------------
   Which models cause which others to be included
   ----------------------------------------------
   {'simpleapp.taggedarticle.1': set(['simpleapp.author.1',
                                      'simpleapp.category.1'])}

   ----------------------------------------------
   Dependencies
   ----------------------------------------------
   simpleapp.taggedarticle.1
        categories
            simpleapp.category.1
        author
            simpleapp.author.1

   ----------------------------------------------
   Serialization order
   ----------------------------------------------
   [<Category: World>, <Author: Obi Wan>, <TaggedArticle: Stars at war>]


Including Relations
===================
