from random import randint, choice, sample, choices

L = [3, 5, 7, 9]
# print(randint(1, 100))  # # [1, 100]
# print(choice(L))  # 1つ選択
# print(sample(L, k=2))  # 非復元抽出
print(sample(L, k=len(L)))  # random permutation
# print(choices(L, k=2))  # 復元抽出

def randperm(n:int):
    return sample(list(range(1, n+1)), k=n)

def randseq(n:int, l:int, r:int, distinct=False):
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

def printtree(n: int):
    pass

def printgraph(n: int, m: int):
    pass

# N = randint(1, 100000)
# K = randint(1, 100000)
# print(N, K)
# print(randperm(5))
# print(randseq(10, 1, 100, True))
