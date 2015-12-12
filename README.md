h1. mopidy-lirc

Small script to control mpd through mpc with a remote control.
It was created for a Raspberry Pi board.
The main script file is mpc_lirc.py.


h2. Dependencies:

	apt-get install mpd mpc lirc python3 python3-django-web-utils

	python3-django-web-utils: https://github.com/sdiemer/django-web-utils


h2. Notes

Do not forget to run "mpc update" before trying to play any music with mpd.