#!/bin/sh
#
# THIS SCRIPT WILL INSTALL THE GNORDVPN APP SYSTEM WIDE
# THE SCRIPT MUST BE RUN WITH SUDO
#
# It will create a startup shell script named glanscan in /usr/bin,
# the app will be placed in /usr/share/glanscan-sprokkel78

mkdir -p /usr/local/share/glanscan-sprokkel78
cp -r ./* /usr/local/share/glanscan-sprokkel78/
echo "#!/bin/sh" > /usr/local/bin/glanscan
echo "cd /usr/local/share/glanscan-sprokkel78" >> /usr/local/bin/glanscan
echo "python3 ./glanscan.py" >> /usr/local/bin/glanscan
chmod 755 /usr/local/bin/glanscan
chmod 644 /usr/local/share/glanscan-sprokkel78/*
