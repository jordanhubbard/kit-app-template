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
-- Only define apps that actually exist in _build/apps
define_app("my_company.my_editor.kit")
define_app("test_editor.kit")

define_app("my_company.explorer.kit")
define_app("test.explorer.kit")
define_app("my_company.base_editor.kit")
define_app("foobar.base_editor.kit")
define_app("foo.base_editor.kit")
define_app("blah.base_editor.kit")
define_app("blahblah.composer.kit")
define_app("test.api_validation.kit")
define_app("blahblah.viewer.kit")
define_app("meh.base_editor.kit")
define_app("meh.viewer.kit")
define_app("test_api.base_editor.kit")
define_app("cli_test.editor.kit")
define_app("simple.viewer.kit")