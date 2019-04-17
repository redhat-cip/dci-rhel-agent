from scheduler import asap, parallel


def test_scheduler_exec_tasks_in_order():
    queue = []

    def one():
        queue.append("1")

    def two():
        queue.append("2")

    def three():
        queue.append("3")

    asap(one)
    asap(two)
    asap(three)

    assert queue == ["1", "2", "3"]


def test_scheduler_exec_nested_tasks_in_order():
    queue = []

    def two():
        queue.append("2")

    def three():
        queue.append("3")

    def one():
        queue.append("1")
        asap(two)
        asap(three)

    asap(one)

    assert queue == ["1", "2", "3"]


def test_scheduler_exec_tasks_in_parallel():
    queue = []

    def three():
        queue.append("3")

    def one():
        queue.append("1")
        asap(three)

    def two():
        queue.append("2")

    parallel([one, two])

    assert queue == ["1", "2", "3"]

