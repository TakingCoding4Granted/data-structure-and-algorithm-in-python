def merge(s1, s2, s):
    """将有序列表s1和s2合并为一个有序列表"""
    i = j = 0
    while i + j < len(s):
        if j == len(s2) or (i < len(s1) and s1[i] < s2[j]):
            s[i + j] = s1[i]  # 将s1的第i个元素拷贝为s的下一个元素
            i += 1
        else:
            s[i + j] = s2[j]  # 将s2的第j个元素拷贝为s的下一个元素
            j += 1


def merge_sort(s):
    """对列表s使用归并排序算法"""
    num = len(s)
    if num < 2:
        return
    # 分（divide）
    mid = num // 2
    s1 = s[0:mid]
    s2 = s[mid:num]
    # 治（conquer）
    merge_sort(s1)
    merge_sort(s2)
    # 合并结果（merge results）
    merge(s1, s2, s)
