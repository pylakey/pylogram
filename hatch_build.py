import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

# Add the current directory to the path, so we can import the compiler.
sys.path.insert(0, ".")


class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data):
        """Initialize the hook."""
        if self.target_name in {"install"}:
            return

        from compiler.api.compiler import start as compile_api
        from compiler.errors.compiler import start as compile_errors

        print("compiling api")
        compile_api()
        print("compiled api")

        print("compiling errors")
        compile_errors()
        print("compiled errors")
