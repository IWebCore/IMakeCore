###################################
# SYSTEM CONFIGURED, DO NOT EDIT!!!
###################################

# inclue packages.json to project
OTHER_FILES += packages.json 


# test@world@1.0.0
# Test library that depends on hello
include(C:/Users/Yue/IMakeCore/test/basic_resolve/project_transitive/.lib/test@world@1.0.0.pri)

# test@hello@2.0.0
# Test source library v2 (contains .cpp)
include(C:/Users/Yue/IMakeCore/test/basic_resolve/project_transitive/.lib/test@hello@2.0.0.pri)
