from ch8.tree import LinkedBinaryTree
from ch10.map import MapBase


class TreeMap(LinkedBinaryTree, MapBase):
    """使用二叉搜索树实现的有序映射类"""

    class Position(LinkedBinaryTree.Position):
        """用于表示二叉搜索树中节点位置的类"""

        def key(self):
            """返回映射中某键值对的键"""
            return self.element().key

        def value(self):
            """返回映射中某键值对的值"""
            return self.element().value

    def _subtree_search(self, p, k):
        """针对根节点在位置p处的二叉搜索（子）树，返回键为k的节点位置"""
        if k == p.key():
            return p  # 查找成功
        elif k < p.key():  # 对左子树进行递归查找
            if self.left(p) is not None:
                return self._subtree_search(self.left(p), k)
        else:  # 对右子树进行递归查找
            if self.right(p) is not None:
                return self._subtree_search(self.right(p), k)
        return p  # 查找失败

    def _subtree_first_position(self, p):
        """返回以位置p处节点为根节点的二叉搜索（子）树中“第一个”节点的位置"""
        walk = p
        while self.left(walk) is not None:
            walk = self.left(walk)
        return walk

    def _subtree_last_position(self, p):
        """返回以位置p处节点为根节点的二叉搜索（子）树中“最后一个”节点的位置"""
        walk = p
        while self.right(walk) is not None:
            walk = self.right(walk)
        return walk

    def first(self):
        """返回该二叉搜索树第一个节点的位置"""
        return self._subtree_first_position(self.root()) if len(self) > 0 else None

    def last(self):
        """返回该二叉搜索树最后一个节点的位置"""
        return self._subtree_last_position(self.root()) if len(self) > 0 else None

    def before(self, p):
        """返回中序遍历时，位置p的前一个位置，当位置p为第一个位置时返回None"""
        self._pos2node(p)  # 确保待操作位置的节点依然有效
        if self.left(p):
            return self._subtree_last_position(self.left(p))
        else:
            walk = p
            ancestor = self.parent(walk)
            while ancestor is not None and walk == self.left(ancestor):
                walk = ancestor
                ancestor = self.parent(walk)
            return ancestor

    def after(self, p):
        """返回中序遍历时，位置p的后一个位置，当位置p为最后一个位置时返回None"""
        self._pos2node(p)  # 确保待操作位置的节点依然有效
        if self.right(p):
            return self._subtree_first_position(self.right(p))
        else:
            walk = p
            ancestor = self.parent(walk)
            while ancestor is not None and walk == self.right(ancestor):
                walk = ancestor
                ancestor = self.parent(walk)
            return ancestor

    def find_position(self, k):
        """
        如果有序映射非空，则当有序映射中存在键为k的键值对，
        则返回该键值对所在节点在二叉搜索树中的位置，
        不存在则返回最后到达的位置，否则返回None
        """
        if self.is_empty():
            return None
        else:
            return self._subtree_search(self.root(), k)

    def find_min(self):
        """
        如有序映射非空，则返回有序映射中键最小的键值对所在节点在二叉搜索树中的位置，
        否则返回None
        """
        if self.is_empty():
            return None
        else:
            p = self.first()
            return p.key(), p.value()

    def find_ge(self, k):
        """查找并返回键不小于k的键值对，如不存在这样的键值对则返回None"""
        if self.is_empty():
            return None
        else:
            p = self.find_position(k)
            if p.key() < k:
                p = self.after(p)
            return p.key(), p.value() if p is not None else None

    def find_range(self, start, stop):
        """
        迭代所有满足start <= key < stop的键值对(key,value)，
        且如果start为None，则迭代从最小的键开始，
        如果stop为None，则迭代到最大的键结束。
        """
        if not self.is_empty():
            if start is None:
                p = self.first()
            else:
                p = self.find_position(start)
                if p.key() < start:
                    p = self.after(p)
            while p is not None and (stop is None or p.key() < stop):
                yield p.key(), p.value()
                p = self.after(p)

    def __getitem__(self, k):
        """返回有序映射中键k所对应的值，如键k不存在则抛出KeyError异常"""
        if self.is_empty():
            raise KeyError('Key Error: ' + repr(k))
        else:
            p = self._subtree_search(self.root(), k)
            if k != p.key():
                raise KeyError('Key Error: ' + repr(k))
            return p.value()

    def __setitem__(self, k, v):
        """向有序映射中插入键值对(k, v)，当k存在时替换原有的值"""
        if self.is_empty():
            self._add_root(self._Item(k, v))
        else:
            p = self._subtree_search(self.root(), k)
            if p.key() == k:
                p.element().value = v
                return
            else:
                item = self._Item(k, v)
                if p.key() < k:
                    self._add_right(p, item)
                else:
                    self._add_left(p, item)

    def __iter__(self):
        """生成映射所有键的一个迭代"""
        p = self.first()
        while p is not None:
            yield p.key()
            p = self.after(p)

    def delete(self, p):
        """删除给定位置处的节点"""
        self._pos2node(p)  # 确保待操作位置的节点依然有效
        if self.left(p) and self.right(p):  # 位置p处有两个子节点
            replacement = self._subtree_last_position(self.left(p))
            self._replace(p, replacement.element())  # 将位置p处节点的键值对进行替换
            p = replacement
        # 这时位置p处至多有一个子节点
        self._delete(p)

    def __delitem__(self, k):
        """删除键为k的节点，当键k不存在时抛出KeyError异常"""
        if not self.is_empty():
            p = self._subtree_search(self.root(), k)
            if k == p.key():
                self.delete(p)
                return
        raise KeyError('Key Error: ' + repr(k))


def test_tree_map():
    m = TreeMap()
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
    test_tree_map()
