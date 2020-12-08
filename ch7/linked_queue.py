class Empty(Exception):
    """尝试对空队列进行删除操作时抛出的异常"""
    pass


class _Node:
    """节点类"""

    def __init__(self, element, next=None):
        """
        :param element: 节点代表的对象元素
        :param next: 节点对象中用于指向下一个节点的实例属性
        """
        self.element = element
        self.next = next


class LinkedQueue:
    """使用单链表保存对象元素实现的队列数据结构"""
    def __init__(self):
        """创建一个空队列"""
        self._head = None  # 初始化头节点
        self._tail = None  # 初始化尾节点
        self._size = 0  # 队列元素个数

    def __len__(self):
        """
        返回队列中的元素个数
        :return: 元素个数
        """
        return self._size

    def is_empty(self):
        """
        如果队列为空则返回True
        :return: 队列是否为空的状态
        """
        return self._size == 0

    def first(self):
        """
        返回但不删除队头元素
        :return: 队头元素
        """
        if self.is_empty():
            raise Empty('当前队列为空！')
        return self._head.element

    def enqueue(self, element):
        """
        向队列尾部插入对象元素
        :param element: 待插入队列尾部的对象元素
        :return: None
        """
        node = _Node(element)
        if self.is_empty():
            self._head = node
        else:
            self._tail.next = node
        self._tail = node  # 使新入队尾的元素成为尾节点
        self._size += 1

    def dequeue(self):
        """
        删除并返回队头的节点，并返回其中的对象元素，如此时队列为空则抛出异常
        :return: 队头节点的element域
        """
        if self.is_empty():
            raise Empty('队列为空！')
        ans = self._head.element
        self._head = self._head.next
        self._size -= 1
        if self.is_empty():  # 如果执行本次出对操作时队列中仅有一个节点，则此时该节点同时也是尾节点，需对此做处理
            self._tail = None
        return ans
