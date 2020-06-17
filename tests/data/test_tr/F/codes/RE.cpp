#include "header.hpp"
template<class T=ll> using vec = vector<T>;

struct Sieve {/*{{{*/
    // エラトステネスのふるい O(NloglogN)
    ll n;                              // n]
    vector<ll> f;                      // [1, 2, 3, 2, 5, 2, 7, 2, 3, ....]
    vector<ll> primes;                 // [2, 3, 5, .......]
    Sieve(ll n = 1) : n(n), f(n + 1) { /*{{{*/
        f[0] = f[1] = -1;
        for (ll i = 2; i <= n; ++i) {
            if (f[i]) continue;
            primes.push_back(i);
            f[i] = i;
            for (ll j = i * i; j <= n; j += i) {
                if (!f[j]) f[j] = i;
            }
        }
    } /*}}}*/
    bool isPrime(ll x) { return f[x] == x; }

    vector<ll> factor_list(ll x) { /*{{{*/
        vector<ll> res;
        if (x < n) {
            while (x != 1) {
                res.push_back(f[x]);
                x /= f[x];
            }
        } else {
            for (ll i = 0; primes[i] * primes[i] <= x; i++) {
                while (x % primes[i] == 0) {
                    res.pb(primes[i]);
                    x /= primes[i];
                }
            }
            if (x != 1) res.pb(x);
        }

        return res;  // [2, 3, 3, 5, 5, 5.....]
    }                /*}}}*/

    vector<pair<ll, ll>> factor(ll x) { /*{{{*/
        vector<ll> fl = factor_list(x);
        if (fl.size() == 0) return {};
        vector<pair<ll, ll>> res(1, mp(fl[0], 0));
        for (ll p : fl) {
            if (res.back().first == p) {
                res.back().second++;
            } else {
                res.emplace_back(p, 1);
            }
        }
        return res;  // [(2,1), (3,2), (5,3), .....]
    }                /*}}}*/
};/*}}}*/
Sieve sv(31623);

ll query(ll q){/*{{{*/
    cout << "?" << " " << q << endl;
    fflush(stdout);

    ll res; cin>>res;
    if (cin.eof()==1) exit(1);  // judgeがWAで止まった時などに終了するためのコード
    return res;
}/*}}}*/

void answer(ll u){/*{{{*/
    cout << "!" << " " << u << endl;
    fflush(stdout);
}/*}}}*/

ll calc(ll x){/*{{{*/
    if (x==1) return 1;
    ll ox = x;
    while(x<=1000000000){
        x *= ox;
        // dump(x);
    }
    return x/ox;
}/*}}}*/

ll solve(){
    int x = 1;
    x /= 0;
    // answer(-1);

    return 0;
}

int main(){/*{{{*/
    ll Q;cin>>Q;
    rep(_, Q){
        solve();
    }
    return 0;
}/*}}}*/
