from uuid import UUID
import threading
from novaclient import client

from c3os.objects.instance import Instance
from c3os.conf import UUID_LEN
from c3os.objects.region import Region
from c3os import conf

CONF = conf.CONF
log_f = open(CONF['os_info']['REGION_NAME'] + '.log', 'w')


def clear_database(db_pool, exist_ids, is_own=True):
    """ Real friction is put out with DB. """
    region_uuid = exist_ids[0][UUID_LEN:UUID_LEN * 2]
    db_ids = [instance.id for instance in db_pool.all(Instance)
              if instance.region_uuid == region_uuid]
    diff = set(db_ids) - set(exist_ids)
    for id in diff:
        if is_own:
            if id[:UUID_LEN] == id[UUID_LEN:UUID_LEN * 2]:
                db_pool.delete(Instance, 'id', id)
        else:
            db_pool.delete(Instance, 'id', id)


def generate_id(os_uuid, region_uuid, birth_region_uuid=None):
    """ Generating id. 

    Args:
        os_uuid (str): UUID made with Cloud OS.
        region_uuid (str): Region UUID.
        birth_region (:obj:`str`, optional): UUID in original Region.
    """
    if birth_region_uuid is None:
        birth_region_uuid = region_uuid
    birth_region_uuid = UUID(birth_region_uuid).hex
    region_uuid = UUID(region_uuid).hex
    os_uuid = UUID(os_uuid).hex
    _id = birth_region_uuid + region_uuid + os_uuid
    return _id


def start_thread(method):
    """ Starting thread. 
    
    Args:
        method (method): Threading target method.
    """
    t = threading.Thread(target=method)
    t.setDaemon(True)
    t.start()


def to_dict(db_pool):
    """ The data of DB is made dict. 

    Args:
        db_pool (DBPool): DBPool instance.
    Returns:
        dict
    """
    ret_dict = {}
    for region in db_pool.all(Region):
        ret_dict[region.name] = [ins.to_dict() for ins in region.instance_list]
    return ret_dict


def is_active_instance(searched_value, db_pool, colum="id"):
    """ An instance checks whether it's valid. 

    Args:
        searched_value (str or int): The value searched for.
        db_pool (DBPool): DBPool instance.
        colum (:obj:`str`, optional): The colum searched for.
    Returns:
        bool
    """
    instance = db_pool.search(Instance, colum, searched_value)
    if instance is not None and instance.status == "ACTIVE":
        return True
    else:
        return False


def connection_nova():
    """ Connection to Nove. 
    
    Returns:
        novaclient.client.Client()
    """
    nova_auth = {}
    nova_auth['username'] = CONF['auth']['USERNAME']
    nova_auth['password'] = CONF['auth']['PASSWORD']
    nova_auth['auth_url'] = CONF['auth']['AUTH_URL']
    nova_auth['project_id'] = CONF['auth']['TENANT_NAME']
    nova_auth['region_name'] = CONF['auth']['REGION_NAME']
    return client.Client(2, **nova_auth)


def conver_addresses(s):
    """ Making a list of the address.

    Args:
        s (novaclient.v2.servers.Server): Clout OS instance.
    Returns:
        list
    Examples:
        >>> utils.conver_addresses(instance)
        ["192.168.12.2", "192.168.12.3"]
    """
    all_addresses = str()
    for addres in s.networks.values():
        for addr in addres:
            if all_addresses == str():
                all_addresses = addr
            else:
                all_addresses += ",", addr

    return all_addresses


def write_log(str):
    """ Writing the log. """
    log_f.write(str + '\n')
