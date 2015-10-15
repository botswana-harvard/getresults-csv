

class DmisRouter(object):

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label == 'dmis_models':
            return 'dmis'
        else:
            return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'dmis_models':
            return False
        else:
            return 'default'

    def allow_migrate(self, db, model):
        if db == 'dmis':
            return False
        elif model._meta.app_label == 'dmis_models':
            return False
        else:
            return True
#         try:
#             if model.do_not_migrate:
#                 return False
#         except AttributeError:
#             return True
