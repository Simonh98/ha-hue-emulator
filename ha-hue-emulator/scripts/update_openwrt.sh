#!/bin/bash

echo -e "\033[32m Disable startup service.\033[0m"
/etc/init.d/hueemulatorWrt-service disable
echo -e "\033[32m Create directory for backup configuration.\033[0m"
mkdir /tmp/diyHue-config
echo -e "\033[32m Copying configuration file.\033[0m"
cp /opt/ha-hue-emulator/config.json /tmp/diyHue-config/config.json.bak
cp /opt/ha-hue-emulator/cert.pem /tmp/diyHue-config/cert.pem.bak
echo -e "\033[32m Deleting directories.\033[0m"
rm -Rf /opt/ha-hue-emulator
rm -Rf /etc/init.d/hueemulatorWrt-service
echo -e "\033[32m Updating python3-pip.\033[0m"
python3 -m pip install --upgrade pip
wait
echo -e "\033[32m Updating pip dependencies.\033[0m"
python3 -m pip install --upgrade requests
wait
python3 -m pip install --upgrade astral
wait
python3 -m pip install --upgrade pytz
wait
python3 -m pip install --upgrade ws4py
wait
python3 -m pip install --upgrade paho-mqtt
wait
echo -e "\033[32m Creating directories.\033[0m"
mkdir /opt
mkdir /opt/tmp
mkdir /opt/ha-hue-emulator
cd /opt/tmp
echo -e "\033[32m Downloading diyHue.\033[0m"
wget -q https://github.com/diyhue/diyHue/archive/master.zip -O diyHue.zip
echo -e "\033[32m Unzip diyHue.\033[0m"
unzip -q -o  diyHue.zip
wait
echo -e "\033[32m Copying unzip files to directories.\033[0m"
cd /opt/tmp/diyHue-master/BridgeEmulator
cp HueEmulator3.py updater /opt/ha-hue-emulator/
cp /tmp/diyHue-config/config.json.bak /opt/ha-hue-emulator/config.json
cp /tmp/diyHue-config/cert.pem.bak /opt/ha-hue-emulator/cert.pem
cp default-config.json /opt/ha-hue-emulator/default-config.json
cp -r functions protocols debug web-ui /opt/ha-hue-emulator/
echo -e "\033[32m Detecting processor architecture.\033[0m"
wait
arch=`uname -m`
wait
echo -e "\033[32m Architecture detected: $arch\033[0m"
echo -e "\033[32m Copying binary $arch for Openwrt.\033[0m"
cp entertainment-openwrt-$arch /opt/ha-hue-emulator/entertain-srv
echo -e "\033[32m Copying custom network function for openwrt.\033[0m"
rm -Rf /opt/ha-hue-emulator/functions/network.py
mv /opt/ha-hue-emulator/functions/network_OpenWrt.py /opt/ha-hue-emulator/functions/network.py
wait
echo -e "\033[32m Copying startup service.\033[0m"
cp /opt/tmp/diyHue-master/BridgeEmulator/hueemulatorWrt-service /etc/init.d/
echo -e "\033[32m Changing permissions.\033[0m"
chmod +x /etc/init.d/hueemulatorWrt-service
chmod +x /opt/ha-hue-emulator/HueEmulator3.py
chmod +x /opt/ha-hue-emulator/debug
chmod +x /opt/ha-hue-emulator/protocols
chmod +x /opt/ha-hue-emulator/updater
chmod +x /opt/ha-hue-emulator/web-ui
chmod +x /opt/ha-hue-emulator/functions
chmod +x /opt/ha-hue-emulator/config.json
chmod +x /opt/ha-hue-emulator/default-config.json
chmod +x /opt/ha-hue-emulator/entertain-srv
chmod +x /opt/ha-hue-emulator/functions/network.py
echo -e "\033[32m Enable startup service.\033[0m"
/etc/init.d/hueemulatorWrt-service enable
wait
echo -e "\033[32m Update completed.\033[0m"
rm -Rf /opt/tmp
echo -e "\033[32m Restarting...\033[0m"
wait
reboot 10
exit 0
