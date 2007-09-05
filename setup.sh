#!/bin/bash
if [ ! "$UID" -eq 0 ]; then
	echo "This script must be run as super-user, you could use sudo '"$0"'"
	exit 1
fi

cp engine/vdown /usr/bin/vdown
mkdir -p /usr/lib/python2.5/site-packages/gvdown/glade
cp gvdown.conf /usr/lib/python2.5/site-packages/gvdown.conf.example
cp gvdown.conf /etc/gvdown.conf
cp glade/gvdown.glade /usr/lib/python2.5/site-packages/gvdown/glade/gvdown.glade
cp gvdown.py controller.py config.py gvdown_handler.py handler.py /usr/lib/python2.5/site-packages/gvdown/
cp man/vdown.1 /usr/share/man/man1/vdown.1
cp gvdown /usr/bin/gvdown
cp gvdown.xpm /usr/share/pixmaps/
cp gvdown.desktop /usr/share/applications

echo "Installed gvdown succesfully (if no errors were shown)."
exit 0
