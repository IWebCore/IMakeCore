-- IMakeCore xmake integration
--
-- Include from a project's xmake.lua:
--   local imake = os.getenv("IXMakeCore")
--   if imake then includes(imake) end
-- then add the rule to each target:
--   target("myapp")
--       add_rules("imakecore")
--
-- The rule's on_load hook runs in xmake's SCRIPT domain — the only place
-- commands (python) can be executed. It resolves packages.json by running
-- IMakeCore.py, reads the machine-readable .package.xmake.json it emits, and
-- applies include dirs / defines / files / links via target:add().

rule("imakecore")
    on_load(function (target)
        import("lib.detect.find_program")

        -- Locate the Python interpreter.
        local python = find_program("python", {paths = {"$(env PATH)"}})
            or find_program("python3")
            or find_program("py")
            or os.getenv("PYTHON")
        if not python then
            os.raise("IMakeCore: Python interpreter not found")
        end

        -- Locate IMakeCore.py.
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

        -- The target's defining xmake.lua directory holds its packages.json.
        local proj_dir = target:scriptdir()

        -- Resolve packages (generates .package.lua + .package.xmake.json).
        -- os.iorunv raises on failure, propagating a clear error.
        os.iorunv(python, {"-B", script, proj_dir, "xmake"})

        -- Read the resolved config emitted by the Python engine.
        local json = import("core.base.json")
        local data = json.loadfile(path.join(proj_dir, ".package.xmake.json")) or {}

        -- Apply settings to the target.
        for _, pkg in ipairs(data) do
            for _, inc in ipairs(pkg.includes or {}) do
                target:add("includedirs", inc)
            end
            for _, d in ipairs(pkg.definitions or {}) do
                target:add("defines", d)
            end
            for _, h in ipairs(pkg.headers or {}) do
                target:add("headerfiles", h)
            end
            for _, f in ipairs(pkg.sources or {}) do
                target:add("files", f)
            end
            for _, ph in ipairs(pkg.precompile_headers or {}) do
                target:add("pcxxheader", ph)
            end
            for _, l in ipairs(pkg.links or {}) do
                target:add("links", l)
            end
            if pkg.linkdir and pkg.linkdir ~= "" then
                target:add("linkdirs", path.join(proj_dir, pkg.linkdir,
                    os.arch() .. "-" .. os.host() .. "-" .. pkg.mode))
            end
        end
    end)
