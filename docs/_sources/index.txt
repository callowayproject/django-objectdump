=============================
django-objectdump v |version|
=============================

Goals
=====

* Export one or more objects with their relations so that when loaded again with Django's ``loaddata`` command, the object and all its connections are intact.

* Serialize objects in any format supported by Django's serialization framework

* Allow customization of the objects exported (to support generic relations and any other custom relations)

* Provide debug feedback indicating from where related objects were linked.



Contents
========

.. toctree::
   :maxdepth: 2
   :glob:

   getting_started
   reference/index
