#include "ICmdInterface.h"
#include "cmd/ICmdException.h"

$PackageWebCoreBegin

namespace detail
{

void toBool(bool& value, const QString& raw)
{
    QStringList trueValue = {
        "true", "yes", "y", "on", "1", "enable"
    };
    QStringList falseValue = {
        "false", "no", "n", "off", "0", "disable"
    };

    for(const QString& val : trueValue){
        if(val.toUpper() == raw.toUpper()){
            value = true;
            return;
        }
    }

    for(const QString& val : falseValue){
        if(val.toUpper() == raw.toUpper()){
            value = false;
            return;
        }
    }

    QString tip = QString(" [Truthy Value]: ").append(trueValue.join(", "))
            .append(" [Falsy Value]: ").append(falseValue.join(", "));
    throw ICmdException("argument can not be parsed to bool. only below value (ignore case) can be processed " + tip);
}

template<>
void setValue<QStringList>(QStringList& value, const QStringList& raws)
{
    value = raws;
}

template<>
void setValue<QList<short>>(QList<short>& value, const QStringList& raws)
{
    bool ok;
    for(const QString& raw : raws){
        value.append(raw.toShort(&ok));
        if(!ok){
            throw ICmdException("value can not be convert to QList<short>. [Values]: " + raws.join(", "));
        }
    }
}

template<>
void setValue<QList<ushort>>(QList<ushort>& value, const QStringList& raws)
{
    bool ok;
    for(const QString& raw : raws){
        value.append(raw.toUShort(&ok));
        if(!ok){
            throw ICmdException("value can not be convert to QList<ushort>. [Values]: " + raws.join(", "));
        }
    }
}

template<>
void setValue<QList<int>>(QList<int>& value, const QStringList& raws)
{
    bool ok;
    for(const QString& raw : raws){
        value.append(raw.toInt(&ok));
        if(!ok){
            throw ICmdException("value can not be convert to QList<int>. [Values]: " + raws.join(", "));
        }
    }
}

template<>
void setValue<QList<uint>>(QList<uint>& value, const QStringList& raws)
{
    bool ok;
    for(const QString& raw : raws){
        value.append(raw.toUInt(&ok));
        if(!ok){
            throw ICmdException("value can not be convert to QList<uint>. [Values]: " + raws.join(", "));
        }
    }
}

template<>
void setValue<QList<long>>(QList<long>& value, const QStringList& raws)
{
    bool ok;
    for(const QString& raw : raws){
        value.append(raw.toLong(&ok));
        if(!ok){
            throw ICmdException("value can not be convert to QList<long>. [Values]: " + raws.join(", "));
        }
    }
}

template<>
void setValue<QList<ulong>>(QList<ulong>& value, const QStringList& raws)
{
    bool ok;
    for(const QString& raw : raws){
        value.append(raw.toLong(&ok));
        if(!ok){
            throw ICmdException("value can not be convert to QList<ulong>. [Values]: " + raws.join(", "));
        }
    }
}

template<>
void setValue<QList<qlonglong>>(QList<qlonglong>& value, const QStringList& raws)
{
    bool ok;
    for(const QString& raw : raws){
        value.append(raw.toLong(&ok));
        if(!ok){
            throw ICmdException("value can not be convert to QList<longlong>. [Values]: " + raws.join(", "));
        }
    }
}

template<>
void setValue<QList<qulonglong>>(QList<qulonglong>& value, const QStringList& raws)
{
    bool ok;
    for(const QString& raw : raws){
        value.append(raw.toULongLong(&ok));
        if(!ok){
            throw ICmdException("value can not be convert to QList<qulonglong>. [Values]: " + raws.join(", "));
        }
    }
}

template<>
void setValue<QList<bool>>(QList<bool>& value, const QStringList& raws)
{
    bool val;
    for(const QString& raw : raws){
        toBool(val, raw);
        value.append(val);
    }
}

template<>
void setValue<QString>(QString& value, const QStringList& raws)
{
    if(raws.length() != 1){
        throw ICmdException("argument should be one, but exist many. ");
    }

    value = raws.first();
}

template<>
void setValue<short>(short& value, const QStringList& raws)
{
    if(raws.length() != 1){
        throw ICmdException("argument should be one, but exist many. ");
    }

    bool ok;
    QString raw = raws.first();
    value = raw.toShort(&ok);
    if(!ok){
        throw ICmdException("argument can not be parsed to short");
    }
}

template<>
void setValue<ushort>(ushort& value, const QStringList& raws)
{
    if(raws.length() != 1){
        throw ICmdException("argument should be one, but exist many. ");
    }

    bool ok;
    QString raw = raws.first();
    value = raw.toUShort(&ok);
    if(!ok){
        throw ICmdException("argument can not be parsed to ushort");
    }
}

template<>
void setValue<int>(int& value, const QStringList& raws)
{
    if(raws.length() != 1){
        throw ICmdException("argument should be one, but exist many. ");
    }

    bool ok;
    QString raw = raws.first();
    value = raw.toInt(&ok);
    if(!ok){
        throw ICmdException("argument can not be parsed to int");
    }
}

template<>
void setValue<uint>(uint& value, const QStringList& raws)
{
    if(raws.length() != 1){
        throw ICmdException("argument should be one, but exist many. ");
    }

    bool ok;
    QString raw = raws.first();
    value = raw.toInt(&ok);
    if(!ok){
        throw ICmdException("argument can not be parsed to uint");
    }
}

template<>
void setValue<long>(long& value, const QStringList& raws)
{
    if(raws.length() != 1){
        throw ICmdException("argument should be one, but exist many. ");
    }

    bool ok;
    QString raw = raws.first();
    value = raw.toLong(&ok);
    if(!ok){
        throw ICmdException("argument can not be parsed to long");
    }
}

template<>
void setValue<ulong>(ulong& value, const QStringList& raws)
{
    if(raws.length() != 1){
        throw ICmdException("argument should be one, but exist many. ");
    }

    bool ok;
    QString raw = raws.first();
    value = raw.toULong(&ok);
    if(!ok){
        throw ICmdException("argument can not be parsed to ulong");
    }
}

template<>
void setValue<qlonglong>(qlonglong& value, const QStringList& raws)
{
    if(raws.length() != 1){
        throw ICmdException("argument should be one, but exist many. ");
    }

    bool ok;
    QString raw = raws.first();
    value = raw.toLongLong(&ok);
    if(!ok){
        throw ICmdException("argument can not be parsed to longlong");
    }
}

template<>
void setValue<qulonglong>(qulonglong& value, const QStringList& raws)
{
    if(raws.length() != 1){
        throw ICmdException("argument should be one, but exist many. ");
    }

    bool ok;
    QString raw = raws.first();
    value = raw.toULongLong(&ok);
    if(!ok){
        throw ICmdException("argument can not be parsed to ulonglong");
    }
}

template<>
void setValue<bool>(bool& value, const QStringList& raws)
{
    if(raws.length() != 1){
        throw ICmdException("argument should be one, but exist many. ");
    }

    auto raw = raws.first();
    toBool(value, raw);
}


}

$PackageWebCoreEnd
