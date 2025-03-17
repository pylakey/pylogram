import os
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

# Add the current directory to the path, so we can import the compiler.
sys.path.insert(0, ".")


class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data):
        """Initialize the hook."""
        if self.target_name not in {"wheel", "install"}:
            return

        from compiler.api.compiler import start as compile_api
        from compiler.errors.compiler import start as compile_errors

        compile_api()
        compile_errors()

    def finalize(self, version, build_data, artifact_path):
        """Finalize the build by adjusting the metadata."""
        if artifact_path and os.path.exists(artifact_path):
            if self.target_name == "wheel":
                self._fix_wheel_metadata(artifact_path)
            elif self.target_name == "sdist":
                self._fix_sdist_metadata(artifact_path)

    def _fix_wheel_metadata(self, artifact_path):
        """Fix metadata in wheel file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(artifact_path, "r") as wheel:
                wheel.extractall(tmpdir)

            # Find the METADATA file
            metadata_files = list(Path(tmpdir).glob("*.dist-info/METADATA"))
            if metadata_files:
                metadata_path = metadata_files[0]

                # Read the current metadata
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata_content = f.read()

                # Remove problematic license entries
                fixed_lines = []
                for line in metadata_content.splitlines():
                    if not line.startswith("License-File:") and not line.startswith(
                        "License-Expression:"
                    ):
                        fixed_lines.append(line)

                # Write back the fixed metadata
                with open(metadata_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(fixed_lines))

                # Recreate the wheel with fixed metadata
                with zipfile.ZipFile(artifact_path, "w") as new_wheel:
                    for root, _, files in os.walk(tmpdir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, tmpdir)
                            new_wheel.write(file_path, arcname)

    def _fix_sdist_metadata(self, artifact_path):
        """Fix metadata in source distribution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract the tarball
            with tarfile.open(artifact_path, "r:gz") as tar:
                tar.extractall(path=tmpdir)

            # Find the PKG-INFO file (should be at the root of the extracted directory)
            pkg_info_files = []
            for root, _, files in os.walk(tmpdir):
                if "PKG-INFO" in files:
                    pkg_info_files.append(os.path.join(root, "PKG-INFO"))

            if pkg_info_files:
                pkg_info_path = pkg_info_files[0]

                # Read the current metadata
                with open(pkg_info_path, "r", encoding="utf-8") as f:
                    metadata_content = f.read()

                # Remove problematic license entries
                fixed_lines = []
                for line in metadata_content.splitlines():
                    if not line.startswith("License-File:") and not line.startswith(
                        "License-Expression:"
                    ):
                        fixed_lines.append(line)

                # Write back the fixed metadata
                with open(pkg_info_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(fixed_lines))

                # Recreate the tarball with fixed metadata
                main_dir = os.path.basename(os.path.dirname(pkg_info_path))
                original_dir = os.getcwd()
                try:
                    os.chdir(tmpdir)

                    with tarfile.open(artifact_path, "w:gz") as new_tar:
                        new_tar.add(main_dir)

                finally:
                    os.chdir(original_dir)
