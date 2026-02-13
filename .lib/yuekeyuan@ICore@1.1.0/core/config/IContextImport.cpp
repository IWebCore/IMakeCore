#include "IContextImport.h"

template class IContextImport<IJson>;
template class IContextImport<bool>;
template class IContextImport<char>;
template class IContextImport<uchar>;
template class IContextImport<signed char>;
template class IContextImport<short>;
template class IContextImport<ushort>;
template class IContextImport<int>;
template class IContextImport<uint>;
template class IContextImport<long>;
template class IContextImport<ulong>;
template class IContextImport<long long>;
template class IContextImport<qulonglong>;
template class IContextImport<float>;
template class IContextImport<double>;
template class IContextImport<long double>;

template class IContextImport<std::map<std::string, std::string>>;
template class IContextImport<QString>;
template class IContextImport<std::string>;
template class IContextImport<QStringList>;

