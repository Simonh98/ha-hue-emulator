import sys, logging, json
from ws4py.client.threadedclient import WebSocketClient
from ws4py import messaging
from types import SimpleNamespace
from Bridge import Bridge
from Config import Config
# sys.path.append(".")
import helpers as helper
# import Integration

log = logging.getLogger("HA Service")

class Hasher(dict):
    # https://stackoverflow.com/a/3405143/190597
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

class Light:
    def __init__(self) -> None:
        self.entity_id = None
        self.friendly_name = None
        self.on = False
        self.bri = 125
        self.color = (None, None, None)
        # self.color_temp = 
        
    def update_ha_state(self, state: dict):
        self.on = helper.safeget(state, self.on, 'state')
        self.bri = helper.safeget(state, self.bri, 'attributes', 'brightness')
        self.color = tuple(helper.safeget(state, self.color, 'attributes', 'rgb_color'))
        self.entity_id = helper.safeget(state, self.entity_id, 'entity_id')
        self.friendly_name = helper.safeget(state, self.color, 'attributes', 'friendly_name')
        # log.info(json.dumps(state, sort_keys=True, indent=4))
        log.info(f"{self.entity_id=}, {self.friendly_name=}, {self.on=}, {self.bri=}, {self.color=}")

class HomeAssistant(WebSocketClient):
    
    @property
    def id(self):
        self.msgid = 0 if self.msgid > 2e10 else self.msgid + 1
        return self.msgid
    
    SUBSCRIBE_STATE_CHANGE_ID = 242
    UNSUBSCRIBE_STATE_CHANGE_ID = 241
    GET_STATES_ID = 214
    
    def __init__(self, config_service: Config, bridge_service: Bridge, protocols) -> None:
        self.bridge_service = bridge_service
        
        self.ip = config_service.ha_ip
        self.port = config_service.ha_port
        self.token = config_service.ha_token
        
        self.url = f'ws://{self.ip}:{self.port}/api/websocket'
        super().__init__(url=self.url, protocols=protocols)
        
        
        self.lights = {
            'light.philips_hue_go_1': Light()
        }
        
        self.msgid = 1
        self.pending_responses = {}
        
        self.rx_event_map = {
            'auth_required' : self.on_auth_required,
            'auth_ok' : self.on_auth_complete,
            'auth_invalid' : self.on_auth_invalid,
            'result' : self.on_result,
            'event' : self.on_event,
            'pong' : self.on_pong
        }

    def opened(self):
        log.info("WebSocket connection opened")

    def closed(self, code, reason=None):
        log.info(f"WebSocket connection closed ({code=}, {reason=})")

    def received_message(self, msg: messaging.TextMessage):
        # log.debug(f"Message received: {msg}")
        message_text = msg.data.decode(msg.encoding)
        message: dict = json.loads(message_text)
        type = message.get('type', None)
        try:
            dispatch = self.rx_event_map[type]
        except KeyError:
            log.warning(f"Unkown message received: {type=}")
        else:
            dispatch(message)
        
    def on_auth_required(self, *_):
        log.info("Authetication required")
        payload = {
            'type': 'auth',
            'access_token': self.token
        }
        self.send_json(payload)

    def on_auth_complete(self, *_):
        log.info("Authentication complete")
        self.get_states()
        self.subscribe_state_changes()

    def on_auth_invalid(self, msg):
        log.error(f"Authentication invalid: {msg}")

    def on_result(self, msg):
        log.info(f"on_result()")
        if helper.safeget(msg, -1, 'id') != self.GET_STATES_ID:
            return
        for state in helper.safeget(msg, [], 'result'):
            try:
                self.lights[state['entity_id']].update_ha_state(state)
                # log.info(json.dumps(state, sort_keys=True, indent=4))
            except KeyError:
                pass
            # self.pending_responses.pop(msg['id'])()

    def on_event(self, msg):
        if msg['id'] != self.SUBSCRIBE_STATE_CHANGE_ID:
            return
        try:
            self.lights[msg['event']['data']['entity_id']].update_ha_state(msg['event']['data']['new_state'])
        except KeyError:
            pass

    def on_pong(self, msg):
        log.info(f"on_pong() {msg=}")
        
    #########
    
    def get_states(self):
        log.info("Fetching states")
        def _fetch_entities():
            log.info("_fetch_entities() -> getstates")
        self.send_request({'type': 'get_states'}, _fetch_entities)
    
    #####
        
    def send_json(self, data: dict):
        json_payload = json.dumps(data)
        self.send(json_payload)
        
    def send_request(self, data: dict, callback):
        data['id'] = self.msgid
        self.pending_responses[self.msgid] = callback
        self.msgid += 1
        self.send_json(data)
        
    def on_state_change(self, data: dict):
        pass
        
    def subscribe_state_changes(self):
        self.send_json({
            'id': self.SUBSCRIBE_STATE_CHANGE_ID,
            'type': 'subscribe_events',
            'event_type': 'state_changed'
        })
        
    def get_states(self):
        self.send_json({
            'id': self.GET_STATES_ID,
            'type': 'get_states'
        })
        
    def unsubscribe_state_change(self):
        self.send_json({
            "id": self.UNSUBSCRIBE_STATE_CHANGE_ID,
            "type": "unsubscribe_events",
            "subscription": self.SUBSCRIBE_STATE_CHANGE_ID
        })
        