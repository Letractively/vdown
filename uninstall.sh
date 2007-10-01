#!/bin/bash
if [ ! "$UID" -eq 0 ]; then
	echo "This script must be run as super-user, you could use sudo '"$0"'"
	exit 1
fi

rm /usr/bin/vdown
rm -rf /usr/lib/python2.5/site-packages/gvdown
rm /etc/gvdown.conf
rm /usr/share/man/man1/vdown.1
rm /usr/bin/gvdown
rm /usr/share/applications/gvdown.desktop
rm /usr/share/pixmaps/gvdown.xpm

echo "Removed gvdown successfully."
exit 0
