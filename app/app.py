import logging
from logging.handlers import SMTPHandler
from sqlalchemy import inspect
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, render_template
from celery import Celery
from flask_compress import Compress
from app.blueprints.api import api
from app.blueprints.api.models.user import User
from app.extensions import (
    csrf,
    db,
    login_manager,
    cache,
    cors
)


CELERY_TASK_LIST = [
    'app.blueprints.api.tasks'
]


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()
    celery = Celery(broker=app.config.get('CELERY_BROKER_URL'), include=CELERY_TASK_LIST)
    celery.conf.update(app.config)
    celery.conf.beat_schedule = app.config.get('CELERYBEAT_SCHEDULE')
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True, subdomain_matching=True)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    # Keeps the app from crashing on reload
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 499
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 120
    app.static_folder = 'static'
    app.static_url_path = '/static'

    # CORS
    app.config['CORS_HEADERS'] = 'Content-Type'

    if settings_override:
        app.config.update(settings_override)

    middleware(app)
    error_templates(app)
    exception_handler(app)
    app.register_blueprint(api)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_error)
    template_processors(app)
    extensions(app)
    authentication(app, User)

    # Compress Flask app
    Compress(app)

    @app.errorhandler(500)
    def error_502(e):
        return render_template('errors/500.html')

    @app.errorhandler(404)
    def error_404(e):
        return render_template('errors/404.html')

    @app.errorhandler(502)
    def error_502(e):
        return render_template('errors/500.html')

    return app


def page_not_found(e):
    return render_template('errors/404.html'), 404


def internal_error(e):
    return render_template('errors/500.html'), 500


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': 'redis'})
    cors(app, support_credentials=True, resources={r"/*": {"origins": "*"}})

    return None


def template_processors(app):
    """
    Register 0 or more custom template processors (mutates the app passed in).

    :param app: Flask application instance
    :return: App jinja environment
    """
    app.jinja_env.filters['dict_filter'] = dict_filter
    app.jinja_env.filters['site_name_filter'] = site_name_filter

    return app.jinja_env


def authentication(app, user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = 'api.login'

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Swap request.remote_addr with the real IP address even if behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


def error_templates(app):
    """
    Register 0 or more custom error pages (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def render_status(status):
        """
         Render a custom template for a specific status.
           Source: http://stackoverflow.com/a/30108946

         :param status: Status as a written name
         :type status: str
         :return: None
         """
        # Get the status code from the status, default to a 500 so that we
        # catch all types of errors and treat them as a 500.
        code = getattr(status, 'code', 500)
        return render_template('errors/{0}.html'.format(code)), code

    for error in [404, 500]:
        app.errorhandler(error)(render_status)

    return None


def exception_handler(app):
    """
    Register 0 or more exception handlers (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    mail_handler = SMTPHandler((app.config.get('MAIL_SERVER'),
                                app.config.get('MAIL_PORT')),
                               app.config.get('MAIL_USERNAME'),
                               [app.config.get('MAIL_USERNAME')],
                               '[Exception handler] A 5xx was thrown',
                               (app.config.get('MAIL_USERNAME'),
                                app.config.get('MAIL_PASSWORD')),
                               secure=())

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter("""
    Time:               %(asctime)s
    Message type:       %(levelname)s


    Message:

    %(message)s
    """))
    app.logger.addHandler(mail_handler)

    return None


def dict_filter(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
    # return [x.as_dict() for x in l]


def site_name_filter(arg):
    from flask import current_app
    return current_app.config.get('SITE_NAME')


def site_url_filter(arg):
    from flask import current_app
    return current_app.config.get('SERVER_NAME')