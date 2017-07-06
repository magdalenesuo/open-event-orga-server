from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from pytz import timezone
from datetime import datetime

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.bootstrap import api
from app.models.role_invite import RoleInvite
from app.models.event import Event
from app.models.role import Role



class RoleInviteSchema(Schema):
    """
    Api schema for role invite Model
    """
    class Meta:
        """
        Meta class for role invite Api Schema
        """
        type_ = 'role-invite'
        self_view = 'v1.role_invite_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    email = fields.Str()
    hash = fields.Str()
    created_at = fields.DateTime(timezone=True)
    is_declined = fields.Bool(default=False)
    role_id = fields.Integer()

    event = Relationship(attribute='event',
                         self_view='v1.role_invite_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'role_invite_id': '<id>'},
                         schema='EventSchema',
                         type_='event')

    role = Relationship(attribute='role',
                         self_view='v1.role_invite_role',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.role_detail',
                         related_view_kwargs={'role_invite_id': '<id>'},
                         schema='RoleSchema',
                         type_='role')

class RoleInviteList(ResourceList):
    """
    List and create role invite
    """
     def query(self, view_kwargs):
        """
        query method for Role Invite List
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(RoleInvite)
        if view_kwargs.get('event_id'):
            try:
                event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_id'},
                                     "Event: {} not found".format(view_kwargs['event_id']))
            else:
                query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('event_identifier'):
            try:
                event = self.session.query(Event).filter_by(identifier=view_kwargs['event_identifier']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))

        if view_kwargs.get('role_id'):
            try:
                role = self.session.query(Role).filter_by(id=view_kwargs['role_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'role_id'},
                                     "Role: {} not found".format(view_kwargs['role_id']))
            else:
                query_ = query_.join(Role).filter_by(role_id=role.id)

        return query_

    def before_create_object(self, data, view_kwargs):
        """
        Method to create object before posting
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_id'):
            try:
                event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_id'},
                                     "Event: {} not found".format(view_kwargs['event_id']))
            else:
                data['event_id'] = event.id

        elif view_kwargs.get('event_identifier'):
            try:
                event = self.session.query(Event).filter_by(identifier=view_kwargs['event_identifier']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                data['event_id'] = event.id

    view_kwargs = True
    decorators = (api.has_permission('is_organizer', methods="POST"),)
    schema = RoleInviteSchema
    data_layer = {'session': db.session,
                  'model': RoleInvite,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object}}


class RoleInviteDetail(ResourceDetail):
    """
    Role detail by id
    """
    decorators = (api.has_permission('is_organizer', methods="PATCH,DELETE"),)
    schema = RoleInviteSchema
    data_layer = {'session': db.session,
                  'model': RoleInvite}

class TicketTagRelationship(ResourceRelationship):
    """
    TicketTag Relationship
    """
    decorators = (jwt_required,)
    schema = TicketTagSchema
    data_layer = {'session': db.session,
                  'model': TicketTag}
