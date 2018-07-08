import logging
from .base import BaseSessionInterface
from itsdangerous import URLSafeTimedSerializer, BadSignature

log = logging.getLogger(__name__)

class CookieSessionInterface(BaseSessionInterface):
    session_type = dict
    def __init__(self, app=None, domain: str=None, expiry: int = 86400,
            httponly: bool=True, cookie_name: str = 'session'):
        self.expiry = expiry
        self.cookie_name = cookie_name
        self.domain = domain
        self.httponly = httponly
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        super(CookieSessionInterface, self).init_app(app)
        secret_key = app.config.get('SESSION_COOKIE_SECRET_KEY')
        if not secret_key:
            secret_key = app.config.get('SECRET_KEY')
        if not secret_key:
            raise RuntimeError(
                'either SESSION_COOKIE_SECRET_KEY or SECRET_KEY must be set')
        salt_key = app.config.get('SESSION_COOKIE_SALT')
        if not salt_key:
            raise RuntimeError('SESSION_COOKIE_SALT must be set')
        
        self.serializer = URLSafeTimedSerializer(secret_key, salt=salt_key)
        
    
    async def open(self, request) -> dict:
        if self.session_name in request:
            return
        session_cookie = request.cookies.get(self.cookie_name)
        
        if session_cookie:
            try:
                session = self.serializer.loads(session_cookie, max_age=self.expiry)
            except BadSignature as ex:
                log.warning('%s - %s', ex, ex.payload)
                session = self.session_type()
        else:
            session = self.session_type()
        request[self.session_name] = session
        return session
    
    async def save(self, request, response) -> None:
        session = request.get(self.session_name)
        if session is None:
            session = request[self.session_name] = self.session_type()
        response.cookies[self.cookie_name] = self.serializer.dumps(session)
        response.cookies[self.cookie_name]['expires'] = self.get_cookie_expires()
        response.cookies[self.cookie_name]['max-age'] = self.expiry
        response.cookies[self.cookie_name]['httponly'] = self.httponly
        if self.secure:
            response.cookies[self.cookie_name]['secure'] = self.secure
        if self.domain:
            response.cookies[self.cookie_name]['domain'] = self.domain