# Audit Finding Configuration & Few-Shot Examples

# 1. Common GMP Violations (Applied to ALL logs)
COMMON_EXAMPLES = [
    {
        "scenario": "Data Deletion without Reason",
        "log_snippet": "2024-02-07 14:00 | User: Admin | Action: Delete File 'Run_23.dat'",
        "analysis": "User 'Admin' deleted raw data file 'Run_23.dat' without documenting a reason (e.g., 'invalid run due to leak'). This violates 21 CFR Part 11.10(e) and ALCOA+ 'Original' principle.",
        "severity": "CRITICAL"
    },
    {
        "scenario": "Testing into Compliance",
        "log_snippet": "2024-02-07 14:05 | Action: Sequence Aborted\n2024-02-07 14:10 | Action: Sequence Started (Pass)",
        "analysis": "Sequence was aborted and immediately restarted to achieve a passing result. This indicates potential 'Testing into Compliance'.",
        "severity": "MAJOR"
    },
    {
        "scenario": "Back-dating (Time Manipulation)",
        "log_snippet": "2024-02-07 09:00 | System | Action: Clock Changed from 2024-02-07 09:00 to 2024-02-06 09:00",
        "analysis": "System clock was manually changed to a past date. This is a critical indication of data falsification (Back-dating).",
        "severity": "CRITICAL"
    }
]

# 2. Equipment Specific Examples (Future Expansion)
# These can be dynamically loaded based on user selection in the UI.

HPLC_EXAMPLES = [
    {
        "scenario": "Unjustified Manual Integration",
        "log_snippet": "User: Analyst1 | Action: Manual Integration | Reason: <Empty>",
        "analysis": "Manual integration performed without a documented scientific justification. Requires review.",
        "severity": "MAJOR"
    }
]

BALANCE_EXAMPLES = [
    {
        "scenario": "Repeat Weighing (Picking)",
        "log_snippet": "Weight: 20.1g (Print) -> Weight: 19.9g (No Print) -> Weight: 20.0g (Print)",
        "analysis": "Multiple weighings were performed but only the compliant result (20.0g) was printed/saved. Potential 'Testing into Compliance'.",
        "severity": "MAJOR"
    }
]

def get_examples(equipment_type="COMMON"):
    """
    Returns the appropriate examples based on equipment type.
    """
    examples = COMMON_EXAMPLES.copy()
    
    if equipment_type == "HPLC":
        examples.extend(HPLC_EXAMPLES)
    elif equipment_type == "BALANCE":
        examples.extend(BALANCE_EXAMPLES)
    
    return examples
