from django.db import models

from user_app.models.meta import Meta


class Permission(models.Model):
    label = models.CharField(max_length=30)
    index = models.SmallIntegerField(unique=True)

    class Meta:
        db_table = 'back_permission'


def check_permission(user, label, permission):
    try:
        user_permission = Meta.objects.get(user_id=user.id, meta_key='admin_permission').meta_value
        index = Permission.objects.get(label=label).index

        item_permission = int(user_permission[index - 1:index], 16)

        if permission == 'read' and item_permission & 8 > 0:
            return True
        if permission == 'update' and item_permission & 4 > 0:
            return True
        if permission == 'create' and item_permission & 2 > 0:
            return True
        if permission == 'delete' and item_permission & 1 > 0:
            return True

    except:
        pass

    return False
