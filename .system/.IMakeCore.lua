-- IMakeCore xmake integration
--
-- Include from a project's xmake.lua:
--   local imake = os.getenv("IXMakeCore")
--   if imake then includes(imake) end
--   imakecore_init(os.scriptdir())
--
-- imakecore_init(proj_dir) resolves packages.json in proj_dir by running
-- IMakeCore.py <proj_dir> xmake, then includes the generated
-- <proj_dir>/.package.lua chain file at root scope (applies to all targets).

function imakecore_init(proj_dir)
    -- (1) Build the IMAKECORE_* compile-info env table from xmake.
    local platform = is_plat("windows", "macosx", "linux") or os.host()
    local arch = get_config("arch") or os.arch()
    local compiler = get_config("toolchain") or ""
    if compiler == "clang-cl" then
        compiler = "msvc"
    end
    local build_mode = get_config("mode") or "debug"

    local target_type = "executable"
    if is_kind("static") then
        target_type = "static"
    elseif is_kind("shared") then
        target_type = "dynamic"
    end

    local cxxflags = get_config("cxxflags") or ""
    local cpp_std = ""
    local std_flag = cxxflags:match("-std=([^%s]+)")
    if std_flag then
        cpp_std = std_flag:gsub("gnu%+%+", ""):gsub("c%+%+", "")
    end
    local exceptions = "1"
    if cxxflags:find("-fno-exceptions", 1, true) then
        exceptions = "0"
    end
    local rtti = "1"
    if cxxflags:find("-fno-rtti", 1, true) then
        rtti = "0"
    end

    local runtimes = "system"
    if compiler == "msvc" then
        local vs_runtime = get_config("vs_runtime") or ""
        if vs_runtime:find("MD", 1, true) then
            runtimes = "dynamic"
        else
            runtimes = "static"
        end
    end

    local compiler_version = ""
    local cc = get_config("cc") or get_config("cxx")
    if cc then
        try {
            function()
                compiler_version = (os.iorunv(cc, {"-dumpversion"}) or ""):gsub("%s+", "")
            end,
            catch {
                function() compiler_version = "" end
            }
        }
    end

    local imakecore_envs = {
        IMAKECORE_PLATFORM = platform,
        IMAKECORE_ARCH = arch,
        IMAKECORE_COMPILER = compiler,
        IMAKECORE_COMPILER_VERSION = compiler_version,
        IMAKECORE_BUILD_MODE = build_mode,
        IMAKECORE_TARGET_TYPE = target_type,
        IMAKECORE_CPP_STD = cpp_std,
        IMAKECORE_EXCEPTION_ENABLED = exceptions,
        IMAKECORE_RTTI_ENABLED = rtti,
        IMAKECORE_RUNTIMES = runtimes,
    }

    -- (2) Locate IMakeCore.py.
    local script
    local sys_dir = os.getenv("IMAKECORE_SYSTEM")
    if sys_dir and sys_dir ~= "" then
        script = path.join(sys_dir, "IMakeCore.py")
    else
        local root = os.getenv("IMAKECORE_ROOT")
        if root and root ~= "" then
            script = path.join(root, ".system", "IMakeCore.py")
        end
    end
    if not script then
        os.raise("IMakeCore: neither IMAKECORE_SYSTEM nor IMAKECORE_ROOT is set — cannot locate IMakeCore.py")
    end

    -- (3) Locate the Python interpreter.
    import("lib.detect.find_program")
    local python = find_program("python", {paths = {"$(env PATH)"}})
        or find_program("python3")
        or find_program("py")
        or os.getenv("PYTHON")
    if not python then
        os.raise("Python interpreter not found")
    end

    -- (4) Run IMakeCore.py to resolve packages and emit .package.lua.
    local outdata, errdata, failed
    try {
        function()
            outdata, errdata = os.iorunv(python, {"-B", script, proj_dir, "xmake"},
                                         {envs = os.joinenvs(os.getenvs(), imakecore_envs)})
        end,
        catch {
            function(e) failed = tostring(e) end
        }
    }
    -- belt-and-braces: a failure mode that does NOT raise (non-zero exit on
    -- some xmake builds) leaves .package.lua absent on first run — detect it.
    if failed or not os.isfile(path.join(proj_dir, ".package.lua")) then
        os.raise("IMakeCore resolution failed: " .. tostring(failed or "")
                 .. tostring(outdata or "") .. tostring(errdata or ""))
    end

    -- (5) Include the generated chain file (root scope — applies to all targets).
    includes(path.join(proj_dir, ".package.lua"))
end
