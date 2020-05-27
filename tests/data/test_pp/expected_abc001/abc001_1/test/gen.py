from random import randint, choice, sample, choices
from typing import TYPE_CHECKING, List, Optional, Type
import string
import math
# print(choice(a))  # 1つ選択
# print(sample(a, k=2))  # 非復元抽出
# print(sample(a, k=len(L)))  # random permutation
# print(choices(a, k=2))  # 復元抽出

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

class randperm(object):
    def __init__(self, n:int):
        self.data = sample(list(range(1, n+1)), k=n)
    def __str__(self):
        return ' '.join(map(str, self.data))

class randseq(object):
    def __init__(self, n: int, l: int, r: int, distinct=False):
        self.data = []
        used = set()
        if (n>r-l+1) and distinct:
            raise Exception(print("n>r-l+1 and distinct=True is not impossible"))

        while len(self.data) < n:
            v = randint(l, r)
            if distinct and v in used:
                pass
            else:
                self.data.append(v)
                used.add(v)

    def __str__(self):
        return ' '.join(map(str, self.data))

def randstr(length: int, chars: List=['a', 'b', 'c', 'd', 'e']):
# def randstr(length: int, chars: List=string.ascii_lowercase):
    res = ""
    for i in range(length):
        res += choice(chars)
    return res

def randprime(l: int = 2, r: int = 1000000007): # [l, r]
    def is_prime(x):
        if (x == 1): return False
        for i in range(2, int(math.sqrt(x))+1):
            if x % i == 0:
                return False
        return True


    cnt = 0
    while True:
        res = randint(l, r)
        if (is_prime(res)):
            return res
        cnt += 1
        if cnt>=1000:
            assert False

class randtree(object):
    def __init__(self, n: int, root: int = 0):
        assert root < n
        self.edges = []
        self.n = n
        s = set([x for x in range(n) if x!=root])
        joined = [root]
        self.edges = []
        for _ in range(n-1):
            a = sample(s, 1)[0]
            b = choice(joined)
            self.edges.append((b, a))  # この向きにするとgraphvizの表示が木らしくなる。
            s.remove(a)
            joined.append(a)

    def __str__(self, one_index=True, header=False):
        res = []
        if header:
            res.append(f"{self.n} {self.n-1}")

        for edge in self.edges:
            res.append(f"{edge[0]+one_index} {edge[1]+one_index}")
        return '\n'.join(res)

class randgraph(object):  # undirected
    def __init__(self, n:int, lb:int=1, ub:int=float('inf'), tree_ok=True):
        self.n = n
        if ub == float('inf'):
            ub = n*(n-1)/2

        while True:
            if tree_ok:  # tree graph
                # 10%くらいは木が生成されるように
                r = randint(1, 10)
                if (r<=2):
                    self.edges = randtree(n).edges
                    return

            # TODO: [line graph, star graph, complete graph]

            uf = UnionFind(n)
            self.edges = set()
            while(uf.group_count()>1 or len(self.edges)<lb):
                u = randint(0, n-1)
                v = randint(0, n-1)
                if (u==v): continue

                if (u>v): u,v=v,u
                self.edges.add((u, v))
                uf.union(u, v)
            self.edges = list(self.edges)
            if len(self.edges) <= ub:
                return

    def __str__(self, one_index=True, header=True):
        res = []
        if header:
            res.append(f"{self.n} {len(self.edges)}")
        for edge in self.edges:
            res.append(f"{edge[0]+one_index} {edge[1]+one_index}")
        return '\n'.join(res)

# write down here
# ---------------------------------------------
n = randint(2, 10)
print(n)
