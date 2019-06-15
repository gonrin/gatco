import time
from datetime import datetime
import warnings
import socket
from .utils import CallbackDict

def is_ip(value):
    """Determine if the given string is an IP address.
    :param value: value to check
    :type value: str
    :return: True if string is an IP address
    :rtype: bool
    """

    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.inet_pton(family, value)
        except socket.error:
            pass
        else:
            return True

    return False

class SessionDict(CallbackDict):
    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True

        super().__init__(initial, on_update)

        self.sid = sid
        self.modified = False

class BaseSessionInterface:
    
    def init_app(self, app):
        """Setup with application's configuration.
        This method be called automatically if the application is provided
        upon initialization
        """
        setdefault = app.config.setdefault
        self.cookie_name = setdefault('SESSION_COOKIE_NAME', 'session')
        self.domain = self.get_cookie_domain(app)
        self.httponly = setdefault('SESSION_COOKIE_HTTPONLY', True)
        self.expiry = setdefault('SESSION_COOKIE_MAX_AGE', 86400)
        self.secure = setdefault('SESSION_COOKIE_SECURE', False)
        self.session_name = setdefault('SESSION_NAME', 'session')
        self.__sanic_version__ = app.__sanic_version__
        
        @app.middleware('request')
        async def add_session_to_request(request):
            # before each request initialize a session
            # using the client's request
            await self.open(request)
    
    
        @app.middleware('response')
        async def save_session(request, response):
            # after each request save the session,
            # pass the response to set client cookies
            await self.save(request, response)
            
    def delete_cookie(self, request, response):
        #response.cookies[self.cookie_name] = request['session'].sid
        response.cookies[self.cookie_name] = None
        response.cookies[self.cookie_name]['expires'] = datetime.now()
        response.cookies[self.cookie_name]['max-age'] = 0

    def set_cookie(self, request, response):
        response.cookies[self.cookie_name] = request['session'].sid
        response.cookies[self.cookie_name]['expires'] = self.get_cookie_expires()
        response.cookies[self.cookie_name]['max-age'] = self.expiry
        response.cookies[self.cookie_name]['httponly'] = self.httponly

        if self.domain:
            response.cookies[self.cookie_name]['domain'] = self.domain
    
    def get_cookie_expires(self):
        expires = time.time() + self.expiry

        major_version = None
        try:
            major_version = self.__sanic_version__.split(".")
            if len(major_version) > 0:
                major_version = int(major_version[0])
        except:
            pass

        if (major_version is not None) and (major_version > 18):
            return  datetime.fromtimestamp(expires)
        else:
            return time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(expires)) 
    
    def get_cookie_domain(self, app):
        rv = app.config.get('SESSION_COOKIE_DOMAIN')
        if rv is not None:
            return rv if rv else None
        rv = app.config.get('SERVER_NAME')
        if not rv:
            app.config['SESSION_COOKIE_DOMAIN'] = False
            return None
        rv = rv.rsplit(':', 1)[0].lstrip('.')
        if '.' not in rv:
            warnings.warn(
                '"{rv}" is not a valid cookie domain, it must contain a ".".'
                ' Add an entry to your hosts file, for example'
                ' "{rv}.localdomain", and use that instead.'.format(rv=rv)
            )
            app.config['SESSION_COOKIE_DOMAIN'] = False
            return None
        ip = is_ip(rv)
        if ip:
            warnings.warn(
                'The session cookie domain is an IP address. This may not work'
                ' as intended in some browsers. Add an entry to your hosts'
                ' file, for example "localhost.localdomain", and use that'
                ' instead.'
            )

        # if this is not an ip and app is mounted at the root, allow subdomain
        # matching by adding a '.' prefix
        if self.get_cookie_path(app) == '/' and not ip:
            rv = '.' + rv

        app.config['SESSION_COOKIE_DOMAIN'] = rv
        return rv
    
    def get_cookie_path(self, app):
        """Returns the path for which the cookie should be valid.  The
        default implementation uses the value from the ``SESSION_COOKIE_PATH``
        config var if it's set, and falls back to ``APPLICATION_ROOT`` or
        uses ``/`` if it's ``None``.
        """
        return app.config.get('SESSION_COOKIE_PATH') \
               or app.config.get('APPLICATION_ROOT')