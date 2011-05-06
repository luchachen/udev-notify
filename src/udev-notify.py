#!/usr/bin/env python
import os
import sys
import pynotify
import pyudev
import locale
import gettext
import re
from copy import deepcopy
from optparse import OptionParser

APP = 'udev-notify'
DIR = '/usr/share/locale/'

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

parser = OptionParser()
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help=_("Display verbose output on STDOUT"))
(arguments, args) = parser.parse_args()
VERBOSE = arguments.verbose

# register to libnotify
if not pynotify.init("new-hardware"):
    print _("Cannot initialize libnotify")
    sys.exit(1)

devices = [
    {
        'type': _('CD-ROM Drive'),
        'icon': 'media-optical',
        'detection': {
            'DEVTYPE': 'disk',
            'ID_TYPE': 'cd',
            'SUBSYSTEM': 'block' 
        }
    },
    {
        'type': _('Multimedia Player'), #this must be BEFORE generic storage and USB devices
        'icon': 'multimedia-player',
        'detection': {
            'DEVTYPE':'usb_device',
            'SUBSYSTEM': 'usb',
            'ID_MEDIA_PLAYER': '*',
        }
    },
    
    #{
    #    'type': _('Disk Partition'),
    #    'icon': 'drive-removable-media',
    #    'detection': {
    #        'DEVTYPE':'partition',
    #        'ID_FS_USAGE':'filesystem',
    #        'ID_TYPE':'disk',
    #        'SUBSYSTEM':'block'
    #    }
    #},
    {
        'type': _('USB Storage Device'), # MemoryStick
        'icon': 'gnome-dev-media-ms',
        'detection': {
            'DEVTYPE':'disk',
            'ID_TYPE':'disk',
            'SUBSYSTEM':'block',
            'ID_BUS': 'usb',
            'ID_DRIVE_FLASH_MS' : '1'
        }
    },
            
    {
        'type': _('USB Storage Device'), #SmartMedia
        'icon': 'gnome-dev-media-sm',
        'detection': {
            'DEVTYPE':'disk',
            'ID_TYPE':'disk',
            'SUBSYSTEM':'block',
            'ID_BUS': 'usb',
            'ID_DRIVE_FLASH_SM' : '1'
        }
    },
    {
        'type': _('USB Storage Device'), #CompatFlash
        'icon': 'gnome-dev-media-cf',
        'detection': {
            'DEVTYPE':'disk',
            'ID_TYPE':'disk',
            'SUBSYSTEM':'block',
            'ID_BUS': 'usb',
            'ID_DRIVE_FLASH_CF' : '1'
        }
    },      
    {
        'type': _('SD/MMC Memory'), #SD Card
        'icon': 'gnome-dev-media-sdmmc',
        'detection': {
            'SUBSYSTEM':'mmc'
        }
    },          
          
    {
        'type': _('USB Storage Device'), #SD Card
        'icon': 'gnome-dev-media-sdmmc',
        'detection': {
            'DEVTYPE':'disk',
            'ID_TYPE':'disk',
            'SUBSYSTEM':'block',
            'ID_BUS': 'usb',
            'ID_DRIVE_FLASH_SD' : '1'
        }
    },          
          
    {
        'type': _('USB Storage Device'),
        'icon': 'drive-removable-media',
        'detection': {
            'DEVTYPE':'disk',
            'ID_TYPE':'disk',
            'SUBSYSTEM':'block',
            'ID_BUS': 'usb'
        }
    },
    {
        'type': _('WiFi Device'),
        'icon': 'network-wireless',
        'detection': {
            'DEVTYPE':'wlan',
            'SUBSYSTEM': 'net'
        }
    },
    {
        'type': _('WebCam / TV Tuner'),
        'icon': 'camera-web',
        'detection': {
            'SUBSYSTEM': 'video4linux'
        }
    },
    {
        'type': _('Mouse'),
        'icon': 'mouse',
        'detection': {
            'ID_INPUT_MOUSE': '1',
            'ID_TYPE': 'hid',
            'SUBSYSTEM': 'input'
        }
    },
    {
        'type': _('Game Controller'),
        'icon': 'joystick',
        'detection': {
            'ID_INPUT_JOYSTICK': '1',
            'ID_TYPE': 'hid',
            'SUBSYSTEM': 'input'
        }
    },
    {
        'type': _('Sound Card'), # needs testing
        'icon': 'sound',
        'detection': {
            'ID_TYPE': 'sound',
            'SUBSYSTEM': 'sound'
        }
    },
    
    {
        'type': _('USB Modem'),
        'icon': 'modem',
        'detection': {
            'ID_BUS':'usb',
            'SUBSYSTEM': 'tty',
        }
    },
    {
        'type': _('Modem'),
        'icon': 'modem',
        'detection': {
            'ID_USB_DRIVER': 'cdc_acm',
            'SUBSYSTEM': 'tty'
        }
    },
    {
        'type': _('PDA Device'),
        'icon': 'pda',
        'detection': {
            'ID_USB_DRIVER': 'ipaq',
            'SUBSYSTEM': 'tty'
        }
    },    
    {
        'type': _('Keyboard'),
        'icon': 'mouse',
        'detection': {
            'ID_CLASS': 'kbd',
            'ID_TYPE': 'hid',
            'SUBSYSTEM': 'input'
        }
    },
    
    {
        'type': _('Digital Camera'),
        'icon': 'camera-photo',
        'detection': {
            'DEVTYPE':'usb_device',
            'ID_GPHOTO2': '1',
        }
    },    
    {
        'type': _('Network Device'),
        'icon': 'network-wired',
        'detection': {
            'ID_BUS':'pci',
            'SUBSYSTEM': 'net',
        }
    },
    {
        'type': _('USB Network Device'),
        'icon': 'network-wired',
        'detection': {
            'ID_BUS':'usb',
            'SUBSYSTEM': 'net',
        }
    },
    {
        'type': _('USB Device'),
        'icon': 'gnome-dev-unknown-usb',
        'detection': {
            'DEVTYPE':'usb_device',
            'SUBSYSTEM': 'usb',
        }
    },
]

def cleanstr_cb(m):
    return unichr(int(eval('0'+m.group(1))))

def cleanstr(text):
    return re.sub(r'\\(x(\d{2}))', cleanstr_cb, text).encode('utf-8').strip()

def detect_device(device):
    if VERBOSE:
        for i in device:
            print i, device[i]
        print "-------------"

    for d in devices:
        d['name'] = ''
        detected = False  
        keys = d['detection'].keys()
        for k in keys:
            if k in device:
                if device[k] == d['detection'][k] or d['detection'][k] == '*':
                    detected = True
                else:
                    detected = False
                    break
            else:
                detected = False
                break
        if detected:
            result = deepcopy(d)
            
            if 'UDISKS_PRESENTATION_ICON_NAME' in device:
                result['icon'] = device['UDISKS_PRESENTATION_ICON_NAME']
            else:
                result['icon'] = result['icon']
            
            device_name = ''
            
            if 'ID_VENDOR_FROM_DATABASE' in device:
                device_name += device['ID_VENDOR_FROM_DATABASE'].strip()
            
            if 'ID_MODEL_FROM_DATABASE' in device:
                if device_name:
                    device_name += ' '
                device_name += device['ID_MODEL_FROM_DATABASE'].strip()
            
            if device_name == '' and 'ID_MODEL_ENC' in device and 'ID_VENDOR_ENC' in device:
                device_name += cleanstr(device['ID_VENDOR_ENC']) + ' '
                device_name += cleanstr(device['ID_MODEL_ENC'])
            
            if device_name == '' and 'ID_V4L_PRODUCT' in device:
                device_name = cleanstr(device['ID_V4L_PRODUCT'])
            
            if 'ID_FS_LABEL' in device and 'ID_FS_TYPE' in device:
                device_name = '%s (%s)' % (device['ID_FS_LABEL'], device['ID_FS_TYPE'])
            
            if device_name != '':
                 result['name'] = result['type'] + '\n' + device_name
            else:
                result['name'] = result['type']
            return result
        else:
            continue

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)

notification = None
for action, device in monitor:
    detected = detect_device(device)
    if detected != None:
        if device['ACTION'] == 'add':
            if notification == None:
                notification = pynotify.Notification(
                    _('Device recognized')
                    , detected['name']
                    , detected['icon']
                )
            else:
                notification.update(
                    _('Device recognized')
                    , detected['name']
                    , detected['icon']
                )
            notification.show()    
        elif device['ACTION'] == 'remove':
            if notification == None:
                notification = pynotify.Notification(
                    _('Device removed')
                    , detected['name']
                    , detected['icon']
                )
            else:
                notification.update(
                    _('Device removed')
                    , detected['name']
                    , detected['icon']
                )
            notification.show() 
    notification = None  
sys.exit(0)

# TODO: printer, scanner, ??

