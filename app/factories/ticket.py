import factory
from app.models.ticket import db, Ticket
from app.factories.event import EventFactoryBasic
import app.factories.common as common


class TicketFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Ticket
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    description = common.string_
    is_description_visible = common.string_
    type = common.string_
    quantity = common.integer_
    position = common.integer_
    price = common.float_
    is_fee_absorbed = False
    sales_starts_at = common.date_
    sales_ends_at = common.dateEnd_
    is_hidden = False
    min_order = common.integer_
    max_order = common.integer_
