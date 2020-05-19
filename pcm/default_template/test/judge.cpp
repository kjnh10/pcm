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

template <class T>/*{{{*/
void tell(T x) {
    cout << x << endl;
    fflush(stdout);
}/*}}}*/

bool check_AIE(){/*{{{*/
    ll tmp;cin>>tmp;
    if (cin.eof()==0) exit(AIE);  // check needles user-output does not exist
}/*}}}*/

int judge_case(ll x) {
    ll num = 22;  // TODO: update query number limit
    while(num--){
        string query;
        cin >> query;
        if (query=="?"){ // query
            ll solver_ans;cin>>solver_ans;
            tell(gcd(solver_ans, x));
        }
        if (query=="!"){ // ans
            ll solver_ans;cin>>solver_ans;
            if (abs(solver_ans-x)<=7 || (solver_ans<=2*x && x<=2*solver_ans)){
                return 0;
            }
            else{
                cerr << "WA: ";
                dump(x, solver_ans);
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
        cerr << "start judge for: " << x[q] << " [judge]" << endl;;
        judge_case(x[q]); 
    }

    // check_AIE(); // これは何故か動かない。無限待機になってしまう。
    exit(AC);
    return 0;
}
