#include "testlib.h"
#include <iostream>

using namespace std;

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    
    int min_val = opt<int>("min_val");
    int max_val = opt<int>("max_val");
    
    int a = rnd.next(min_val, max_val);
    int b = rnd.next(min_val, max_val);
    
    cout << a << " " << b << endl;
    
    return 0;
}
