#!/usr/bin/python3

import logging, sys
from Container import Container
import helpers as helper

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s,%(msecs)03d %(name)-20s %(levelname)-8s %(message)s', stream=sys.stdout)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def main():
    
    container = Container()
    container.init_resources()
    container.wire(modules=[
        __name__,
        'Endpoints.v1.User',
        'Endpoints.v1.ResourceElements',
        'Endpoints.v2.Resource',
        'Endpoints.v2.ClipV2',
        'Endpoints.v2.ClipV2ResourceId',
        'Endpoints.v2.EventStream'
    ])
    
    config_service = container.config_service()
    messaging_service = container.messaging_service()
    bridge_service = container.bridge_service()
    hass_service = container.hass_service()
    
    from Bridge.LightProfiles import Device
    from Bridge.LightProfiles import Light
    light_hue_go = Light(
        id_v1="/lights/2",
        owner=Light.Owner(helper.getuuid()),
        metadata=Light.Metadata('Hue Go lightservice'),
        dimming=Light.Dimming(0)
    )
    device_hue_go = Device(
        id_v1="/lights/1",
        # product_data=Device.ProductData('LLC020', 'Signify Netherlands B.V.', 'Hue Go'),
        product_data=Device.ProductData('LWB010', 'Signify Netherlands B.V.', 'LWB010'),
        metadata=Device.Metadata('Hue Go device')
    )
    device_hue_go.link_lightservice(light_hue_go)
    
    bridge_service.add_device(device_hue_go)
    bridge_service.add_light(light_hue_go)
    
    import Endpoints.Core
    core = Endpoints.Core.Core(config_service, messaging_service, bridge_service)
    
    hass_service.connect()
    core.run_forever()

if __name__ == '__main__':
    main()