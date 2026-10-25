import subprocess as sb
import re
sb.run(
    "rundll32.exe user32.dll,LockWorkStation",
    shell=True,
)