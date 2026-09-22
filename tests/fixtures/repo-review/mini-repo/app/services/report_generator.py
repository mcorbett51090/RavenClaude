"""Generates a summary report of tasks, cross-referenced against a list of
VIP owners who should be called out specially in the output.
"""


def build_vip_report(tasks, vip_owners: list):
    """Return the subset of tasks belonging to a VIP owner.

    `tasks` can be tens of thousands of rows and `vip_owners` is passed in
    as a plain list (e.g. loaded straight from a config file), so this does
    a linear `in` scan of vip_owners for every single task instead of
    converting vip_owners to a set once up front -- O(len(tasks) *
    len(vip_owners)) instead of O(len(tasks)).
    """
    vip_tasks = []
    for task in tasks:
        if task.owner in vip_owners:
            vip_tasks.append(task)
    return vip_tasks
