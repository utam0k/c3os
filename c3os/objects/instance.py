from enum import IntEnum
from sqlalchemy import Column, String, ForeignKey


from c3os import conf
from c3os.conf import UUID_LEN


class Instance(conf.Base):
    """Instance object

    Args:
        id (str): Instance id
        status (str): Instance status
        addressed (list): Have addresses
        name (:obj:`str`, optional): Instance name
        migrated_org_hint (:obj:`str`, optional): The hint which specifies an instance before migrate.
    """
    __tablename__ = 'instances'

    id = Column(String, primary_key=True)
    name = Column(String)
    status = Column(String)
    addresses = Column(String)
    region_uuid = Column(String, ForeignKey('regions.uuid'))
    migrated_org_hint = Column(String, nullable=True)

    def __init__(self, id, status, addresses, name=None, migrated_org_hint=None):
        self.id = id
        self.status = status
        self.name = name
        self.addresses = addresses
        self.region_uuid = id[UUID_LEN:UUID_LEN * 2]
        if migrated_org_hint is not None:
            self.migrated_org_hint = migrated_org_hint

    @classmethod
    def create_from_db(cls, db_pool, id, *args, **kwargs):
        """An object is made from DB.

        When an object of id is in DB already, that's returned.
        It's generated besides that.

        Args:
            db_pool (DBPool): DBPool instance.
            id (str): Instance id.
        """
        instance = db_pool.search(cls, 'id', id)
        if instance:
            instance.__init__(id, *args, **kwargs)
            return instance
        else:
            return cls(id, *args, **kwargs)

    def to_dict(self):
        """ Instance infomation to dict. """
        ret_dict = {}
        ret_dict['id'] = self.id
        ret_dict['status'] = self.status
        ret_dict['name'] = self.name
        ret_dict['addresses'] = self.addresses
        return ret_dict

    @property
    def get_address_list(self):
        """ Address list getter. 

        Returns:
            list: Address list.
        """
        return self.addresses.split(",")

    @property
    def os_uuid(self):
        """ Cloud os uuid getter. """
        return self.id[UUID_LEN * 2:UUID_LEN * 3]

    @property
    def birth_region_uuid(self):
        """ UUID of the Cloud OS which is originally. """
        return self.id[:UUID_LEN]


class Status(IntEnum):
    """ Instance status. """
    ACTIVE = 0
    SHUTOFF = 1
    PAUSED = 2
    SUSPENDED = 3
    RESCUED = 4
    STOPPED = 5
    SOFTDELETED = 6
    ERROR = 7
