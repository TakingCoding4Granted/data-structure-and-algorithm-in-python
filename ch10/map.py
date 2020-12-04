from abc import abstractmethod
from collections.abc import MutableMapping
from random import randrange


class MapBase(MutableMapping):
    """提供用于保存键值对记录类的自定义映射基类"""

    class _Item:
        __slots__ = 'key', 'value'

        def __init__(self, key, value):
            self.key = key
            self.value = value

        def __eq__(self, other):
            return self.key == other.key  # 使用'=='语法基于键比较两个键值对是否相等

        def __ne__(self, other):
            return not (self == other)  # 使用'!='语法基于键比较两个键值对是否不等

        def __lt__(self, other):
            return self.key < other.key  # 使用'<'语法基于键比较两个键值对

    def __str__(self):
        """返回映射对象的字符串表示形式"""
        return str(dict(self.items()))


class UnsortedListMap(MapBase):

    def __init__(self):
        """创建一个空的映射对象"""
        self._table = []  # 映射中的键值对记录保存在列表中

    def __getitem__(self, key):
        """返回与键key关联的值value，当键key不存在则抛出KeyError异常"""
        for item in self._table:
            if key == item.key:
                return item.value
        raise KeyError('key error: ', repr(key))

    def __setitem__(self, key, value):
        """将key-value添加至映射对象中，当存在键值key时将其值替换为value"""
        for item in self._table:  # 遍历查询映射中是否存在键key
            if key == item.key:
                item.value = value
                return
        self._table.append(self._Item(key, value))  # 映射中不存在键key

    def __delitem__(self, key):
        """删除键key代表的键值对，当键key不存在则抛出KeyError异常"""
        for j in range(len(self._table)):  # 遍历查询映射中是否存在键key
            if key == self._table[j].key:
                self._table.pop(j)
                return
        raise KeyError('key error: ', repr(key))  # 映射中不存在键key

    def __len__(self):
        """返回映射中键值对数量"""
        return len(self._table)

    def __iter__(self):
        """生成一个映射中所有键的迭代"""
        for item in self._table:
            yield item.key


class HashMapBase(MapBase):
    """使用哈希表实现映射的基类"""

    def __init__(self, cap=11, p=109345121):
        """创建一个空的映射"""
        self._table = cap * [None]
        self._n = 0
        self._prime = p  # MAD压缩函数中大于哈希表容量的大质数
        self._scale = 1 + randrange(p - 1)  # MAD压缩函数中的缩放系数a
        self._shift = randrange(p)  # MAD压缩函数中的便宜系数b

    def _hash_function(self, k):
        """哈希函数"""
        return (self._scale * hash(k) + self._shift) % self._prime % len(self._table)

    @abstractmethod
    def _bucket_getitem(self, j, k):
        pass

    @abstractmethod
    def _bucket_setitem(self, j, k, v):
        pass

    @abstractmethod
    def _bucket_delitem(self, j, k):
        pass

    def __len__(self):
        return self._n

    def __getitem__(self, k):
        j = self._hash_function(k)
        return self._bucket_getitem(j, k)  # 可能抛出KeyError异常

    def __setitem__(self, k, v):
        j = self._hash_function(k)
        self._bucket_setitem(j, k, v)
        if self._n > len(self._table) // 2:  # 确保负载系数小于0.5
            self._resize(2 * len(self._table) - 1)  # 通常2 * n - 1为质数

    def __delitem__(self, k):
        j = self._hash_function(k)
        self._bucket_delitem(j, k)  # 可能抛出KeyError异常
        self._n -= 1

    def _resize(self, cap):
        """将哈希表容量调整为cap"""
        old = list(self.items())  # 通过迭代获得已有的所有键值对
        self._table = cap * [None]
        self._n = 0
        for k, v in old:
            self[k] = v  # 将键值对重新插入新的哈希表中


class ChainHashMap(HashMapBase):
    """使用分离链接法处理哈希碰撞实现的哈希映射"""

    def _bucket_getitem(self, j, k):
        bucket = self._table[j]
        if bucket is None:
            raise KeyError('Key Error: ' + repr(k))
        return bucket[k]

    def _bucket_setitem(self, j, k, v):
        if self._table[j] is None:
            self._table[j] = UnsortedListMap()  # 使得哈希表该单元处引用一个二级容器
        oldsize = len(self._table[j])
        self._table[j][k] = v
        if len(self._table[j]) > oldsize:  # k为新的键
            self._n += 1

    def _bucket_delitem(self, j, k):
        bucket = self._table[j]
        if bucket is None:
            raise KeyError('Key Error: ' + repr(k))
        del bucket[k]

    def __iter__(self):
        for bucket in self._table:
            if bucket is not None:
                for key in bucket:
                    yield key


class ProbeHashMap(HashMapBase):
    """使用线性查找法处理哈希碰撞实现的哈希映射"""

    _AVAIL = object()  # 哨兵标识，用于标识被键值对被删除的哈希表单元

    def _is_available(self, j):
        """当哈希表索引为j的单元处为空或键值对被删除，则返回True"""
        return self._table[j] is None or self._table[j] is ProbeHashMap._AVAIL

    def _find_slot(self, j, k):
        """查找索引为j的哈希表单元处是否有键k
        该方法的返回值为一个元组，且返回的情况如下：
        - 当在索引为j的哈希表单元处找到键k，则返回(True, first_avail)；
        - 当未在哈希表任何单元处找到键k，则返回(False, j)。
        """
        first_avail = None
        while True:
            if self._is_available(j):
                if first_avail is None:
                    first_avail = j
                if self._table[j] is None:
                    return False, first_avail
            elif k == self._table[j].key:
                return True, j
            j = (j + 1) % len(self._table)

    def _bucket_getitem(self, j, k):
        found, s = self._find_slot(j, k)
        if not found:
            raise KeyError('Key Error: ' + repr(k))
        return self._table[s].value

    def _bucket_setitem(self, j, k, v):
        found, s = self._find_slot(j, k)
        if not found:
            self._table[s] = self._Item(k, v)
            self._n += 1
        else:
            self._table[s].value = v

    def _bucket_delitem(self, j, k):
        found, s = self._find_slot(j, k)
        if not found:
            raise KeyError('Key Error: ' + repr(k))
        self._table[s] = ProbeHashMap._AVAIL

    def __iter__(self):
        for j in range(len(self._table)):
            if not self._is_available(j):
                yield self._table[j].key


class SortedTableMap(MapBase):
    """使用列表实现的有序映射"""

    def __init__(self):
        """创建一个空的有序映射"""
        self._table = []

    def _find_index(self, k, low, high):
        """
        使用二分查找算法，返回从左开始第一个键等于k的键值对所在列表中的位置索引，如果不存在，则返回high + 1
        :param k: 待搜索的键
        :param low: 待搜索的区间下限
        :param high: 待搜索的区间上限
        :return: 位置索引
        """
        if high < low:  # 查询失败
            return high + 1
        else:
            mid = (low + high) // 2
            if k == self._table[mid].key:
                return mid
            elif k < self._table[mid].key:
                return self._find_index(k, low, mid - 1)
            else:
                return self._find_index(k, mid + 1, high)

    def __len__(self):
        """返回映射中键值对个数"""
        return len(self._table)

    def __getitem__(self, k):
        """返回键等于k的值，若k不存在则抛出KeyError异常"""
        j = self._find_index(k, 0, len(self._table) - 1)
        if j == len(self._table) or self._table[j].key != k:  # 列表索引可能越界
            raise KeyError('Key Error: ' + repr(k))
        return self._table[j].value

    def __setitem__(self, k, v):
        """设置键值对(k, v)，如k已存在则用v替换原先的值"""
        j = self._find_index(k, 0, len(self._table) - 1)
        if j < len(self._table) and self._table[j].key == k:
            self._table[j].value = v  # 替换键k处已存在的值v
        else:
            self._table.insert(j, self._Item(k, v))  # 封装键值对(k, v)后插入映射

    def __delitem__(self, k):
        """删除和键k相关的键值对，如不存在键k则抛出异常KeyError"""
        j = self._find_index(k, 0, len(self._table) - 1)
        if j == len(self._table) or self._table[j].key != k:
            raise KeyError('Key Error: ' + repr(k))
        self._table.pop(j)

    def __iter__(self):
        """按照顺序生成映射所有键的一个迭代"""
        for item in self._table:
            yield item.key

    def __reversed__(self):
        """按照逆序生成所有键的一个迭代"""
        for item in reversed(self._table):
            yield item.key

    def find_min(self):
        """返回映射中键最小的键值对，如果映射为空，则返回None"""
        if len(self._table) > 0:
            return self._table[0].key, self._table[0].value
        else:
            return None

    def find_max(self):
        """返回映射中键最大的键值对，如果映射为空，则返回None"""
        if len(self._table) > 0:
            return self._table[-1].key, self._table[-1].value
        else:
            return None

    def find_lt(self, k):
        """返回映射中键严格小于k的键值对，如果不存在这样的键值对则返回None"""
        j = self._find_index(k, 0, len(self._table) - 1)
        if j > 0:
            return self._table[j - 1].key, self._table[j - 1].value
        else:
            return None

    def find_le(self, k):
        """返回映射中键小于或等于k的键值对，如果不存在这样的键值对则返回None"""
        j = self._find_index(k, 0, len(self._table) - 1)
        if j > 0:
            if j < len(self._table) and self._table[j].key == k:
                return self._table[j].key, self._table[j].value
            else:
                return self._table[j - 1].key, self._table[j - 1].value
        else:
            return None

    def find_gt(self, k):
        """返回映射中键严格大于k的键值对，如果不存在这样的键值对则返回None"""
        j = self._find_index(k, 0, len(self._table) - 1)
        if j < len(self._table) and self._table[j] == k:  # 需要先确保列表索引不越界
            j += 1  # 确保严格大于的条件
        if j < len(self._table):
            return self._table[j].key, self._table[j].value
        else:
            return None

    def find_ge(self, k):
        """返回映射中键大于或等于k的键值对，如果不存在这样的键值对则返回None"""
        j = self._find_index(k, 0, len(self._table) - 1)
        if j < len(self._table):
            return self._table[j].key, self._table[j].value
        else:
            return None

    def find_range(self, start, stop):
        """
        迭代所有满足start <= key < stop的键值对(key,value)，
        且如果start为None，则迭代从最小的键开始，
        如果stop为None，则迭代到最大的键结束。
        """
        if start is None:
            j = 0
        else:
            j = self._find_index(start, 0, len(self._table) - 1)
        while j < len(self._table) and (stop is None or self._table[j].key < stop):
            yield self._table[j].key, self._table[j].value
            j += 1


def test_unsorted_map():
    m = UnsortedListMap()
    print(m)  # {}
    m['K'] = 2
    print(m)  # {'K': 2}
    m['B'] = 4
    print(m)  # {'K': 2, 'B': 4}
    m['U'] = 2
    print(m)  # {'K': 2, 'B': 4, 'U': 2}
    m['V'] = 8
    print(m)  # {'K': 2, 'B': 4, 'U': 2, 'V': 8}
    m['K'] = 9
    print(m)  # {'K': 9, 'B': 4, 'U': 2, 'V': 8}
    print(m['B'])  # 4
    print(m.get('F'))  # None
    print(m.get('F', 5))  # 5
    print(m.get('K', 5))  # 9
    print(len(m))  # 4
    del m['V']
    print(m)  # {'K': 9, 'B': 4, 'U': 2}
    print(m.pop('K'))  # 9
    print(m)  # {'B': 4, 'U': 2}
    print(m.setdefault('B', 1))  # 4
    print(m.setdefault('A', 1))  # 1
    print(m)  # {'B': 4, 'U': 2, 'A': 1}


def test_chain_map():
    m = ChainHashMap()
    print(m)  # {}
    m['K'] = 2
    print(m)  # {'K': 2}
    m['B'] = 4
    print(m)  # {'K': 2, 'B': 4}
    m['U'] = 2
    print(m)  # {'K': 2, 'B': 4, 'U': 2}
    m['V'] = 8
    print(m)  # {'K': 2, 'B': 4, 'U': 2, 'V': 8}
    m['K'] = 9
    print(m)  # {'K': 9, 'B': 4, 'U': 2, 'V': 8}
    print(m['B'])  # 4
    print(m.get('F'))  # None
    print(m.get('F', 5))  # 5
    print(m.get('K', 5))  # 9
    print(len(m))  # 4
    del m['V']
    print(m)  # {'K': 9, 'B': 4, 'U': 2}
    print(m.pop('K'))  # 9
    print(m)  # {'B': 4, 'U': 2}
    print(m.setdefault('B', 1))  # 4
    print(m.setdefault('A', 1))  # 1
    print(m)  # {'B': 4, 'U': 2, 'A': 1}


def test_probe_map():
    m = ProbeHashMap()
    print(m)  # {}
    m['K'] = 2
    print(m)  # {'K': 2}
    m['B'] = 4
    print(m)  # {'K': 2, 'B': 4}
    m['U'] = 2
    print(m)  # {'K': 2, 'B': 4, 'U': 2}
    m['V'] = 8
    print(m)  # {'K': 2, 'B': 4, 'U': 2, 'V': 8}
    m['K'] = 9
    print(m)  # {'K': 9, 'B': 4, 'U': 2, 'V': 8}
    print(m['B'])  # 4
    print(m.get('F'))  # None
    print(m.get('F', 5))  # 5
    print(m.get('K', 5))  # 9
    print(len(m))  # 4
    del m['V']
    print(m)  # {'K': 9, 'B': 4, 'U': 2}
    print(m.pop('K'))  # 9
    print(m)  # {'B': 4, 'U': 2}
    print(m.setdefault('B', 1))  # 4
    print(m.setdefault('A', 1))  # 1
    print(m)  # {'B': 4, 'U': 2, 'A': 1}


def test_sorted_map():
    m = SortedTableMap()
    print(m)  # {}
    m['K'] = 2
    print(m)  # {'K': 2}
    m['B'] = 4
    print(m)  # {'K': 2, 'B': 4}
    m['U'] = 2
    print(m)  # {'K': 2, 'B': 4, 'U': 2}
    m['V'] = 8
    print(m)  # {'K': 2, 'B': 4, 'U': 2, 'V': 8}
    m['K'] = 9
    for k, v in m.find_range('C', 'V'):
        print('(' + repr(k) + ': ' + repr(v) + ')')  # ('K': 9) ('U': 2)
    print(m['B'])  # 4
    print(m.get('F'))  # None
    print(m.get('F', 5))  # 5
    print(m.get('K', 5))  # 9
    print(len(m))  # 4
    del m['V']
    print(m)  # {'K': 9, 'B': 4, 'U': 2}
    print(m.pop('K'))  # 9
    print(m)  # {'B': 4, 'U': 2}
    print(m.setdefault('B', 1))  # 4
    print(m.setdefault('A', 1))  # 1
    print(m)  # {'B': 4, 'U': 2, 'A': 1}


if __name__ == '__main__':
    # test_probe_map()
    test_sorted_map()
