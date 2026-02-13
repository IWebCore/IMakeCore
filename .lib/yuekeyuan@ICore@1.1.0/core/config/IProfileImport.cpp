#include "IProfileImport.h"

template class IProfileImport<IJson>;
template class IProfileImport<bool>;
template class IProfileImport<char>;
template class IProfileImport<uchar>;
template class IProfileImport<signed char>;
template class IProfileImport<short>;
template class IProfileImport<ushort>;
template class IProfileImport<int>;
template class IProfileImport<uint>;
template class IProfileImport<long>;
template class IProfileImport<ulong>;
template class IProfileImport<long long>;
template class IProfileImport<qulonglong>;
template class IProfileImport<float>;
template class IProfileImport<double>;
template class IProfileImport<long double>;

template class IProfileImport<std::map<std::string, std::string>>;
template class IProfileImport<QString>;
template class IProfileImport<std::string>;
template class IProfileImport<QStringList>;
