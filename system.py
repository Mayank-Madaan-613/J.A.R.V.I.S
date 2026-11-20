import subprocess as sb
import re
import re

def parse_system_command(query: str) -> dict:
    """
    Parses a 'system_cmd' utterance into a structured action dictionary:
    {'action': str, 'target': str | None, 'value': int | str | None}
    """
    clean_query = query.lower().strip()

    # Ordered from most specific patterns to broader catch-alls
    rules = [
        # 1. File / Folder Search: "find file report.pdf", "where is image screenshot.png stored"
        {
            "action": "file_search",
            "pattern": r"(?:find|search\s+(?:for|my\s+computer\s+for)?|locate|where\s+is)\s+(?:the\s+)?(?:file|folder|document|python\s+script|script|image)?\s*(?P<target>[\w\.\-\s]+?)(?:\s+on\s+my\s+pc|\s+stored)?$"
        },

        # 2. Process Kill / Close: "shutdown chrome", "kill python process", "force quit spotify"
        {
            "action": "process_kill",
            "pattern": r"(?:close|kill|terminate|stop|shutdown|force\s+quit|exit)\s+(?:all\s+active\s+|running\s+)?(?P<target>[\w\s]+)"
        },

        # 3. Volume Controls (Absolute, Relative, Mute): "set volume to 50 percent", "mute system audio"
        {
            "action": "volume_control",
            "pattern": r"(?:(?P<value>mute|unmute)\s*(?:system|audio|volume)?|(?:set\s+volume\s+to|volume)\s+(?P<target>\d+)\s*(?:percent|%)?|turn\s+volume\s+(?P<dir>up|down))"
        },

        # 4. Brightness Controls: "increase brightness by 20 percent", "set screen brightness to max", "dim the screen"
        {
            "action": "brightness_control",
            "pattern": r"(?:(?P<dir>increase|decrease|dim)\s+(?:screen\s+|the\s+)?(?:brightness|screen)(?:\s+by\s+(?P<target>\d+)\s*(?:percent|%)?)?|(?:set\s+(?:screen\s+)?brightness\s+to)\s+(?P<value>\d+|max|min|maximum|minimum)\s*(?:percent|%)?)"
        },

        # 5. System Status & Hardware Monitoring: "check CPU usage", "how much RAM am I using", "battery level"
        {
            "action": "system_status",
            "pattern": r"(?:check|what\s+is\s+(?:my)?|how\s+much|how\s+long\s+has\s+(?:the\s+)?(?:computer|pc)\s+been)\s*(?P<target>cpu\s+usage|ram|memory|battery\s+(?:percentage|level)|system\s+status|running|uptime)"
        },

        {
            "action": "power_control",
            "pattern": r"(?P<target>lock|sleep|shutdown|shut\s+down|restart|reboot)(?:\s+(?:my\s+|the\s+)?(?:pc|computer|system|screen|now))*"
        }
    ]

    for rule in rules:
        match = re.search(rule["pattern"], clean_query)
        if match:
            groups = match.groupdict()
            action = rule["action"]
            target = groups.get("target")
            value = groups.get("value") or groups.get("dir")

            if action == "process_kill" and target:
                target = re.sub(r"\b(process|browser|app|application|player)\b", "", target).strip()

            if action == "system_status" and target:
                if "cpu" in target:
                    target = "cpu"
                elif "ram" in target or "memory" in target:
                    target = "ram"
                elif "battery" in target:
                    target = "battery"
                elif "running" in target or "uptime" in target:
                    target = "uptime"

            return {
                "action": action,
                "target": target.strip() if target else None,
                "value": value.strip() if value else None
            }

    return {"action": "unknown", "target": None, "value": None}


test_commands = [
    "find file report.pdf",
    "search for document budget.xlsx on my pc",
    "where is image screenshot.png stored",
    "shutdown chrome",
    "kill python process",
    "force quit spotify",
    "set volume to 50 percent",
    "mute system audio",
    "turn volume up",
    "increase brightness by 20 percent",
    "set screen brightness to max",
    "dim the screen",
    "check CPU usage",
    "how much RAM am I using",
    "what is my battery level",
    "how long has the computer been running",
    "lock my PC",
    "put computer to sleep",
    "restart the computer"
]

print(f"{'VOICE COMMAND':<45} | {'ACTION':<18} | {'TARGET':<16} | {'VALUE'}")
print("-" * 95)
for cmd in test_commands:
    res = parse_system_command(cmd)
    print(f"{cmd:<45} | {res['action']:<18} | {str(res['target']):<16} | {res['value']}")