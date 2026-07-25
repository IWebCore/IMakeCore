#include "hello.h"
#include <iostream>

int main() {
    std::cout << "hello world";
    return hello_version() != 1 ? 0 : 1;

}
