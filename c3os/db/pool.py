import time
import functools


class DBPool(object):
    """ A pool just before DB.

    Args:
        session (sqlalchemy.orm.session.Session): DB session.
        clses (pool): The ranges with which a pool is made.
    """

    def __init__(self, session, clses):
        self.session = session
        self.__all_pool_cls = clses
        try:
            getattr(DBPool, "locked")
        except:
            DBPool.locked = False

        for cls in clses:
            try:
                getattr(DBPool, cls.__name__.lower() + '_pool')
            except:
                setattr(DBPool, cls.__name__.lower() + '_pool', set())

    def wait_unlock(func):
        """ Waiting until lock releases. """
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            while True:
                if not self.is_locked():
                    return func(self, *args, **kwargs)
                time.sleep(0.05)
        return wrapper

    def db_occupy(func):
        """ DB is occupied. """
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            self.lock()
            result = func(self, *args, **kwargs)
            self.unlock()
            return result
        return wrapper

    def retry_session_rock(func):
        """ Retrying at an error. """
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            while True:
                try:
                    result = func(self, *args, **kwargs)
                    return result
                except:
                    print(func, 'failed')
                    return
        return wrapper

    def lock(self):
        """ DB is locked. """
        DBPool.id = id(self)
        DBPool.locked = True

    def unlock(self):
        """ DB is unlocked. """
        DBPool.locked = False
        DBPool.id = None

    def is_locked(self):
        """ Is DB locked

        Returns:
            bool: If True, DB is locked.
        """
        if not DBPool.locked:
            return False
        else:
            if id(self) == DBPool.id:
                return False
            else:
                return True

    @wait_unlock
    def get_pool(self, cls):
        """ Pool getter.

        Args:
            cls (cls): Class in the pool you want.
        Returns:
            set
        Examples:
            >>> db_pool.get_pool(Region)
            {Region1Instance, Region2Instance}
        """
        return getattr(DBPool, cls.__name__.lower() + '_pool')

    @db_occupy
    def get_all_pool(self):
        """ All pool getter.

        Returns:
            set
        """
        ret = set()
        for cls in self.__all_pool_cls:
            for obj in self.get_pool(cls):
                ret.add(obj)
        return ret

    @retry_session_rock
    def all(self, cls):
        """ All db Infomation and all pool getter.

        Args:
            cls (cls): Class in the pool you want.
        Returns:
            set
        """
        ret = set()
        ret = ret.union(self.get_pool(cls))
        ret = ret.union(self.session.query(cls).all())
        return ret

    @wait_unlock
    def add(self, obj):
        """ An object is added to the pool.

        Args:
            obj (ClassInstance): Class in the pool you want.
        """
        pool = self.get_pool(obj.__class__)
        pool.add(obj)

    def clear_pool(self):
        """ A pool is clear. """
        for cls in self.__all_pool_cls:
            self.get_pool(cls).clear()

    @db_occupy
    @wait_unlock
    @retry_session_rock
    def commit(self):
        """ DB is renewed actually. """
        for obj in self.get_all_pool():
            self.session.merge(obj)
        self.session.commit()
        self.clear_pool()

    @retry_session_rock
    def search(self, cls, colum, compare, first=True):
        """ Searching for an object.

        Args:
            cls (cls): Class in the pool you want.
            colum (str): The column for which you search.
            compare (str): The value for which you search.
            first (:obj:`bool`, optional): If Treu, it's returned at the beginning of the search result.
        Returns:
            obj or list: Search result.
        """
        pool = self.get_pool(cls)
        ret = set()
        for obj in pool.copy():
            item = getattr(obj, colum)

            if colum is "addresses":
                is_in = item in compare
            else:
                is_in = item == compare

            if is_in:
                if first:
                    return obj
                else:
                    ret.add(obj)
        if first:
            return self.session.query(cls).filter_by(**{colum: compare}).first()
        else:
            [ret.add(obj) for obj in self.session.query(
                cls).filter_by(**{colum: compare}).all()]
        return ret

    @db_occupy
    def delete(self, cls, colum, compare):
        """ Deleteing an object.

        Args:
            cls (cls): Class in the pool you want.
            colum (str): The column for which you want delete.
            compare (str): The value for which you want delete.
        """
        obj = self.search(cls, colum, compare)
        pool = self.get_pool(cls)
        if obj in pool.copy():
            pool.remove(obj)
        current_session = self.session.object_session(obj)
        if obj is None or current_session is None:
            return
        current_session.delete(obj)
