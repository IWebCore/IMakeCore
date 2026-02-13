#include "ICodecUtil.h"

$PackageWebCoreBegin

namespace detail {
  unsigned char ToHex(unsigned char x) { return x > 9 ? x + 55 : x + 48; }

  unsigned char FromHex(unsigned char x) {
    unsigned char y{0};
    if (x >= 'A' && x <= 'Z')
      y = x - 'A' + 10;
    else if (x >= 'a' && x <= 'z')
      y = x - 'a' + 10;
    else if (x >= '0' && x <= '9')
      y = x - '0';
    else
      assert(0);        // NOTE:!
    return y;
  }
}

QByteArray ICodecUtil::urlEncode(const QString& rawUrl) {
  QByteArray str = rawUrl.toUtf8();
  return urlEncode(str);
}

QByteArray ICodecUtil::urlEncode(const QByteArray& str) {
  QByteArray strTemp;
  uint length = str.length();
  for (uint i = 0; i < length; i++) {
    if (isalnum((unsigned char)str[i]) || (str[i] == '-') || (str[i] == '_') ||
        (str[i] == '.') || (str[i] == '~'))
      strTemp += str[i];
    else if (str[i] == ' ')
      strTemp += "+";
    else {
      strTemp += '%';
      strTemp += detail::ToHex((unsigned char)str[i] >> 4);
      strTemp += detail::ToHex((unsigned char)str[i] % 16);
    }
  }
  return strTemp;
}

QByteArray ICodecUtil::urlDecode(const QString& rawUrl) {
  QByteArray str = rawUrl.toLocal8Bit();
  return urlDecode(str);
}

QByteArray ICodecUtil::urlDecode(const QByteArray& str) {
  QByteArray strTemp;
  uint length = str.length();
  for (uint i = 0; i < length; i++) {
    if (str[i] == '+')
      strTemp += ' ';
    else if (str[i] == '%') {
      assert(i + 2 < length);
      unsigned char high = detail::FromHex((unsigned char)str[++i]);
      unsigned char low = detail::FromHex((unsigned char)str[++i]);
      strTemp += high * 16 + low;
    } else
      strTemp += str[i];
  }
  return strTemp;
}

QString ICodecUtil::pathEncode(const QString& rawPath) {
  QByteArray strTemp;
  QByteArray str = rawPath.toLocal8Bit();

  uint length = str.length();
  for (uint i = 0; i < length; i++) {
    if (isalnum((unsigned char)str[i]) || (str[i] == '-') || (str[i] == '_') ||
        (str[i] == '.') || (str[i] == '~') || (str[i] == '/') ||
        (str[i] == ':'))
      strTemp += str[i];
    else if (str[i] == ' ')
      strTemp += "+";
    else {
      strTemp += '%';
      strTemp += detail::ToHex((unsigned char)str[i] >> 4);
      strTemp += detail::ToHex((unsigned char)str[i] % 16);
    }
  }
  return strTemp;
}

$PackageWebCoreEnd
