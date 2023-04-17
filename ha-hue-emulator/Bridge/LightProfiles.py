from dataclasses import dataclass
import traceback, logging

log = logging.getLogger(__name__)

# https://developers.meethue.com/develop/hue-api/supported-devices/


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
        fixed_mired: int = None
        
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
        fixed_mired: int = None

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

    id: str
    on: bool
    owner: Owner
    metadata: Metadata
    dimming: Dimming = None
    color_temperature: ColorTempearture = None
    color: Color = None

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
    
    id: str
    # id_v1: str
    services: list[Service]
    product_data: ProductData
    metadata: Metadata
    
    def link_lightservice(self, light: Light):
        try:
            self.services.append(Device.Service(light.owner.rid, light.owner.rtype))
        except KeyError:
            log.error(traceback.format_exc())
    
    def unlink_lightservice(self, light: Light):
        try:
            for service in self.services:
                if service.rid == light.owner.rid and service.rtype == light.owner.rtype:
                    # TODO inefficient
                    self.services.remove(service)
                    return
        except KeyError:
            log.error(traceback.format_exc())
