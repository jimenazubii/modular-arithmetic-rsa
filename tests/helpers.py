from io import StringIO

import imatlab


def run(command: str, detallado: bool = False) -> str:
    """Runs one IMAT-LAB command in batch mode and returns its output line."""
    out = StringIO()
    imatlab.run_commands(StringIO(command + "\n"), out, detallado=detallado)
    return out.getvalue().rstrip("\n")
