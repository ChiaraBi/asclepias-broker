# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
#
# Asclepias Broker is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Admin model views for Asclepias broker."""

from __future__ import absolute_import, print_function

import json

from flask import redirect, request, url_for
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_babelex import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms.fields import StringField
from wtforms.validators import DataRequired

from .cli import find_json, update_groups
from .models import Event, Identifier, Relationship


class IdentifierModelView(ModelView):
    """ModelView for the Indentifier."""

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    column_display_all_relations = True

    column_list = (
        'id',
        'value',
        'scheme',
    )

    column_searchable_list = ('value',)


class RelationshipModelView(ModelView):
    """ModelView for the Relationship."""

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    column_display_all_relations = True

    column_list = (
        'id',
        'source_id',
        'target_id',
        'relation',
        'deleted',
        'source',
        'target',

    )


class EventModelView(ModelView):
    """ModelView for the Event."""

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    column_display_all_relations = True

    column_list = (
        'id',
        'user_id',
        'status',
        'payload',
    )

    column_searchable_list = ('payload',)


class UpdateMetadataForm(FlaskForm):
    """Form for updating groups metadata."""

    dir_path = StringField(
        _('Directory'),
        description=_('Required.'),
        validators=[DataRequired()],
    )


class UpdateMetadataView(BaseView):
    """View for updating groups metadata."""

    @expose('/', methods=('GET', 'POST'))
    def update_metadata(self):
        """."""
        update_metadata_form = UpdateMetadataForm()
        message = None
        if update_metadata_form.validate_on_submit():
            dir_path = request.form['dir_path']

            # update metadata
            files = find_json(dir_path)
            for fn in files:
                with open(fn, 'r') as fp:
                    data = json.load(fp)
                update_groups(data)

            # TODO: display a message
            # return redirect(url_for('updatemetadataview.update_metadata'))
        return self.render('asclepias_broker/update_metadata.html',
                           update_metadata_form=update_metadata_form)


identifier_adminview = dict(
    model=Identifier,
    modelview=IdentifierModelView,
)


relationship_adminview = dict(
    model=Relationship,
    modelview=RelationshipModelView,
)


event_adminview = dict(
    model=Event,
    modelview=EventModelView,
)


updatemetadata_adminview = {
    'view_class': UpdateMetadataView,
    'kwargs': {'name': 'Update Group Metadata'},
}
