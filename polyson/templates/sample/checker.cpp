#include "testlib.h"

using namespace std;

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    long long answer = ans.readLong();
    long long ouf_val = ouf.readLong();
    
    if (answer != ouf_val) {
        quitf(_wa, "Expected %lld, found %lld", answer, ouf_val);
    }
    
    quitf(_ok, "answer is %lld", answer);

    return 0;
}
