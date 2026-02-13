#include "ITicTacUtil.h"

$PackageWebCoreBegin

ITicTac::ITicTac(const char *file, const char *function, int line)
    : file(file), function(function), line(QString::number(line))
{
    using namespace std::chrono;
    tic = std::chrono::high_resolution_clock().now();
}

ITicTac::~ITicTac()
{
    using namespace std::chrono;
    auto toc = high_resolution_clock().now();
    auto tip = QString("ms TAC in %1 file, %2 line, %3 function,").arg(file).arg(line).arg(function);
    qDebug().noquote() << duration_cast<microseconds>(toc - tic).count() * 1.0 / 1000  << tip;
}

$PackageWebCoreEnd
