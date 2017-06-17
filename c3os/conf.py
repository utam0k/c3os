import configparser
from uuid import uuid5, NAMESPACE_DNS
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

CONF = configparser.ConfigParser()
CONF.read('./config.ini')
UUID_LEN = 32
OWN_REGION_UUID = uuid5(NAMESPACE_DNS, CONF['os_info']['REGION_NAME']).hex
