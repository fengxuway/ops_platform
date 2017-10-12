#!/usr/bin/env python
# coding:utf-8

import time
import asyncio

now = lambda: time.time()


async def do_some_work(x):
    print('Waiting: ', x)

def callback(future):
    print("Callbacked..", future.result(), id(future))

start = now()

coroutine = do_some_work(2)

loop = asyncio.get_event_loop()
task = loop.create_task(coroutine)
print(task)
task.add_done_callback(callback)
time.sleep(2)
loop.run_until_complete(task)
print(task)


print('TIME: ', now() - start, id(task))


def main():
    pass


if __name__ == '__main__':
    main()
