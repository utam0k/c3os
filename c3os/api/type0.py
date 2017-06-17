import ast

from c3os.objects.instance import Instance
from c3os.objects.region import Region
from c3os import db
from c3os import utils
from c3os import conf

UUID_LEN = conf.UUID_LEN
registed_regions = {}


def execute(db_pool, body):
    """API type 0 execute.

    Args:
        db_pool (DBPool): DBPool class.
        body (str): Instances infomation.
    Returns:
        str: If return value is True, this request is succeed.
    """

    regions, divi_region_instances = parse_message(body, db_pool)

    for region in regions:
        utils.clear_database(
            db_pool, [instance.id for instance in divi_region_instances[region.name]], is_own=False)

    add_db(db_pool, regions, divi_region_instances)
    db_pool.commit()

    return str(True)


def parse_message(message, db_pool):
    """Parse message

    Args:
        message (str): Instances infomation.
        db_pool (DBPool): DBPool class.
    Returns:
        list, dict: Region list and instances per Region.
    """

    message = ast.literal_eval(message)
    divi_region_instances = dict()
    regions = set()
    region_names = {region_name for region_name in message.keys()}
    for region_name in region_names:
        instances = set()
        # TODO: nothing instance
        try:
            region_uuid = message[region_name][0]['id'][UUID_LEN:UUID_LEN * 2]
        except:
            continue

        if region_name not in registed_regions.keys():
            region = Region.create_from_db(db_pool, region_name, region_uuid)
            registed_regions[region_name] = region
        else:
            region = registed_regions[region_name]

        regions.add(region)

        for ins_info in message[region_name]:
            instance = Instance.create_from_db(db_pool, **ins_info)
            instances.add(instance)
        divi_region_instances[region_name] = instances

    return regions, divi_region_instances


def add_db(db_pool, regions, divi_region_instances):
    """Add db 

    Args:
        db_pool (DBPool): DBPool class.
        regions (list): Regions list.
        divi_region_instances (dict): Instances per Region.
    Returns:
        None
    """
    for region in regions:
        db_pool.add(region)

        for instance in divi_region_instances[region.name]:
            db_pool.add(instance)
            region.add_instance(instance)
        db_pool.commit()
