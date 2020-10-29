import sys
from math import gcd
from pcm.codefile import JudgeResult as jr


def tell(x):
    print(x, flush=True)


def dump(x):
    print(x, ': by judge', file=sys.stderr)


def check_AIE():
    try:
        input()
    except EOFError:
        pass
    else:
        exit(jr.AIE)


def judge_case(x):
    dump(f'start judge for {x=}')
    try:
        num = 22
        while (num):
            num -= 1
            query = list(input().split())
            v = int(query[1])
            if (query[0] == "?"):
                tell(gcd(v, x))

            if (query[0] == "!"):
                if (abs(v - x) <= 7 or (v <= 2 * x and x <= 2 * v)):
                    dump(f"AC: {x=}, {v=}")
                    return 0
                else:
                    dump(f"WA: {x=}, {v=}")
                    sys.exit(jr.WA)
        sys.exit(jr.QLE)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(jr.RE)


def main():  # multi case type
    # input case from a case file
    # case fileの入力をとりきらないとsolver-codeからの出力を入力として受け取れないことに注意。
    Q = int(input())
    x = []
    for i in range(Q):
        x.append(int(input()))

    # judge
    tell(Q)  # TODO: needed only for multi-test-case
    for i in range(Q):
        print('', file=sys.stderr)
        judge_case(x[i])

    # これは何故か動かない。
    # check_AIE()
    sys.exit(jr.AC)


# def main():  # single case type
#     x = int(input())
#     judge_case(x)
#     sys.exit(jr.AC)

if __name__ == "__main__":
    # main()
    print("hello")
