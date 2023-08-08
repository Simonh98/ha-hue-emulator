import traceback, yaml, pathlib, logging, subprocess, os
import helpers as helper

log = logging.getLogger(__name__)

class Config:
    
    def __init__(self) -> None:
        self.config = self.get_config()
        self.host = helper.safeget(self.config, '0.0.0.0', 'host')
        self.mac: str = helper.safeget(self.config, '', 'mac')
        self.netmask = helper.safeget(self.config, '', 'netmask')
        self.gateway = helper.safeget(self.config, '', 'gateway')
        self.certpath = helper.safeget(self.config, 'cert.pem', 'certpath')
        self.ha_ip = helper.safeget(self.config, '', 'HomeAssistant', 'ip')
        self.ha_port = helper.safeget(self.config, 8123, 'HomeAssistant', 'port')
        self.ha_token = helper.safeget(self.config, '', 'HomeAssistant', 'token')
        self.try_generate_certificate()
        
    def try_generate_certificate(self):
        
        if os.path.isfile(self.certpath):
            return
        log.info("Generating certificate")
        mac = self.mac.replace(':', '')
        serial = (mac[:6] + "fffe" + mac[-6:]).encode('utf-8')
        t = subprocess.call(["/bin/bash", "/opt/ha-hue-emulator/scripts/genCert.sh", serial, '/opt/ha-hue-emulator'])
        self.certpath = f'/opt/ha-hue-emulator/cert.pem'
        log.info("Certificate created")
    
    def get_config(self, file=None):
        if file is None:
            file = f"{pathlib.Path().resolve()}/ha-hue-emulator/conf.main.yaml"
        config = {}
        try:
            with open(file, "r") as stream:
                config: dict = yaml.safe_load(stream)
            log.info(f"Loaded \"{file}\"")
        except:
            log.error(traceback.format_exc())
        return config