from random import randint, choice, sample, choices
from typing import TYPE_CHECKING, List, Optional, Type
import string
class UnionFind():
    def __init__(self, n):
        self.n = n
        self.parents = [-1] * n

    def find(self, x):
        if self.parents[x] < 0:
            return x
        else:
            self.parents[x] = self.find(self.parents[x])
            return self.parents[x]

    def union(self, x, y):
        x = self.find(x)
        y = self.find(y)

        if x == y:
            return

        if self.parents[x] > self.parents[y]:
            x, y = y, x

        self.parents[x] += self.parents[y]
        self.parents[y] = x

    def size(self, x):
        return -self.parents[self.find(x)]

    def same(self, x, y):
        return self.find(x) == self.find(y)

    def members(self, x):
        root = self.find(x)
        return [i for i in range(self.n) if self.find(i) == root]

    def roots(self):
        return [i for i, x in enumerate(self.parents) if x < 0]

    def group_count(self):
        return len(self.roots())

    def all_group_members(self):
        return {r: self.members(r) for r in self.roots()}

    def __str__(self):
        return '\n'.join('{}: {}'.format(r, self.members(r)) for r in self.roots())

a = [3, 5, 7, 9]
# print(randint(1, 100))  # # [1, 100]
# print(choice(a))  # 1つ選択
# print(sample(a, k=2))  # 非復元抽出
# print(sample(a, k=len(L)))  # random permutation
# print(choices(a, k=2))  # 復元抽出
def randperm(n: int):
    return sample(list(range(1, n+1)), k=n)
def randseq(n: int, l: int, r: int, distinct=False):
    res = []
    used = set()
    if (n>r-l+1) and distinct:
        raise Exception(print("n>r-l+1 and distinct=True is not impossible"))

    while len(res) < n:
        v = randint(l, r)
        if distinct and v in used:
            pass
        else:
            res.append(v)
            used.add(v)
    return res
def randstr(length: int, chars: List=['a', 'b', 'c', 'd', 'e']):
# def randstr(length: int, chars: List=string.ascii_lowercase):
    res = ""
    for i in range(length):
        res += choice(chars)
    return res

def print_tree(n: int, one_index=True, header=False):
    if header: print(n, n-1)

    s = set(range(1, n))
    joined = [0]
    edges = []
    for _ in range(n-1):
        a = sample(s, 1)[0]
        b = choice(joined)
        edges.append((a, b))
        s.remove(a)
        joined.append(a)
    for edge in edges:
        print(edge[0]+one_index, edge[1]+one_index)
def print_connected_graph(n: int, one_index=True, tree_ok=True):
    if tree_ok:
        # 10%くらいは木が生成されるように
        r = randint(1, 10)
        if (r<=2):
            print_tree(n, one_index=one_index)
            return 0

    uf = UnionFind(n)
    edges = set()
    while(uf.group_count()>1 and (tree_ok or len(edges)>=n)):
        u = randint(0, n-1)
        v = randint(0, n-1)
        if (u==v): continue

        if (u>v): u,v=v,u
        edges.add((u, v))
        uf.union(u, v)

    print(n, len(edges))
    for edge in edges:
        print(edge[0]+one_index, edge[1]+one_index)

def pl(x: List):
    print(' '.join(map(str, x)))

# write down here
# ---------------------------------------------
print_connected_graph(10)
