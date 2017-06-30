import factory
from app.models.setting import Setting
import app.factories.common as common


class SettingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Setting
        sqlalchemy_session = db.session

	payment_country: common.country_
    paypal_email: common.email_
    thumbnail_image_url: common.image_url_
    schedule_published_on: common.date_
    payment_currency: common.currency_
    organizer_description: common.string_
    is_map_shown: True
    original_image_url: common.image_url_
    onsite_details: common.string_
    organizer_name: common.string_
    can_pay_by_stripe: True
    large_image_url: common.image_url_
    timezone: common.timezone_
    can_pay_onsite: true
    deleted_at: common.date_
    ticket_url: common.url_
    can_pay_by_paypal: True
    location_name: common.string_
    is_sponsors_enabled: False
    is_sessions_speakers_enabled: True
    privacy: common.string_
    code_of_conduct: common.image_url_
    state: common.image_url_
    latitude: common.float_
    starts_at: common.date_
    searchable_location_name: common.string_
    is_ticketing_enabled: True
    can_pay_by_cheque: True
    description: common.string_
    pentabarf_url: null
    xcal_url: null
    logo_url: common.image_url_
    event_url: common.url_
    is_tax_enabled: True
    icon_image_url: common.image_url_
    ical_url: common.url_
    name: common.string_
    can_pay_by_bank: True
    ends_at: common.dateEnd_
    created_at: common.date_
    longitude: common.float_
    bank_details: common.string_
    cheque_details: common.string_
    identifier: common.string_