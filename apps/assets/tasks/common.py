# -*- coding: utf-8 -*-
#

from celery import shared_task

from orgs.utils import tmp_to_root_org
from assets.models import AuthBook

__all__ = ['add_nodes_assets_to_system_users']


@shared_task
@tmp_to_root_org()
def add_nodes_assets_to_system_users(nodes_keys, system_users):
    from ..models import Node
    nodes = Node.objects.filter(key__in=nodes_keys)
    assets = Node.get_nodes_all_assets(*nodes)
    for system_user in system_users:
        """ 解决资产和节点进行关联时，已经关联过的节点不会触发 authbook post_save 信号， 
        无法更新节点下所有资产的管理用户的问题 """
        for asset in assets:
            defaults = {'asset': asset, 'systemuser': system_user, 'org_id': asset.org_id}
            instance, created = AuthBook.objects.update_or_create(
                defaults=defaults, asset=asset, systemuser=system_user
            )
            # 只要关联都需要更新资产的管理用户
            instance.update_asset_admin_user_if_need()
