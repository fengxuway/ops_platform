#!/usr/bin/env python
# coding:utf-8
from celery.task import task
from service.logic import run_task


class Tasks(object):
    def __init__(self, inventory, module_name='command', module_args='', pattern='all'):
        self.inventory = inventory
        self.module_name = module_name
        self.module_args = module_args
        self.pattern = pattern

    def __unicode__(self):
        return str(self.inventory) + self.module_args

@task
def run_multi_tasks(tasks):
    print(type(tasks))
    print(tasks)
    result = []
    for i in tasks:
        print(i, type(i))
        result.append(run_task(i.inventory, i.module_name, i.module_args, i.pattern))
    return result


def main():
    pass


if __name__ == '__main__':
    main()
