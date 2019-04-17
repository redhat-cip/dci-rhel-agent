from collections import deque

queue = deque([])


def flush():
    while len(queue) > 0:
        next_task = queue.popleft()
        next_task()


def asap(task):
    queue.append(task)
    flush()


def parallel(tasks):
    for task in tasks:
        queue.append(task)
    flush()
