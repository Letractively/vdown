#!/bin/bash
if [ ! "$UID" -eq 0 ]; then
        echo "This script must be run as super-user, you could use 'sudo "$0"'"
        exit 1
fi
#which python2.5 > /dev/null || echo "Python 2.5 must be installed!" && exit 1
mkdir -p /usr/lib/python2.5/site-packages/gvdown/po
cp *.py *.glade /usr/lib/python2.5/site-packages/gvdown
cp nonsrc/gvdown.xpm /usr/share/pixmaps/
cp nonsrc/gvdown.desktop /usr/share/applications/
cp -R po/ /usr/lib/python2.5/site-packages/gvdown/
echo '#!/bin/bash
cd /usr/lib/python2.5/site-packages/gvdown
./gui.py
exit 0' > /usr/bin/gvdown
echo '#!/bin/bash
CWD=$(pwd)
cd /usr/lib/python2.5/site-packages/gvdown
./cli.py --destination=$CWD $@
exit 0' > /usr/bin/vdown
chmod +x /usr/bin/vdown
chmod +x /usr/bin/gvdown
echo ""
echo "Installation was successful, if no errors were shown."
echo "You can now start vdown with 'vdown URL1 URL2' and so on, you can start gvdown with Applications->Internet->GVDOWN or 'gvdown'."
