# IMakeCore 测试套件说明

> 运行方式：`python run_all.py [qmake] [cmake] [xmake]`，默认三种都测。
> IDE 入口：用 Qt Creator 打开 `tests.pro` 或 `CMakeLists.txt` 即可导入全部 75 个测试项目。

---

## basic_resolve — 基本包解析 (5 tests)

| 测试 | 说明 |
|------|------|
| `test_single_package_no_deps` | 解析单个 header-only 包（hello@1.0.0），验证 `.package.pri` 生成且包含 hello |
| `test_single_source_package` | 解析单个 source 包（hello@2.0.0，含 .cpp），验证产物 |
| `test_transitive_dependency` | world 依赖 hello → 两个包都被解析，hello 出现在产物中 |
| `test_version_selection_latest` | 版本约束 `>=2.0` → 选择 2.0.0 而非 1.0.0 |
| `test_version_skip` | 版本 `x` → 包被跳过，不出现在产物中 |

---

## static_propagation — Static 模式传播 (2 tests)

| 测试 | 说明 |
|------|------|
| `test_static_propagates` | world (static) → hello 依赖也被标记为 static |
| `test_static_source_cpp` | hello@2.0.0 (source+cpp) 标记 static → 根据验证规则决定是否接受 |

---

## validation — 错误路径校验 (5 tests)

| 测试 | 说明 |
|------|------|
| `test_header_only_rejects_static` | hello@1.0.0 (header-only) + `mode=static` → 报错退出 |
| `test_header_only_rejects_dynamic` | hello@1.0.0 (header-only) + `mode=dynamic` → 报错退出 |
| `test_missing_dependency` | 引用不存在的包 `test/nonexistent` → 报错退出 |
| `test_missing_packages_json` | 项目无 `packages.json` → 优雅失败 |
| `test_dynamic_without_definition` | 标记 dynamic 但包缺少 `dynamicDefinition` → 验证处理 |

---

## version_specifiers — 版本约束 (5 tests)

| 测试 | 说明 |
|------|------|
| `test_wildcard_latest` | `*` → 选最新版本 2.0.0 |
| `test_exact_version` | 精确 `2.0.0` → 精确匹配，1.0.0 不泄露 |
| `test_version_range_lower_bound` | `>=1.0` → 选 2.0.0 |
| `test_version_range_restricted` | `>=1.0,<2.0` → 只能选 1.0.0（2.0.0 被排除） |
| `test_version_skip_x` | `x` → 跳过包 |

---

## cmake_output — CMake 输出 (3 tests)

| 测试 | 说明 |
|------|------|
| `test_cmake_single_package` | CMake 模式下解析 hello@1.0.0 → 生成 `.package.cmake` |
| `test_cmake_transitive` | CMake 模式下 world→hello 传递依赖 |
| `test_cmake_version_select` | CMake 模式下版本选择 `>=2.0` → 2.0.0 |

---

## xmake_output — XMake 输出 (4 tests)

| 测试 | 说明 |
|------|------|
| `test_xmake_single_package` | xmake 模式下解析 hello@1.0.0 → 生成 `.package.xmake` + includes 链 + add_includedirs/add_headerfiles |
| `test_xmake_transitive` | xmake 模式下 world→hello 传递依赖 |
| `test_xmake_version_select` | xmake 模式下版本选择 `>=2.0` → 2.0.0 |
| `test_xmake_static_link_contract` | static 库：add_linkdirs 与 set_targetdir 解析到同一目录，add_links/set_basename safe_name 一致 |

---

## local_origin — Local Origin 复制 (3 tests)

| 测试 | 说明 |
|------|------|
| `test_local_origin_copies_package` | `origin=local` → 从系统 `.lib/` 复制包到项目 `.lib/` |
| `test_local_origin_without_system_package` | `origin=local` 但包不存在 → 报错 |
| `test_local_origin_already_in_local` | `origin=local` 且包已在本地 → 直接使用已有的 |

---

## advanced_resolve — 高级解析 (4 tests)

| 测试 | 说明 |
|------|------|
| `test_publisher_scope` | 使用 `test/hello` publisher 前缀 → 正确解析 |
| `test_mode_default_explicit` | 显式 `mode=default` → 等同于未指定 |
| `test_two_independent_packages` | 两个无关联包同时解析 → 都出现在产物中 |
| `test_transitive_with_versions` | world 依赖 hello>=1.0 → 选最新但正确解析 |

---

## path_resolve — 路径解析 (3 tests)

| 测试 | 说明 |
|------|------|
| `test_path_resolve_header_only` | 通过 `path` 字段直接引用 fixture 目录 → 解析成功 |
| `test_path_resolve_source_package` | 通过 `path` 引用 source 包 → 解析成功 |
| `test_path_resolve_nonexistent` | 引用不存在的路径 → 报错退出 |

---

## static_chain — 深层 Static 链 (5 tests)
| 测试 | 说明 |
|------|------|
| `test_static_propagates_to_dep` | world (static) → hello，两者都正确解析 |
| `test_source_marked_static` | hello@2.0.0 (source+cpp) 显式标记 static → 可接受 |
| `test_static_skips_dynamic_dep` | static world + dynamic_lib 共存 |
| `test_source_mode_explicit` | 显式 `mode=source` → 正常解析 |
| `test_static_chain_rejects_source_dep` | world (static) → hello (source) → 报错：source 不应在 static 链中 |

---

## package_json — package.json 字段测试 (14 tests)

| 测试 | 说明 |
|------|------|
| `test_required_fields_present` | 最小有效包（name+version+publisher）→ 解析成功 |
| `test_summary_field` | summary 字段不影响解析 |
| `test_dependencies_field` | 依赖字段正确传递 → 传递解析 |
| `test_mode_sources` | `mode="sources"` → 等同 `"source"` |
| `test_mode_static_only` | `mode=["static"]` → 仅静态库模式 |
| `test_mode_dual_source_static` | `mode=["source","static"]` → 双模式 |
| `test_mode_dynamic` | `mode=["dynamic"]` → 动态库模式 |
| `test_resolve_explicit_files` | resolve 显式 headers+sources+definitions+includePaths |
| `test_resolve_root_field` | resolve root + ignore → 限制扫描范围 |
| `test_resolve_precompile_headers` | resolve precompileHeaders → 预编译头配置 |
| `test_resolve_dynamic_definition` | resolve dynamicDefinition → 动态库定义 |
| `test_invalid_missing_version` | fixture 缺 version → updateDb 跳过不崩溃 |
| `test_invalid_origin` | packages.json 中 `origin="invalid"` → 报错 |
| `test_invalid_mode_in_config` | packages.json 中 `mode="nonexistent"` → 报错 |
