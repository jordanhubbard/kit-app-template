-- Shared build scripts from repo_build package.
repo_build = require("omni/repo/build")

-- Repo root
root = repo_build.get_abs_path(".")

-- Run repo_kit_tools premake5-kit that includes a bunch of Kit-friendly tooling configuration.
kit = require("_repo/deps/repo_kit_tools/kit-template/premake5-kit")
kit.setup_all({ cppdialect = "C++17" })


-- Registries config for testing
repo_build.prebuild_copy {
    { "%{root}/tools/deps/user.toml", "%{root}/_build/deps/user.toml" },
}

-- Apps: for each app generate batch files and a project based on kit files (e.g. my_name.my_app.kit)

-- Add your application .kit files here like: define_app("my_company.my_app.kit")
define_app("my_company.my_editor.kit")
define_app("test.app.kit")
define_app("test.app2.kit")
define_app("test.composer.kit")
define_app("curl.test.kit")
define_app("my_company.viewer.kit")
define_app("my_company.base_editor.kit")
define_app("my_company.kit_base_editor_4396.kit")
define_app("dork.whistle.kit")
define_app("test.docfix.kit")
define_app("test.unixflow.kit")
define_app("test.wrapper.kit")
define_app("test.quick_validation.kit")