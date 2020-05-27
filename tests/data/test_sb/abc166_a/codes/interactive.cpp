#include "header.hpp"
template<class T=ll> using vec = vector<T>;
// TODO: struct flushを切ってあげないといけない？

template<class T, class R>
R query(T q){/*{{{*/
    cout << "?" << " " << q << endl;
    fflush(stdout);

    R res; cin>>res;
    if (cin.eof()==1) exit(1);  // judgeがWAで止まった時などに終了するためのコード
    return res;
}/*}}}*/

template<class T>
void answer(T u){/*{{{*/
    cout << "!" << " " << u << endl;
    fflush(stdout);
}/*}}}*/

void solve(){
    ll res = 1;
    ll num = 22;
    rep(i, num-1){
        // ll g = query(3);
        // res += g;
        // dump(g, res);
    }
    answer(res);

    return 0;
}

int main(){/*{{{*/
    ll Q;cin>>Q;
    rep(_, Q){
        solve();
    }
    return 0;
}/*}}}*/
