#include "IRdbEntityInfo.h"

#include "core/util/IMetaUtil.h"
#include "rdb/IRdbAbort.h"
#include "rdb/entity/IRdbTableInfo.h"

$PackageWebCoreBegin

IRdbEntityInfo::IRdbEntityInfo(const QMetaObject &meta)
    : m_metaObject(meta)
{
    this->m_className = meta.className();
    this->m_entityName = IMetaUtil::getMetaClassInfoByName(meta, "sql_entityName", this->m_className);

    int count = meta.propertyCount();
    for(int i=0; i<count; i++){
        Field field;
        field.m_property = meta.property(i);
        field.m_typeName = field.m_property.typeName();
        field.m_name = field.m_property.name();
        m_fieldNames.append(field.m_name);
        field.m_typeId = QMetaType::Type(IMetaUtil::typeId(field.m_property)); // TODO:
        if(field.m_typeId == QMetaType::User){
            field.m_typeId = QMetaType::Type(IMetaUtil::typeId(field.m_typeName.toUtf8()));
            if(field.m_typeId == QMetaType::UnknownType){
                QString tip = QString("in your field declaration, your field type is not registered, please register it. Field:").append(field.m_name);
                IRdbAbort::abortTableDeclarationError(tip, $ISourceLocation);
            }
        }
        this->m_fields.append(field);
    }
}

$PackageWebCoreEnd
