-- Shared build scripts from repo_build package.
repo_build = require("omni/repo/build")

-- Repo root
root = repo_build.get_abs_path(".")

-- Run repo_kit_tools premake5-kit that includes a bunch of Kit-friendly tooling configuration.
kit = require("_repo/deps/repo_kit_tools/kit-template/premake5-kit")
kit.setup_all({ cppdialect = "C++17" })

-- After setup_all, define_app is now available from kit-kernel's premake5-public.lua
-- Save the original and override it to support nested directory structure
local _original_define_app = define_app

function define_app(kitfile, args)
    local args = args or {}
    local app_name = kitfile:match("(.+)%.kit$") or kitfile
    local subfolder = args.subfolder or "apps"

    -- Override to use nested structure (new default): apps/{name}/{name}.kit
    -- This matches the _fix_application_structure behavior in repo_dispatcher.py
    local nested_config_path = subfolder .. "/" .. app_name .. "/" .. kitfile

    -- Set the config_path to nested structure
    args.config_path = nested_config_path

    -- The original define_app expects to construct config_path itself, but we've
    -- pre-set it. Looking at the original code, it sets args.config_path unconditionally.
    -- So we need to call define_experience directly instead
    define_experience(kitfile, args)

    -- Also handle test generation (copied from original define_app)
    local define_test = (args.define_test == nil) and true or args.define_test
    if define_test then
        local test_args = args.test_args or {}
        define_ext_test_experience(kitfile, test_args)
    end

    local add_profile_startup_script = args.add_profile_startup_script or false
    if add_profile_startup_script then
        create_app_profile_startup_script(kitfile..".profile_startup", args)
    end
end


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
define_app("platform_test.editor.kit")
define_app("aligned_path.editor.kit")
define_app("basebase.base_editor.kit")
define_app("final_test.editor.kit")
define_app("blahblah.base_editor.kit")
define_app("baser.base_editor.kit")
define_app("base.base_editor.kit")
define_app("my_company.viewer.kit")
define_app("boop.omni_usd_viewer_8818.kit")
define_app("boopness.viewer.kit")
define_app("blah.viewer.kit")
define_app("my_company.my_first_app.kit")
define_app("my_company.my_first_viewer.kit")
define_app("my_company.composer.kit")
define_app("foo.viewer.kit")
define_app("test.viewer.kit")
define_app("foobar.viewer.kit")
define_app("my.viewer.kit")
define_app("compose.composer.kit")