from sanic import *
from .sessions import CookieSessionInterface

__version__ = '0.1.0'

__all__ = ['Sanic', 'Blueprint']

class Gatco(Sanic):
    session_interface = CookieSessionInterface()

    def __init__(self, *args, **kw):
        super(Gatco, self).__init__(*args, **kw)
        if (not hasattr(self, 'extensions')) or (self.extensions is None):
            self.extensions = {}
            
    def run(self, *args, **kw):
        if self.session_interface is not None:
            self.session_interface.init_app(self)
        super(Gatco, self).run(*args, **kw)
