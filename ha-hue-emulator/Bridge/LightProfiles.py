from dataclasses import dataclass, asdict, field
import traceback, logging, uuid, random
import helpers as helper

log = logging.getLogger(__name__)

# https://developers.meethue.com/develop/hue-api/supported-devices/

def generate_unique_id():
    rand_bytes = [random.randrange(0, 256) for _ in range(3)]
    return "00:17:88:01:00:%02x:%02x:%02x-0b" % (rand_bytes[0], rand_bytes[1], rand_bytes[2])

@dataclass
class ColorGamut:
    A = [[0.704,	0.296], [0.2151, 0.7106], [0.138, 0.08]]
    B = [[0.675,	0.322], [0.409, 0.518], [0.167, 0.04]]
    C = [[0.692,	0.308], [0.17, 0.7], [0.153, 0.048]]
    
# @dataclass
# class State:
#     reachable: bool
#     on: bool
#     transitiontime: int
#     alert: str
#     mode: str # homeautomation, streaming

# @dataclass
# class Config:
#     pass

# @dataclass
# class Capabilities:
#     certified: bool = True
#     renderer: bool = True
#     proxy: bool = False

# @dataclass
# class Swupdate:
#     state: str
#     lastinstall: int

# @dataclass
# class OnOffLight:
#     type: str
#     name: str
#     modelid: str
#     productid: str
#     swversion: str
#     swconfigid: str
#     state: State
#     config: Config
#     capabilities: Capabilities
#     swipdate: Swupdate

@dataclass
class XY:
    x: float
    y: float

# TODO Add optional attributes
# https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
@dataclass
class Light:
    
    @dataclass
    class Dimming:
        brightness: float # 0 - 100
    
    @dataclass
    class Owner:
        rid: str
        rtype: str = 'light'
        
    @dataclass
    class Metadata:
        name: str
        archtype: str = 'sultan_bulb'
        # fixed_mired: int = None
        
    @dataclass
    class ColorTempearture:
        
        @dataclass
        class MirekSchema:
            mirek_minimum: int = 153
            mirek_maximum: int = 500
        
        mirek: int # 153 - 500
        mirek_valid: bool
        mirek_schema: MirekSchema
        
        
        archtype: str = 'sultan_bulb'
        # fixed_mired: int = None

    @dataclass
    class Color:
        @dataclass
        class Gamut:
            red: XY
            green: XY
            blue: XY
            
        xy: XY
        gamut: Gamut
        gamut_type: str # A, B, C, other

    id_v1: str
    owner: Owner
    metadata: Metadata
    mode: str = 'normal'
    type: str = 'light'
    on: bool = False
    id: str = None
    effects: dict = field(default_factory=dict)
    dimming: Dimming = None
    color_temperature: ColorTempearture = None
    color: Color = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = helper.getuuid()
        self.uniqueid = generate_unique_id()

    def asdict(self):
        # return {k: v for k, v in self.__dict__.items() if v is not None}
        data = asdict(self)
        if data['dimming'] is None: data['dimming'] = {}
        if data['color_temperature'] is None: data['color_temperature'] = {}
        if data['color'] is None: data['color'] = {}
        data['on'] = {'on': data['on']}
        return data

# https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device_get
@dataclass
class Device:
    
    @dataclass
    class ProductData:
        model_id: str
        manufacturer_name: str
        product_name: str
        product_archtype: str = 'sultan_bulb'
        certified: bool = True
        software_version: str = '1.90.1'
    @dataclass
    class Metadata:
        name: str
        archtype: str = 'sultan_bulb'
    @dataclass
    class Service:
        rid: str
        rtype: str
    
    id_v1: str
    product_data: ProductData
    metadata: Metadata
    id: str = None
    services: list[Service] = field(default_factory=list)
    
    identify: dict = field(default_factory=dict)
    type: str = 'device'
    
    def __post_init__(self):
        if self.id is None:
            self.id = helper.getuuid()
        self.link_zigbee_connectivity()
        
    def get_light_services(self) -> list:
        ret = []
        for service in self.services:
            if service.rtype == 'light':
                ret.append(service.rid)
        return ret
        
    def link_lightservice(self, light: Light):
        try:
            self.services.append(Device.Service(light.owner.rid, light.owner.rtype))
        except KeyError:
            log.error(traceback.format_exc())
            
    def link_zigbee_connectivity(self):
        for service in self.services:
            if service.rtype == 'zigbee_connectivity':
                return
        self.services.append(Device.Service(
            str(uuid.uuid5(uuid.NAMESPACE_URL, f'{self.id}zigbee_connectivity')), 'zigbee_connectivity'
        ))
    
    def unlink_lightservice(self, light: Light):
        try:
            for service in self.services:
                if service.rid == light.owner.rid and service.rtype == light.owner.rtype:
                    # TODO inefficient
                    self.services.remove(service)
                    return
        except KeyError:
            log.error(traceback.format_exc())

    def asdict(self):
        data = asdict(self)
        return data