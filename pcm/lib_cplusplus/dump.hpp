#pragma once

// http://www.creativ.xyz/dump-cpp-652
using namespace std;
#include <bits/stdc++.h>

#define DUMPOUT cerr // where to dump. cout or cerr

namespace dump_macro{
    stack<vector<string>> varnames;
    stack<int> varidx;
}

#define cerrendl cerr << endl

#define dump(...)  \
{  \
    dump_macro::varnames.push(split_va_args(#__VA_ARGS__)); \
    dump_macro::varidx.push(0); \
    dump_func(__VA_ARGS__); DUMPOUT<<"in ["<<__LINE__<<":"<<__FUNCTION__<<"]"<<endl;  \
    dump_macro::varnames.pop();dump_macro::varidx.pop(); \
}

#define dump_1d(x,n)  \
{  \
    DUMPOUT <<"  " \
    <<#x<<"["<<#n<<"]"<<":=> {"; \
    rep(i,n){ DUMPOUT << x[i] << (((i)==(n-1))?"}":", "); } DUMPOUT <<" in [" << __LINE__ << "]" << endl;  \
}

#define dump_2d(x,n,m) \
{  \
    DUMPOUT <<"  " \
    <<#x<<"["<<#n<<"]"<<"["<<#m<<"]"<<":=> \n"; \
    rep(i,n)rep(j,m){ DUMPOUT << ((j==0)?"     |":" ") << x[i][j] << (((j)==(m-1))?"|\n":" "); } \
    DUMPOUT <<"  in [" << __LINE__ << "]" << endl; \
}

void dump_func() {
}

template <class Head, class... Tail>
void dump_func(Head&& head, Tail&&... tail)
{
    DUMPOUT << dump_macro::varnames.top()[dump_macro::varidx.top()] << ":" << head;
    if (sizeof...(Tail) == 0) {
        DUMPOUT << " ";
    }
    else {
        DUMPOUT << ", ";
    }
    ++dump_macro::varidx.top();
    dump_func(std::move(tail)...);
}

vector<string> split_va_args(string s){
    int n = s.size(); 
    vector<string> res; 
    string tmp = ""; 
    int parlevel = 0; 
    for(int i=0; i<n; i++){ 
        if (s[i]=='(') parlevel++; 
        if (s[i]==')') parlevel--; 
        if (s[i]==' ') continue; 
        if (s[i]==',' && parlevel==0){ 
            res.push_back(tmp); 
            tmp = ""; 
        } 
        else{ 
            tmp += s[i]; 
        } 
    } 
    res.push_back(tmp); 
    return res; 
}

#include "prettyprint.hpp"
