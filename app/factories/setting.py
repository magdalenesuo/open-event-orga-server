import factory
from app.models.setting import db, Setting
import app.factories.common as common


class SettingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Setting
        sqlalchemy_session = db.session

	app_environment= common.string_
    app_name= common.string_
    tagline= common.string_
    secret= common.string_
    storage_place= common.string_
    aws_key= common.string_
    aws_secret= common.string_
    aws_bucket_name= common.string_
    aws_region= common.string_
    gs_key= common.string_
    gs_secret= common.string_
    gs_bucket_name= common.string_
    google_client_id= common.string_
    google_client_secret= common.string_
    fb_client_id= common.string_
    fb_client_secret= common.string_
    tw_consumer_key= common.string_
    tw_consumer_secret= common.string_
    in_client_id= common.string_
    in_client_secret= common.string_
    stripe_client_id= common.string_
    stripe_secret_key= common.string_
    stripe_publishable_key= common.string_
    paypal_mode= common.string_
    paypal_sandbox_username= common.string_
    paypal_sandbox_password= common.string_
    paypal_sandbox_signature= common.string_
    paypal_live_username= common.string_    
    paypal_live_password= common.string_
    paypal_live_signature= common.string_
    email_service= common.string_
    email_from= common.string_
    email_from_name= common.string_
    sendgrid_key= common.string_
    smtp_host= common.string_
    smtp_username=common.string_
    smtp_password= common.string_
    smtp_port= common.string_
    smtp_encryption= common.string_
    analytics_key= common.string_
    google_url= common.url_
    github_url= common.url_
    twitter_url= common.url_
    support_url= common.url_
    facebook_url= common.url_
    youtube_url= common.url_
    android_app_url= common.url_
    web_app_url= common.url_