#include "../codes/header.hpp"

enum JudgeResult {/*{{{*/
    AC = 0,
    WA = 1,
    RE = 2,
    CE = 3,
    TLE = -2,
    MLE = 4,
    QLE = 5,  // Query limit exceeded
    AIE = 6,  // Additional input error
    NOEXP = 98,
    TLENAIVE = 99,
    YET = 100,
};/*}}}*/

template <class T>
void tell(T x) {
    cout << x << endl;
    fflush(stdout);
}

vector<ll> divisor(ll n) {  // 約数全列挙{{{
    vector<ll> p, q;
    for (ll i = 1; i * i <= n; i++) {
        if (n % i == 0) {
            p.pb(i);
            if (i * i != n) q.pb(n / i);
        }
    }
    reverse(all(q));
    p.insert(p.end(), all(q));
    return p;
}  //}}}

int judge_case(ll x) {
    dump("start judge for", x);
    ll num = 22;
    while(num--){
        string query;
        cin >> query;
        if (query=="?"){ // query
            ll v;cin>>v;
            tell(gcd(v, x));
        }
        if (query=="!"){ // ans
            ll v;cin>>v;
            ll dc = sz(divisor(x));
            if (abs(v-dc)<=7 || (v<=2*dc && dc<=2*v)){
                return 0;
            }
            else{
                exit(WA);
            }
        }
    }
    exit(QLE);
}

int main() {
    // input case
    int Q;
    cin >> Q;
    // Q = 1; if single case
    vector<ll> x(Q);
    rep(q, Q){ cin>>x[q]; }

    // judge
    tell(Q);  // off if single case
    rep(q, Q) {
        judge_case(x[q]); 
    }

    // これは何故か動かない。無限待機になってしまう。
    // ll tmp;cin>>tmp;
    // if (cin.eof()==0) exit(AIE);  // check needles user-output does not exist

    exit(AC);
    return 0;
}
