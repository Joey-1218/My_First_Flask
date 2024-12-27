import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    # instance_relative_config (bool)
    # if set to True relative filenames for loading the config are assumed to be 
    # relative to the instance path instead of the application root.
    app = Flask(__name__, instance_relative_config=True)

    # create and configure the app
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # If test_config is None, it means the application is not in testing mode.
    if test_config is None:
        # The silent=True parameter means:
        # If the file doesn’t exist, Flask will not raise an error. 
        # It will silently skip loading the file.
        app.config.from_pyfile('config.py', silent=True)

    # If test_config is provided, it indicates the application is in testing mode, 
    # and the provided configuration values should be loaded instead of the default ones.
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    # Register a Blueprint on the application.
    app.register_blueprint(auth.bp)

    return app