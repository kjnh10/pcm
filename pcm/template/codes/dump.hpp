// http://www.creativ.xyz/dump-cpp-652
using namespace std;
#include <iostream>
#include <bits/stdc++.h>

#define DUMPOUT cerr // where to dump. cout or cerr

#define dump(...) DUMPOUT<<"  "; \
  DUMPOUT<<#__VA_ARGS__; \
  DUMPOUT<<":=> "; \
  dump_func(__VA_ARGS__); DUMPOUT<<"in ["<<__LINE__<<":"<<__FUNCTION__<<"]"<<endl;

#define dump_1d(x,n) DUMPOUT <<"  " \
  <<#x<<"["<<#n<<"]"<<":=> {"; \
  rep(i,n){ DUMPOUT << x[i] << (((i)==(n-1))?"}":", "); } DUMPOUT <<" in [" << __LINE__ << "]" << endl;

#define dump_2d(x,n,m) DUMPOUT <<"  " \
  <<#x<<"["<<#n<<"]"<<"["<<#m<<"]"<<":=> \n"; \
  rep(i,n)rep(j,m){ DUMPOUT << ((j==0)?"     |":" ") << x[i][j] << (((j)==(m-1))?"|\n":" "); } \
  DUMPOUT <<"  in [" << __LINE__ << "]" << endl;

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

#include "cxx-prettyprint/prettyprint.hpp"
