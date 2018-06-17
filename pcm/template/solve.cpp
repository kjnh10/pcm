using namespace std;
#include <iostream>/*{{{*/
#include <bits/stdc++.h>
#define rep(i, x) for(int i = 0; i < (int)(x); i++)
#define reps(i,x) for(int i = 1; i <= (int)(x); i++)
#define rrep(i,x) for(int i=((int)(x)-1);i>=0;i--)
#define rreps(i,x) for(int i=((int)(x));i>0;i--)
#define FOR(i, m, n) for(int i = m;i < n;i++)
#define RFOR(i, m, n) for(int i = m;i >= n;i--)
#define foreach(x,a) for(auto& (x) : (a) )
#define all(x) (x).begin(),(x).end()
#define sz(x) ((int)(x).size())
#define fill(x,y) memset(x,y,sizeof(x))
#define pb(a) push_back(a)
// dump macro{{{
// http://www.creativ.xyz/dump-cpp-652
#define DUMPOUT cerr // 変数ダンプ先。coutかcerr
 
#define DEBUG_ // 提出時はコメントアウト
#ifdef DEBUG_
#define DEB
#else
// DEB と打つとデバッグ時以外はコメントアウトになる
#define DEB /##/
#endif
 
// 変数ダンプ用マクロ。デバッグ時以外は消滅する
// 引数はいくつでもどんな型でも可（ストリーム出力演算子があればOK）
#define dump(...) DEB DUMPOUT<<"  "; \
DUMPOUT<<#__VA_ARGS__; \
DUMPOUT<<":=> "; \
dump_func(__VA_ARGS__); DUMPOUT<<"in ["<<__LINE__<<":"<<__FUNCTION__<<"]"<<endl;
 
// デバッグ用変数ダンプ関数
void dump_func() {
}
template <class Head, class... Tail>
void dump_func(Head&& head, Tail&&... tail)
{
    DUMPOUT << head;
    if (sizeof...(Tail) == 0) {
        DUMPOUT << " ";
    }
    else {
        DUMPOUT << ", ";
    }
    dump_func(std::move(tail)...);
}
 
// vector出力
template<typename T>
ostream& operator << (ostream& os, vector<T>& vec) {
    os << "{";
    for (int i = 0; i<vec.size(); i++) {
        os << vec[i] << (i + 1 == vec.size() ? "" : ", ");
    }
    os << "}";
    return os;
}/*}}}*/
#define debug(x)                 cerr << __LINE__ << ": " << #x << " -> " << x << '\n'
#define debug2(x, y)             cerr << __LINE__ << #x<<": "<<x<<" | "<<#y<<": "<<y<<endl
#define debug3(x, y, z)          cerr << __LINE__ << #x<<":" <<x<<" | "<<#y<<": "<<y<<" | "<<#z<<": "<<z<<endl
#define debug4(a, b, c, d)       cerr << __LINE__ << #a<<": "<<a<<" | "<<#b<<": "<<b<<" | "<<#c<<": "<<c<<" | "<<#d<<": "<<d<<endl
#define debug5(a, b, c, d, e)    cerr << __LINE__ << #a<<": "<<a<<" | "<<#b<<": "<<b<<" | "<<#c<<": "<<c<<" | "<<#d<<": "<<d<<" | "<<#e<< ": "<<e<<endl
#define debug6(a, b, c, d, e, f) cerr << __LINE__ << #a<<": "<<a<<" | "<<#b<<": "<<b<<" | "<<#c<<": "<<c<<" | "<<#d<<": "<<d<<" | "<<#e<< ": "<<e<<" | "<<#f<<": "<<f<<endl
#define db_2d(d,n,m) rep(i,n){rep(j,m){ cerr << (d)[i][j] << (((j)==(m-1))?"\n":" "); }}
#define db_1d(d,n) rep(i,n){cout << d[i] << (((i)==(n-1))?"\n":" ") << __LINE__}
#define INF 999999999
typedef long long ll;
typedef vector<int> vi;
typedef vector<vi> vvi;
typedef long long ll;
typedef vector<long long> vll;
typedef vector<vll> vvll;
typedef long double ld;
typedef pair<int,int> pii;
typedef vector<pii> vii;
typedef vector<vii> vvii;
typedef tuple<int,int,int> iii;
typedef set<int> si;
typedef complex<double> pnt;
typedef vector<pnt> vpnt;
typedef priority_queue<pii,vii,greater<pii> > spq;
int dy[]={0, 0, 1, -1, 0};
int dx[]={1, -1, 0, 0, 0};/*}}}*/

int main() {
  cin.tie(0);
  ios::sync_with_stdio(false);

  return 0;
}
