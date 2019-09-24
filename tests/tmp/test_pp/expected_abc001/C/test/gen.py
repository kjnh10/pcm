from random import randint, choice, sample, choices

# L = [3, 5, 7, 9]
# print(randint(1, 100))  # # [1, 100]
# print(choice(L))  # 1つ選択
# print(sample(L, k=2))  # 非復元抽出
# print(sample(L, k=len(L)))  # random permutation
# print(choices(L, k=2))  # 復元抽出

N = randint(1, 100000)
K = randint(1, 100000)

print(N, K)
