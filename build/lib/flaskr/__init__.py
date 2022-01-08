'''
Study reviews - André Trigueiro:

This file refers to the configuration, registration and other setup the application needs.
It contains the APPLICATION FACTORY, and it tells Python that the flaskr directory should be treated as a package.

#create_app is the application factory function.
#app = Flask(__name__, instance_relative_config=True) creates the Flask instance
#instance_relative_config=True tells the app that configuration files are relative to the instance folder. 
#app.config.from_mapping() sets some default configuration that the app will use
#app.config.from_pyfile() overrides the default configuration with values taken from the config.py file in the instance folder if it exists. 
#os.makedirs() ensures that app.instance_path exists. 
#@app.route() creates a simple route

'''

import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
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

    # code to create a database with command
    from . import db
    db.init_app(app)

    # code to import and register the blueprint authentication
    from . import auth
    app.register_blueprint(auth.bp)

    # code of blog blueprint
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app