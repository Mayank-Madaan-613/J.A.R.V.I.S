import re
import math
WORD_TO_NUM = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "fifteen": "15",
    "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50",
    "hundred": "100", "thousand": "1000"
}

def normalize_numbers(text: str) -> str:
    """Converts standalone spoken single-word numbers to numeric digits."""
    words = text.lower().split()
    normalized = [WORD_TO_NUM.get(w, w) for w in words]
    return " ".join(normalized)

def extract_math_components(query: str) -> dict:
    """
    Extracts operands and operation from a math calculation voice query.
    Returns a dictionary with 'operands', 'operation', and 'normalized_expression'.
    """
    clean_text = normalize_numbers(query)

    patterns = [
        
        {
            "regex": r"(?P<op1>\d+(?:\.\d+)?)\s*(?:percent|%)\s*(?:of|on)?\s*(?P<op2>\d+(?:\.\d+)?)",
            "op_label": "percentage",
            "symbol": "%"
        },
        
        {
            "regex": r"(?:square\s+root|sqrt)\s+(?:of\s+)?(?P<op1>\d+(?:\.\d+)?)",
            "op_label": "square_root",
            "symbol": "sqrt"
        },
        {
            "regex": r"(?P<op1>\d+(?:\.\d+)?)\s*(?:to\s+the\s+power\s+of|raised\s+to|squared|cubed)\s*(?P<op2>\d+(?:\.\d+)?)?",
            "op_label": "power",
            "symbol": "^"
        },
        {
            "regex": r"(?P<op1>\d+(?:\.\d+)?)\s*(?P<op_word>plus|\+|minus|-|times|multiplied\s+by|\*|x|divided\s+by|divide|by|/)\s*(?P<op2>\d+(?:\.\d+)?)",
            "op_label": "binary_operation",
            "symbol": None
        }
    ]

    op_map = {
        "plus": "+", "+": "+",
        "minus": "-", "-": "-",
        "times": "*", "multiplied by": "*", "x": "*", "*": "*",
        "divided by": "/", "divide": "/", "by": "/", "/": "/"
    }

    for p in patterns:
        match = re.search(p["regex"], clean_text, re.IGNORECASE)
        if match:
            groups = match.groupdict()
            op1 = groups.get("op1")
            op2 = groups.get("op2")
            
            if p["op_label"] == "binary_operation":
                raw_op = groups.get("op_word", "").strip().lower()
                op_symbol = op_map.get(raw_op, raw_op)
                op_label = {
                    "+": "addition",
                    "-": "subtraction",
                    "*": "multiplication",
                    "/": "division"
                }.get(op_symbol, "binary")
            else:
                op_symbol = p["symbol"]
                op_label = p["op_label"]

            if op_label == "power" and not op2:
                if "squared" in clean_text:
                    op2 = "2"
                elif "cubed" in clean_text:
                    op2 = "3"

            operands = [float(o) if "." in o else int(o) for o in [op1, op2] if o is not None]

            if op_label == "percentage":
                expr = (operands[0] / 100) * operands[1]
            elif op_label == "square_root":
                expr = math.sqrt(operands[0])
            elif op_label == "power":
                expr = operands[0] ** operands[1]
            elif op_label=="addition":
                expr = operands[0]+operands[1]
            elif op_label=="subtraction":
                expr = operands[0]-operands[1]
            elif op_label=="multiplication":
                expr = operands[0]*operands[1]
            elif op_label=="division":
                expr = operands[0]/operands[1]

            return {
                "operation": op_label,
                "operands": operands,
                "res": expr
            }

    return {"operation": None, "operands": [], "expression": None}
def calc(query):
    det=extract_math_components(query)
    

# test cases 8
test_queries = [
    "what is 25 plus 45",
    "calculate 120 minus 35",
    "what is 15 times 8",
    "divide 500 by 25",
    "what is 15 percent of 2500",
    "square root of 144",
    "what is 29 to the power of 10",
    "calculate nine squared",
    "what is 5 cubed"
]

if __name__=="__main__":
    print(f"{'QUERY':<32} | {'OPERATION':<16} | {'OPERANDS':<12} | {'EXPRESSION'}")
    print("-" * 80)
    for q in test_queries:
        res = extract_math_components(q)
        print(f"{q:<32} | {str(res['operation']):<16} | {str(res['operands']):<12} | {res['res']}")