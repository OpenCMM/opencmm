#!/bin/bash

# ref. https://github.com/mtconnect/cppagent/tree/main/unix

sudo useradd -r -s /bin/false mtconnect

sudo mkdir /var/log/mtconnect
sudo chown mtconnect:mtconnect /var/log/mtconnect

sudo mkdir -p /etc/mtconnect/cfg 
sudo cp ../unix/agent.cfg /etc/mtconnect/cfg/
sudo cp dist/bin/agent /usr/local/bin/
sudo cp -r dist/share/mtconnect/styles dist/share/mtconnect/schemas dist/share/mtconnect/simulator /etc/mtconnect/
sudo chown -R mtconnect:mtconnect /etc/mtconnect