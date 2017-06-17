from uuid import uuid5, NAMESPACE_DNS
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from c3os import conf


class Region(conf.Base):
    """Region object

    Args:
        name (str): Region name
        uuid (:obj:`str`, optional): Region name
    """

    __tablename__ = 'regions'

    uuid = Column(String, primary_key=True)
    name = Column(String)
    instances = relationship("Instance", collection_class=set, lazy='subquery')
    have_instance_ids = set()

    def __init__(self, name, uuid=None):
        if uuid is None:
            self.uuid = uuid5(NAMESPACE_DNS, name).hex
        else:
            self.uuid = uuid
        self.name = name

    @property
    def instance_list(self):
        """ The instance Region has. """
        return self.instances

    def add_instance(self, instance):
        """ Adding an instance """
        if instance.id not in self.have_instance_ids:
            self.have_instance_ids.add(instance.id)
            self.instances.add(instance)

    def search_instance(self, _id):
        """ Searching for instance """
        for ins in self.instances:
            if _id == ins.id:
                return ins

    @classmethod
    def create_from_db(cls, db_pool, name, *args, **kwargs):
        """An object is made from DB.

        When an object of id is in DB already, that's returned.
        It's generated besides that.

        Args:
            db_pool (DBPool): DBPool instance.
            name (str): Region name.
        """
        region = db_pool.search(cls, 'name', name)
        if region:
            return region
        else:
            return cls(name, *args, **kwargs)
