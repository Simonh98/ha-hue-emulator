from dependency_injector import containers, providers
from Config import Config
from Bridge.Bridge import Bridge
from Messaging import Messaging
from HomeAssistant import HomeAssistant

class Container(containers.DeclarativeContainer):
    config_service = providers.Singleton(Config)
    messaging_service = providers.Singleton(Messaging)
    bridge_service = providers.Singleton(Bridge, config_service=config_service)
    hass_service = providers.Singleton(
        HomeAssistant, 
        config_service=config_service,
        bridge_service=bridge_service,
        protocols=['http-only', 'chat']
    )