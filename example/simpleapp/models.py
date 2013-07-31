# -*- coding: utf-8 -*-
"""
42. Serialization

``django.core.serializers`` provides interfaces to converting Django
``QuerySet`` objects to and from "flat" data (i.e. strings).
"""
from __future__ import unicode_literals

from decimal import Decimal

from django.db import models
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Author(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Tag(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class TaggedItem(models.Model):
    tag = models.ForeignKey(Tag)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "Tag: %s, Model: %s" % (self.tag, self.content_object)


@python_2_unicode_compatible
class Article(models.Model):
    author = models.ForeignKey(Author)
    headline = models.CharField(max_length=50)
    pub_date = models.DateTimeField()
    categories = models.ManyToManyField(Category)

    class Meta:
        ordering = ('pub_date', )

    def __str__(self):
        return self.headline


@python_2_unicode_compatible
class TaggedArticle(models.Model):
    author = models.ForeignKey(Author)
    headline = models.CharField(max_length=50)
    pub_date = models.DateTimeField()
    categories = models.ManyToManyField(Category)

    class Meta:
        ordering = ('pub_date', )

    def __str__(self):
        return self.headline


@python_2_unicode_compatible
class AuthorProfile(models.Model):
    author = models.OneToOneField(Author, primary_key=True)
    date_of_birth = models.DateField()

    def __str__(self):
        return "Profile of %s" % self.author


@python_2_unicode_compatible
class Actor(models.Model):
    name = models.CharField(max_length=20, primary_key=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name
