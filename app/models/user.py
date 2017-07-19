from datetime import datetime
import pytz
import random
import humanize
from flask import url_for
from sqlalchemy import event, desc
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from flask.ext.scrypt import generate_password_hash, generate_random_salt
from sqlalchemy.ext.hybrid import hybrid_property
from app.api.helpers.db import get_count
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.notification import Notification
from app.models.event_invoice import EventInvoice
from app.models.speaker import Speaker
from app.models import db
from app.models.notification import Notification
from app.models.permission import Permission
from app.models.role import Role
from app.models.service import Service
from app.models.custom_system_role import UserSystemRole
from app.models.user_permission import UserPermission
from app.models.users_events_role import UsersEventsRoles as UER
from app.models.panel_permission import PanelPermission
from app.models.helpers.versioning import clean_up_string, clean_html

# System-wide
ADMIN = 'admin'
SUPERADMIN = 'super_admin'

SYS_ROLES_LIST = [
    ADMIN,
    SUPERADMIN,
]

# Event-specific
ORGANIZER = 'organizer'
COORGANIZER = 'coorganizer'
TRACK_ORGANIZER = 'track_organizer'
MODERATOR = 'moderator'
ATTENDEE = 'attendee'
REGISTRAR = 'registrar'


class User(db.Model):
    """User model class"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    _email = db.Column(db.String(120), unique=True, nullable=False)
    _password = db.Column(db.String(128), nullable=False)
    reset_password = db.Column(db.String(128))
    salt = db.Column(db.String(128))
    avatar_url = db.Column(db.String)
    tokens = db.Column(db.Text)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    details = db.Column(db.String)
    contact = db.Column(db.String)
    facebook_url = db.Column(db.String)
    twitter_url = db.Column(db.String)
    instagram_url = db.Column(db.String)
    google_plus_url = db.Column(db.String)
    original_image_url = db.Column(db.String, nullable=True, default=None)
    thumbnail_image_url = db.Column(db.String)
    small_image_url = db.Column(db.String)
    icon_image_url = db.Column(db.String)
    is_super_admin = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    last_accessed_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(pytz.utc))
    deleted_at = db.Column(db.DateTime(timezone=True))
    speaker = db.relationship('Speaker', backref="user")
    access_code = db.relationship('AccessCode', backref="user")
    discount_code = db.relationship('DiscountCode', backref="user_")
    event_invoice = db.relationship('EventInvoice', backref="user_")
    notifications = db.relationship('Notification', backref="user")

    @hybrid_property
    def password(self):
        """
        Hybrid property for password
        :return:
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Setter for _password, saves hashed password, salt and reset_password string
        :param password:
        :return:
        """
        salt = generate_random_salt()
        self._password = generate_password_hash(password, salt)
        hash_ = random.getrandbits(128)
        self.reset_password = str(hash_)
        self.salt = salt

    @hybrid_property
    def email(self):
        """
        Hybrid property for email
        :return:
        """
        return self._email

    @email.setter
    def email(self, email):
        """
        Setter for _email, can be only set once
        :param email:
        :return:
        """
        if self._email is None:
            self._email = email
        else:
            raise AttributeError("Email cannot be modified")

    # User Permissions
    def can_publish_event(self):
        """Checks if User can publish an event
        """
        perm = UserPermission.query.filter_by(name='publish_event').first()
        if not perm:
            return self.is_verified

        return perm.unverified_user

    def can_create_event(self):
        """Checks if User can create an event
        """
        perm = UserPermission.query.filter_by(name='create_event').first()
        if not perm:
            return self.is_verified

        if self.is_verified is False:
            return perm.unverified_user

        return True

    def has_role(self, event_id):
        """Checks if user has any of the Roles at an Event.
        Exclude Attendee Role.
        """
        attendee_role = Role.query.filter_by(name=ATTENDEE).first()
        uer = UER.query.filter(UER.user == self, UER.event_id == event_id,
                               UER.role != attendee_role).first()
        if uer is None:
            return False
        else:
            return True

    def _is_role(self, role_name, event_id):
        """Checks if a user has a particular Role at an Event.
        """
        role = Role.query.filter_by(name=role_name).first()
        uer = UER.query.filter_by(user=self,
                                  event_id=event_id,
                                  role=role).first()
        if not uer:
            return False
        else:
            return True

    def is_organizer(self, event_id):
        # type: (object) -> object
        return self._is_role(ORGANIZER, event_id)

    def is_coorganizer(self, event_id):
        return self._is_role(COORGANIZER, event_id)

    def is_track_organizer(self, event_id):
        return self._is_role(TRACK_ORGANIZER, event_id)

    def is_moderator(self, event_id):
        return self._is_role(MODERATOR, event_id)

    def is_registrar(self, event_id):
        return self._is_role(REGISTRAR, event_id)

    def is_attendee(self, event_id):
        return self._is_role(ATTENDEE, event_id)

    def _has_perm(self, operation, service_class, event_id):
        # Operation names and their corresponding permission in `Permissions`
        operations = {
            'create': 'can_create',
            'read': 'can_read',
            'update': 'can_update',
            'delete': 'can_delete',
        }
        if operation not in operations.keys():
            raise ValueError('No such operation defined')

        try:
            service_name = service_class.get_service_name()
        except AttributeError:
            # If `service_class` does not have `get_service_name()`
            return False

        if self.is_super_admin:
            return True

        service = Service.query.filter_by(name=service_name).first()

        uer_querylist = UER.query.filter_by(user=self,
                                            event_id=event_id)
        for uer in uer_querylist:
            role = uer.role
            perm = Permission.query.filter_by(role=role,
                                              service=service).first()
            if getattr(perm, operations[operation]):
                return True

        return False

    def can_create(self, service_class, event_id):
        return self._has_perm('create', service_class, event_id)

    def can_read(self, service_class, event_id):
        return self._has_perm('read', service_class, event_id)

    def can_update(self, service_class, event_id):
        return self._has_perm('update', service_class, event_id)

    def can_delete(self, service_class, event_id):
        return self._has_perm('delete', service_class, event_id)

    def is_speaker_at_session(self, session_id):
        try:
            session = Session.query.filter(Session.speakers.any(Speaker.user_id == self.id)).filter(
                Session.id == session_id).one()
            if session:
                return True
            else:
                return False
        except MultipleResultsFound:
            return False
        except NoResultFound:
            return False

    def is_speaker_at_event(self, event_id):
        try:
            session = Session.query.filter(Session.speakers.any(Speaker.user_id == self.id)).filter(
                Session.event_id == event_id).first()
            if session:
                return True
            else:
                return False
        except MultipleResultsFound:
            return False
        except NoResultFound:
            return False

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @property
    def is_staff(self):
        return self.is_super_admin or self.is_admin

    def is_sys_role(self, role_id):
        """Check if a user has a Custom System Role assigned.
        `role_id` is id of a `CustomSysRole` instance.
        """
        role = UserSystemRole.query.filter_by(user=self, role_id=role_id).first()
        return bool(role)

    def first_access_panel(self):
        """Check if the user is assigned a Custom Role or not
        This checks if there is an entry containing the current user in the `user_system_roles` table
        returns panel name if exists otherwise false
        """
        custom_role = UserSystemRole.query.filter_by(user=self).first()
        if not custom_role:
            return False
        perm = PanelPermission.query.filter_by(role_id=custom_role.role_id, can_access=True).first()
        if not perm:
            return False
        return perm.panel_name

    def can_access_panel(self, panel_name):
        """Check if user can access an Admin Panel
        """
        if self.is_staff:
            return True

        custom_sys_roles = UserSystemRole.query.filter_by(user=self)
        for custom_role in custom_sys_roles:
            if custom_role.role.can_access(panel_name):
                return True

        return False

    def get_unread_notif_count(self):
        return get_count(Notification.query.filter_by(user=self, is_read=False))

    def get_unread_notifs(self):
        """Get unread notifications with titles, humanized receiving time
        and Mark-as-read links.
        """
        notifs = []
        unread_notifs = Notification.query.filter_by(user=self, is_read=False).order_by(
            desc(Notification.received_at))
        for notif in unread_notifs:
            notifs.append({
                'title': notif.title,
                'received_at': humanize.naturaltime(datetime.now(pytz.utc) - notif.received_at),
                'mark_read': url_for('notifications.mark_as_read', notification_id=notif.id)
            })

        return notifs

    # update last access time
    def update_lat(self):
        self.last_accessed_at = datetime.now(pytz.utc)

    @property
    def fullname(self):
        firstname = self.firstname if self.firstname else ''
        lastname = self.lastname if self.lastname else ''
        if firstname and lastname:
            return u'{} {}'.format(firstname, lastname)
        else:
            return ''

    def __repr__(self):
        return '<User %r>' % self.email

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.email

    def __setattr__(self, name, value):
        if name == 'details':
            super(User, self).__setattr__(name, clean_html(clean_up_string(value)))
        else:
            super(User, self).__setattr__(name, value)


@event.listens_for(User, 'init')
def receive_init(target, args, kwargs):
    target.signup_at = datetime.now(pytz.utc)
