#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path
home = os.path.expanduser("~")
binfolder = os.path.join(home, ".local", "bin")

HOME = Path.home()
LOCAL_BIN = str(HOME / ".local" / "bin")
BACKUP_SUFFIX = ".backup-before-add-local-bin"

def detect_shell():
    shell_env = os.environ.get("SHELL")
    if shell_env:
        return Path(shell_env).name  # ex: "/bin/zsh" -> "zsh"

    try:
        ppid = os.getppid()
        exe_path = os.readlink(f"/proc/{ppid}/exe")
        return Path(exe_path).name
    except Exception:
        pass

    return "sh"

def rc_file_for_shell(shell_name: str) -> Path:
    shell_name = shell_name.lower()
    if shell_name in ("bash",):
        return HOME / ".bashrc"
    if shell_name in ("zsh",):
        return HOME / ".zshrc"
    if shell_name in ("fish",):
        return HOME / ".config" / "fish" / "config.fish"
    if shell_name in ("ksh",):
        return HOME / ".kshrc"
    return HOME / ".profile"

def line_for_shell(shell_name: str) -> str:
    shell_name = shell_name.lower()
    if shell_name == "fish":
        return f'\n# Added by Pysvrscrpit\nset -gx PATH $HOME/.local/bin $PATH\n'
    else:
        return (
            f'\n# Added by add_local_bin_to_path.py\n'
            f'if [ -d "$HOME/.local/bin" ] && ! echo "$PATH" | /bin/grep -q "$HOME/.local/bin"; then\n'
            f'    export PATH="$HOME/.local/bin:$PATH"\n'
            f'fi\n'
        )

def ensure_dir_for_file(path: Path):
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

def add_line_to_rc(rc_path: Path, content: str):
    ensure_dir_for_file(rc_path)
    if not rc_path.exists():
        rc_path.write_text("")  # cria vazio

    current = rc_path.read_text()
    if LOCAL_BIN in current:
        print(f"{rc_path} aready has {LOCAL_BIN}. nothing to do.")
        return

    backup_path = rc_path.with_suffix(rc_path.suffix + BACKUP_SUFFIX)
    try:
        shutil.copy2(rc_path, backup_path)
        print(f"Backup made at: {backup_path}")
    except Exception as e:
        print(f"couldnt make the backup off {rc_path}: {e}")

    with rc_path.open("a", encoding="utf-8") as f:
        f.write(content)
    print(f"Adding line to {rc_path}.")


def main():
    shell = detect_shell()
    rc = rc_file_for_shell(shell)
    block = line_for_shell(shell)

    print(f"Detecting shell: {shell}")
    print(f"rcfile Chosen: {rc}")

    add_line_to_rc(rc, block)

    if shell == "fish":
        print("\nFor loading the changes in path run:\n  source ~/.config/fish/config.fish")
    elif shell in ("bash", "zsh", "ksh"):
        print(f"\nFor loading the changes in path run:\n  source {rc}")
    else:
        print(f"\nOpen a new terminal, or run:\n  source {rc}\npara aplicar as mudanças.")

if __name__ == "__main__":
    main()


# Adding to path part :D 
shutil.copy("pysrvstart", os.path.join(binfolder, "pysrvstart"))
shell = os.environ.get("SHELL", "")

if "bash" in shell:
    subprocess.run(["bash"])
elif "zsh" in shell:
    subprocess.run(["zsh"])
else:
    print("Cant find SHELL, so will use bash instead")
    subprocess.run(["bash"])
