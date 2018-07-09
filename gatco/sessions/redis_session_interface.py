import ujson
from .base import BaseSessionInterface, SessionDict
import uuid

class RedisSessionInterface(BaseSessionInterface):
    def __init__(
            self, domain: str=None, expiry: int = 2592000,
            httponly: bool=True, cookie_name: str='session',
            prefix: str='session:'):
        """Initializes a session interface backed by Redis.
        Args:
            domain (str, optional):
                Optional domain which will be attached to the cookie.
            expiry (int, optional):
                Seconds until the session should expire.
            httponly (bool, optional):
                Adds the `httponly` flag to the session cookie.
            cookie_name (str, optional):
                Name used for the client cookie.
            prefix (str, optional):
                Memcache keys will take the format of `prefix+session_id`;
                specify the prefix here.
        """
        
        self.expiry = expiry
        self.prefix = prefix
        self.cookie_name = cookie_name
        self.domain = domain
        self.httponly = httponly
    
    def init_app(self, app):
        super(RedisSessionInterface, self).init_app(app)
        redis_uri = app.config.get('SESSION_REDIS_URI')
        if not redis_uri:
            raise RuntimeError('SESSION_REDIS_URI must be set')
        
        try:
            import redis
            self.redis_db = redis.StrictRedis.from_url(redis_uri)
        except:
            raise RuntimeError('redis must be installed')

    async def open(self, request):
        """Opens a session onto the request. Restores the client's session
        from Redis if one exists.The session data will be available on
        `request.session`.
        Args:
            request (gatco.request.Request):
                The request, which a sessionwill be opened onto.
        Returns:
            dict:
                the client's session data,
                attached as well to `request.session`.
        """
        if self.session_name in request:
            return

        sid = request.cookies.get(self.cookie_name)
        
        if not sid:
            sid = uuid.uuid4().hex + uuid.uuid4().hex
            session_dict = SessionDict(sid=sid)
        else:
            key = sid if sid.startswith(self.prefix) else self.prefix + sid
            val = self.redis_db.get(key)
            if val is not None:
                data = ujson.loads(val)
                session_dict = SessionDict(data, sid=sid)
            else:
                session_dict = SessionDict(sid=sid)

        request[self.session_name] = session_dict
        return session_dict

    async def save(self, request, response) -> None:
        """Saves the session into Redis and returns appropriate cookies.
        Args:
            request (sanic.request.Request):
                The sanic request which has an attached session.
            response (sanic.response.Response):
                The Sanic response. Cookies with the appropriate expiration
                will be added onto this response.
        Returns:
            None
        """
        if self.session_name not in request:
            return
        
        sid =  request[self.session_name].sid
        
        key = sid if sid.startswith(self.prefix) else self.prefix + sid 
        
        if (not request[self.session_name]) or (len(request[self.session_name]) == 0):
            self.redis_db.delete(key)
            self.delete_cookie(request, response)
        else:
            val = ujson.dumps(dict(request[self.session_name]))
            
            p = self.redis_db.pipeline()
            p.set(key, val)
            p.expire(key, self.expiry)
            p.execute()
            
            response.cookies[self.cookie_name] = key
            response.cookies[self.cookie_name]['expires'] = self.get_cookie_expires()
            response.cookies[self.cookie_name]['max-age'] = self.expiry
            response.cookies[self.cookie_name]['httponly'] = self.httponly
        
        
        if self.secure and (self.cookie_name in response.cookies):
            response.cookies[self.cookie_name]['secure'] = self.secure
        if self.domain and (self.cookie_name in response.cookies):
            response.cookies[self.cookie_name]['domain'] = self.domain