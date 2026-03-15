import os
import subprocess


class TestHelp:
    @staticmethod
    def test_top_level():
        proc = subprocess.run(
            ["prfs"],
            capture_output=True,
            text=True,
            # Colored output screws up assertions on the CI because it detects there's no TTY.
            env={**os.environ, "NO_COLOR": "1"},
        )
        assert "Usage: prfs" in proc.stdout
        assert "--help" in proc.stdout
        assert "fetch" in proc.stdout
        assert "clean" in proc.stdout

    @staticmethod
    def test_help():
        proc = subprocess.run(["prfs", "--help"], capture_output=True, text=True)
        assert "Usage:" in proc.stdout
