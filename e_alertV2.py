#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 08 16:43:56 2019

__author__ = "Ram Kodialbail"
__copyright__ = "Ram Kodialbail, All rights reserved"
__credits__ = []
__license__ = ""
__version__ = "2.0"
__maintainer__ = "Ram Kodialbail"
__email__ = "ramk@netapp.com"
__status__ = "Prototype"

"""

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import yaml
import sys
import socket
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import logging.handlers

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

if (sys.platform != 'linux'):
        print('I have been groomed to run only on Linux. Gotta quit, Sorry!!')
        sys.exit(1)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
formatter = logging.Formatter('%(module)s.%(funcName)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def sendMail(error):
    message = MIMEMultipart()
    mailfrom = "e-series.monitor@mySANtricityProxy.mydomain.com"
    mailto = ["IT.manager@mydomain.com", "IT.Operationse@mydomain.com"]

    message['To'] = ", ".join(mailto)
    message['From'] = mailfrom
    message['subject'] = "Daily e-series fault report"
    msg1 = "*** DO NOT REPLY *** \n\n"
    #msg = msg1 + '\n'.join(error)
    msg = msg1 + error
    message.attach(MIMEText(msg, 'plain'))
    try:
        server = smtplib.SMTP('mail.mydomain.com')
        server.sendmail(mailfrom, mailto, message.as_string())
    except Exception as e:
        print("Unable to send email: ", e)
    finally:
        server.quit()


def get_request(url):
    # headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    try:
        req = session.get(url, headers=headers)
        req.raise_for_status()
        return req.json()
    except requests.exceptions.HTTPError as err:
        logger.info(err)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logger.info(e)
        sys.exit(1)


def post_request(url, data):
    # headers = {'Content-Type': 'application/json', 'Accept': '*/*'}
    try:
        post_result = session.post(url, headers=headers, data = json.dumps(data))
        post_result.raise_for_status()
        if (post_result.status_code == 201):
            logger.info('Storage-system added successfully')
        elif (post_result.status_code == 422):
            logger.info('Could not connect to storage system')
        return post_result.json()
    except requests.exceptions.HTTPError as err:
        logger.info(err)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logger.info(e)
        sys.exit(1)


try:
    with open("/sod/app/scripts/system/config.yml", 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
except IOError:
    cfg = ''
    pass

if cfg:
    skip_array = cfg['suppress'].split()
else:
    skip_array = []

#server_root_url = 'https://mySANtricityProxy.mydomain.com:8443'
server_root_url = ''

auth = ('ro', 'ro')

if not (server_root_url, auth):
    print('server_root_url or auth is not set!')
    sys.exit(1)

session = requests.Session()
session.verify = False
session.auth = auth
headers = {'Content-Type': 'application/json', 'Accept': '*/*'}


api_version = 2
api_path = '/devmgr/v{version}'.format(version=api_version)
base_url = server_root_url + api_path
storage_url = base_url + '/storage-systems'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
session.get(storage_url)


def main():
    error = ""
    arrays_data = get_request(storage_url)
    if not arrays_data:
        arrays_in_repo = []
    else:
        arrays_in_repo = [ (each['name'], each['id'], each['status'], each['ip1'], each['ip2'], each['wwn']) for each in arrays_data]
    for a in arrays_in_repo:
        if a[2] != 'optimal':
            if not a[0]:
                e_name = socket.getfqdn(a[3])
            else:
                e_name = a[0]
            if e_name in skip_array:
                continue
            if a[2] == 'offline':
                failures = "offline"
            else:
                try:
                    failures =get_request(storage_url + '/' + a[1] + '/failures?details=false')
                except:
                    failures = "offline"
            error += "********************************\n"
            error += "\n" + e_name + "\t" + socket.getfqdn(a[3]) + "\n"  
            if failures == "offline":
                #print("\t", "Device is offline")
                error += "\t" + "Device is offline" + "\n"
            else:
                for f in failures:
                    #print("\t", f['failureType'])
                    error += "\t" + f['failureType'] + "\n"

    if error:
        sendMail(error)


if (__name__ == "__main__"):
    main()
