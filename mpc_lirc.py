#!/usr/bin/python3
# -*- coding: utf-8 -*-

### BEGIN INIT INFO
# Provides:          mpc_lirc
# Required-Start:    $local_fs $network
# Required-Stop:     $local_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: mpc lirc daemon
# Description:       starts the mpc_lirc daemon
### END INIT INFO

# This script should be located in /etc/init.d/mpc-lirc
#   ln -s mpc_lirc.py /etc/init.d/mpc-lirc
# To make this script start at boot:
#   update-rc.d mpc_lirc defaults 96 00
# To remove it use:
#   update-rc.d -f mpc_lirc remove

# Do not forget to run "mpc update" before using other controls.

import lirc
import logging
import os
import subprocess
import sys
import time
# https://github.com/sdiemer/django-web-utils
from django_web_utils.daemon.base import BaseDaemon

logger = logging.getLogger('mpc_lirc')

USER = 'pi'
BASE_DIR = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))


class MopidyController(BaseDaemon):
    DAEMON_NAME = 'mpc_lirc'
    SERVER_DIR = BASE_DIR
    LOG_DIR = BASE_DIR
    CONF_DIR = BASE_DIR
    PID_DIR = BASE_DIR
    NEED_GOBJECT = False
    NEED_DJANGO = False
    #DEFAULTS = dict(LOGGING_LEVEL='INFO')
    
    def run(self, *args):
        root_dir = os.path.dirname(self.daemon_path)
        if root_dir.endswith('/.'):
            root_dir = root_dir[:-2]
        if root_dir != '':
            os.chdir(root_dir)
        self.playlist_index = 0
        # Play a sound to indicate the daemon is launched
        # (usefull when no screen is available)
        self.play_sound('online')
        self.start_listening()
    
    def execute(self, cmd):
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        out, err = p.communicate()
        out = out.decode('utf-8') if out else ''
        if err:
            if out:
                out += '\n'
            out += 'Stderr: ' + err.decode('utf-8')
        logger.debug('>>> %s', cmd)
        logger.debug('code: %s | %s', p.returncode, out)
        return p.returncode == 0, out
    
    def play_sound(self, name):
        self.execute(['aplay', 'sounds/%s.wav' % name])
    
    def load_playlist(self, index):
        self.execute(['/usr/bin/mpc', 'clear'])
        loaded, out = self.execute(['/usr/bin/mpc', 'load', 'playlist_%s' % index])
        if loaded:
            self.execute(['/usr/bin/mpc', 'play'])
        self.playlist_index = index
    
    def start_listening(self):
        logger.info('Using lircrc.conf: %s', os.path.join(BASE_DIR, 'lircrc.conf'))
        lirc.init('mpc_lirc', os.path.join(BASE_DIR, 'lircrc.conf'))
        logger.info('Ready to receive key events.')
        while True:
            try:
                received = lirc.nextcode()
            except Exception as e:
                logger.warning('lirc: Failed to get next code: %s', e)
                time.sleep(3)
            else:
                if received:
                    self.play_sound('received')
                    self.key_pressed(received[0])
    
    def key_pressed(self, key):
        if key == 'KEY_PLAYPAUSE':
            self.execute(['/usr/bin/mpc', 'toggle'])
        elif key == 'KEY_VOLUMEUP':
            self.execute(['/usr/bin/mpc', 'volume', '+10'])
        elif key == 'KEY_VOLUMEDOWN':
            self.execute(['/usr/bin/mpc', 'volume', '-10'])
        elif key == 'KEY_PREVIOUS':
            self.execute(['/usr/bin/mpc', 'prev'])
        elif key == 'KEY_NEXT':
            self.execute(['/usr/bin/mpc', 'next'])
        elif key == 'KEY_F1':
            self.execute([os.path.join(BASE_DIR, 'screen.sh'), 'on'])
        elif key == 'KEY_F2':
            self.execute([os.path.join(BASE_DIR, 'screen.sh'), 'off'])
        elif key == 'KEY_HOME':
            self.execute(['/usr/bin/mpc', 'shuffle'])
        elif key == 'KEY_MODE':
            self.play_sound('shutdown')
            self.execute(['sudo', 'shutdown', '-h', 'now'])
            lirc.deinit()
            sys.exit(0)
        elif key == 'KEY_CHANNELDOWN':
            i = self.playlist_index - 1
            if i >= 0:
                self.load_playlist(i)
        elif key == 'KEY_CHANNELUP':
            i = self.playlist_index + 1
            if i <= 9:
                self.load_playlist(i)
        elif key in ('KEY_0', 'KEY_1', 'KEY_2', 'KEY_3', 'KEY_4', 'KEY_5', 'KEY_6', 'KEY_7', 'KEY_8', 'KEY_9'):
            self.load_playlist(int(key[4]))
        else:
            logger.info('Received unbinded key: %s', key)


if __name__ == '__main__':
    user = subprocess.getoutput('whoami')
    if user != USER:
        # switch from root to requested user
        print('Using user %s.' % USER)
        from django_web_utils.system_utils import run_as
        run_as(USER)

    daemon = MopidyController(sys.argv)
    daemon.start()
