﻿# mpc-lirc

	Small script to control mpd using mpc with a remote control.
	It was created for a Raspberry Pi board.
	The main script file is mpc_lirc.py.


## Dependencies:

	apt-get install mpd mpc lirc python3 python3-lirc python3-django-web-utils

	python3-django-web-utils: https://github.com/sdiemer/django-web-utils


## Setup

	Do not forget to run "mpc update" before trying to play any music with mpd.

	Copy the file mpc-lirc-init in "/etc/init.d/mpc-lirc" and run "update-rc.d mpc-lirc defaults 96 00".

	See the following page for lirc configuration:
	http://alexba.in/blog/2013/01/06/setting-up-lirc-on-the-raspberrypi/
