#!/bin/bash
if [ ! "$UID" -eq 0 ]; then
        echo "This script must be run as super-user, you could use 'sudo "$0"'"
        exit 1
fi
rm -rf /usr/lib/python2.5/site-packages/gvdown
rm /usr/bin/vdown
rm /usr/bin/gvdown

echo "Removed gvdown successfully."
