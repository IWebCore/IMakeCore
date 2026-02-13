#include "IGlobalAbort.h"

$PackageWebCoreBegin

template class IAbortInterface<IGlobalAbort>;

QMap<int, QString> IGlobalAbort::abortDescription() const{
    return {
        {UnVisibleMethod, "this method must not be called at any time, but due to qt meta issue, this function must exist,"
                          "so the application abort this info."},
        {UnReachableCode, "this is dead code. it means program never run to here, otherwise the program goes wrong"},
        {UnImplimentedMethod, "unimplimented method, this will be implimented latter"},
        {SingletonInstanceCreateError,  "error with singleton instance, you should not create anyother instance of this"},
        {DuplicatedKey, "in your program, duplicated key exist"}
    };
}

QString IGlobalAbort::abortComment(){
    return "Abort about global fatal event";
}

$PackageWebCoreEnd
