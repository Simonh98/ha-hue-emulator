from Bridge import Bridge
from Config import Config
from Messaging import Messaging
from werkzeug.serving import WSGIRequestHandler
import ssl, logging
from flask import Flask
from flask.json import jsonify
from flask_cors import CORS
from flask_restful import Api
from Endpoints.v1.User import ShortConfig, NewUser
from Endpoints.v2.Resource import ClipV2Resource
from Endpoints.v2.EventStream import EventStream
from Endpoints.v2.ClipV2 import ClipV2
from Endpoints.v1.ResourceElements import ResourceElements
from Endpoints.v2.ClipV2ResourceId import ClipV2ResourceId
from threading import Thread

log = logging.getLogger(__name__)
# logging.getLogger('werkzeug').setLevel(logging.ERROR)

class Core:
    
    def __init__(self, confing_service: Config, messaging_service: Messaging, bridge_service: Bridge) -> None:
        
        self.bridge_service = bridge_service
        self.messaging_service = messaging_service
        
        WSGIRequestHandler.protocol_version = "HTTP/1.1"
        self.app = Flask(__name__, template_folder='flaskUI/templates',static_url_path="/static", static_folder='flaskUI/static')
        self.api = Api(self.app)
        self.cors = CORS(self.app, resources={r"*": {"origins": "*"}})

        self.app.config['SECRET_KEY'] = 'change_this_to_be_secure'
        self.api.app.config['RESTFUL_JSON'] = {'ensure_ascii': False}
        
        # v1
        self.api.add_resource(NewUser, '/api', strict_slashes=False)
        self.api.add_resource(ShortConfig, '/api/config', strict_slashes=False)
        # api.add_resource(EntireConfig, '/api/<string:username>', strict_slashes=False)
        self.api.add_resource(ResourceElements, '/api/<string:username>/<string:resource>', strict_slashes=False)
        # api.add_resource(Element, '/api/<string:username>/<string:resource>/<string:resourceid>', strict_slashes=False)
        # api.add_resource(ElementParam, '/api/<string:username>/<string:resource>/<string:resourceid>/<string:param>/', strict_slashes=False)
        # api.add_resource(ElementParamId, '/api/<string:username>/<string:resource>/<string:resourceid>/<string:param>/<string:paramid>/', strict_slashes=False)
        
        # v2
        self.api.add_resource(EventStream, '/eventstream/clip/v2', strict_slashes=False)
        self.api.add_resource(ClipV2, '/clip/v2/resource', strict_slashes=False)
        self.api.add_resource(ClipV2Resource, '/clip/v2/resource/<string:resource>', strict_slashes=False)
        self.api.add_resource(ClipV2ResourceId, '/clip/v2/resource/<string:resource>/<string:resourceid>', strict_slashes=False)
        
        self.ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ctx.load_cert_chain(certfile=f"{confing_service.certpath}")
        self.ctx.options |= ssl.OP_CIPHER_SERVER_PREFERENCE
        self.ctx.set_ciphers('ECDHE-ECDSA-AES128-GCM-SHA256')
        self.ctx.set_ecdh_curve('prime256v1')
        
    def run_forever(self):
        Thread(target=lambda: self.app.run(host='0.0.0.0', port=443, ssl_context=self.ctx)).start()
        self.app.run(host='0.0.0.0', port=80)