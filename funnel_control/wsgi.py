"""Production WSGI entrypoint that attaches the funnel control API to the existing app."""
from app import app as application
from .routes import funnel_bp

application.register_blueprint(funnel_bp)
app = application
