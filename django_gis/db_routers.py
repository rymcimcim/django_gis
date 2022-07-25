import logging
import random

from django.db import connections
from django.db.utils import OperationalError
from django.utils.connection import ConnectionDoesNotExist

logger = logging.getLogger(__name__)

class PrimaryReplicaRouter:

    @property
    def db_alias(self):
        try:
            connections['primary'].ensure_connection()
        except (ConnectionDoesNotExist, OperationalError):
            ret = 'replica'
            logger.warning('Using replica database!')
        else:
            ret = 'primary'
        return ret

    def db_for_read(self, model, **hints):
        """
        Reads go to a randomly-chosen instance.
        """
        return random.choice((self.db_alias, 'replica'))

    def db_for_write(self, model, **hints):
        """
        Writes always go to primary.
        """
        return self.db_alias

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the primary/replica pool.
        """
        db_set = {'primary', 'replica'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All non-auth models end up in this pool.
        """
        return True
