from lego.apps.users.constants import CO_LEADER, LEADER, MEMBER, TREASURER

"""
This sets group owners as gsuite group owners.
Should group owners manage their gsuite groups, or should they be managed by webkom?
"""

GSUITE_ROLE_MAPPINGS = {
    MEMBER: 'MEMBER',
    LEADER: 'OWNER',
    CO_LEADER: 'MANAGER',
    TREASURER: 'MANAGER'
}
