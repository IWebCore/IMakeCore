// Copyright (c) 2021 Borislav Stanimirov
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#pragma once


#if __has_include(<charconv>)
    #include <charconv>
    namespace msstl = std;
#else

    #include "charconv_fwd.hpp"
    #include "charconv_impl.inl"
#endif
