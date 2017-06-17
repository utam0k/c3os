import json
import time
import pika
import multiprocessing as mp
from uuid import UUID

import c3os.db as db
from c3os.objects.region import Region
from c3os.objects.instance import Instance
from c3os import utils
from c3os import client
from c3os import conf
from c3os import messaging
from c3os.cntl.type import CNTLTYPE

CONF = conf.CONF


def start():
    """ Starting monitor. """
    mp.Process(target=monitor).start()


def monitor():
    """ Monitor main routine.

    1. Information on its Regio is registered with DB.
    2. A finite difference of DB with CloudOS is lost.
    3. The state of the instance written on a setting file is checked.

    Attributes:
        nova (novaclient.client.Client): Nova client.
        own_region (str): The name of the Region.
    """
    nova = utils.connection_nova()
    own_region = Region(CONF['os_info']['REGION_NAME'])
    db.pool.add(own_region)
    db.pool.commit()
    own_region_register(nova, db.pool, own_region)

    while True:
        exist_instance_uuids = [
            instance.id for instance in nova.servers.list()]
        exist_ids = [utils.generate_id(uuid, own_region.uuid)
                     for uuid in exist_instance_uuids]
        utils.clear_database(db.pool, exist_ids)

        own_region_register(nova, db.pool, own_region)

        check_alive_monitor_instance(nova, db.pool)
        db.pool.commit()
        time.sleep(3.0)

        utils.write_log(
            '\n' + time.strftime("%d %b %H:%M:%S", time.localtime()))
        utils.write_log(
            '\n' + json.dumps(utils.to_dict(db.pool), indent=2) + '\n')
        print(time.strftime("%d %b %H:%M:%S", time.localtime()))
        print(json.dumps(utils.to_dict(db.pool), indent=2), '\n')


def own_region_register(nova, db_pool, own_region):
    """ The instance one is managing is registered with DB. 

    Args:
        nova (novaclient.client.Client): Nova client.
        db_pool (DBPool): DBPool instance.
        own_region (Region): Region one is manging.
    """
    nova = utils.connection_nova()
    migrated_instances = [db_pool.search(Instance, 'migrated_org_hint', monitor_ins_id)
                          for monitor_ins_id in CONF['instances'].values()]
    migrated_instance_uuids = [str(UUID(instance.os_uuid))
                               for instance in migrated_instances if instance is not None]
    for s in nova.servers.list():
        all_addresses = utils.conver_addresses(s)
        if s.id in migrated_instance_uuids:
            for migrated_instance in migrated_instances:
                if migrated_instance is not None and s.id == str(UUID(migrated_instance.os_uuid)):
                    instance = migrated_instance
                    instance = Instance.create_from_db(
                        db_pool, instance.id, s.status, all_addresses, name=s.name)
        else:
            id = utils.generate_id(s.id, own_region.uuid)
            instance = Instance.create_from_db(
                db.pool, id, s.status, all_addresses, name=s.name)
        own_region.add_instance(instance)
        db_pool.add(instance)


def check_alive_monitor_instance(nova, db_pool):
    """ It's monitor whether an instance lives.

    Args:
        nova (novaclient.client.Client): Nova client.
        db_pool (DBPool): DBPool instance.
    """

    generated_instances = {instance.migrated_org_hint for instance in db_pool.all(
        Instance) if instance.migrated_org_hint != None}
    for instance_name, monitor_ins_id in CONF['instances'].items():
        if not utils.is_active_instance(monitor_ins_id, db_pool, "addresses"):
            migrated_ids = [instance.migrated_org_hint for instance in db_pool.all(
                Instance) if instance.migrated_org_hint != None]
            if monitor_ins_id not in migrated_ids and monitor_ins_id not in generated_instances:
                generated_instances.add(monitor_ins_id)

                body = {}
                body['name'] = instance_name
                body['migrated_org_hint'] = monitor_ins_id
                data = json.dumps(
                    {'type': CNTLTYPE.CREATE_INSTANCE, 'body': body})
                messaging.publish(body=data)
        elif monitor_ins_id in generated_instances:
            instance = db_pool.search(
                Instance, 'migrated_org_hint', monitor_ins_id)
            if instance is not None and instance.status == 'ACTIVE':
                generated_instances.remove(monitor_ins_id)
                body = {}
                body['colum'] = 'migrated_org_hint'
                body['value'] = monitor_ins_id
                data = json.dumps(
                    {'type': CNTLTYPE.DELETE_INSTANCE, 'body': body})
                messaging.publish(body=data)
                utils.write_log('delete' + instance.name)
