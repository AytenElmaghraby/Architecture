# Digital Logic Design Project
import itertools  # we need this to make all the input combinations
from sympy import Symbol, Not, And, Or
from sympy.logic import SOPform, simplify_logic

# ======================================================
# Part 1: asking the user for the number of inputs
# ======================================================
MIN_INPUTS = 1
MAX_INPUTS = 5  # biggest number of variables we support (we can change it later)


def get_number_of_inputs():
    # what it does: asks the user for the number of input variables (n)
    #               and keeps asking until the user enters a valid number
    # it takes: nothing
    # it returns: n (a whole number between MIN_INPUTS and MAX_INPUTS)

    # keep asking until the user enters a valid number
    while True:
        value = input("Enter the number of input variables (1-5): ")
        # remove extra spaces from the start and the end
        value = value.strip()
        # check if the user left it empty
        if value == "":
            print("Error: you didn't enter anything, try again.")
            continue
        # try to change the text to an integer
        try:
            n = int(value)
        except ValueError:
            # this happens if the user typed letters or a decimal like 3.5
            print("Error: please enter a whole number only.")
            continue
        # check that the number is in the allowed range
        if n < MIN_INPUTS or n > MAX_INPUTS:
            print("Error: the number must be between 1 and 5.")
            continue
        # if we reached here the input is valid
        return n


# ======================================================
# Part 2: the inputs side of the truth table
# ======================================================
def get_variable_names(n):
    # what it does: gives us the names of the variables (A, B, C, ...)
    # it takes: n (the number of inputs)
    # it returns: a list of n names, for example n = 3 gives ["A", "B", "C"]

    # take only the first n names from the list (for n = 3 we get A, B, C)
    return ["A", "B", "C", "D", "E"][:n]


def generate_combinations(n):
    # what it does: makes all the possible 0/1 combinations of the inputs
    #               (this is the left side of the truth table)
    # it takes: n (the number of inputs)
    # it returns: a list of 2^n rows, for example n = 2 gives
    #             [(0,0), (0,1), (1,0), (1,1)]

    # make all the 0/1 combinations for n inputs (the number of rows is 2^n)
    return list(itertools.product([0, 1], repeat=n))


# ======================================================
# Part 3: reading the boolean expression
# ======================================================

# symbols that are allowed in the expression (we will change them if the doctor wants other symbols)
# ' is NOT, + is OR, . and * are AND
ALLOWED_SYMBOLS = ["'", "+", ".", "*", "(", ")", " "]


def read_expression(names):
    # what it does: asks the user to enter the boolean expression
    #               and checks that it is written correctly
    # it takes: names (the variable names, for example ["A", "B", "C"])
    # it returns: the expression as text, for example "A'B + AC"

    # keep asking until the user enters a valid expression
    while True:
        text = input("Enter the boolean expression (example: A'B + AC): ")

        # remove extra spaces and change small letters to capital letters
        text = text.strip().upper()

        # check if the user left it empty
        if text == "":
            print("Error: you didn't enter anything, try again.")
            continue

        is_valid = True

        # check 1: every character must be a variable or an allowed symbol
        for ch in text:
            if ch not in names and ch not in ALLOWED_SYMBOLS:
                print("Error: the character '" + ch + "' is not allowed.")
                is_valid = False
                break

        # check 2: the brackets must be balanced
        if is_valid:
            counter = 0
            for ch in text:
                if ch == "(":
                    counter += 1
                elif ch == ")":
                    counter -= 1
                if counter < 0:  # a ")" came before its "("
                    break
            if counter != 0:
                print("Error: the brackets are not balanced.")
                is_valid = False

        # check 3: try to calculate it once, if it fails the form is wrong
        # (example: "A++B" or "A+")
        if is_valid:
            try:
                test_values = {name: 0 for name in names}
                result = eval(
                    convert_expression(text), {"N": lambda x: 1 - x}, test_values
                )
                if result not in (0, 1):
                    raise ValueError
            except Exception:
                print("Error: the expression is not written correctly.")
                is_valid = False

        # if every check passed we return the text
        if is_valid:
            return text


def print_truth_table(names, rows, outputs):
    # what it does: prints the full truth table on the screen
    # it takes: names (the variable names), rows (the input combinations)
    #           and outputs (the output column, a list of 0 and 1)
    # it returns: nothing, it only prints

    # print the header line
    print(" ".join(names) + " | F")

    # print every row with its output
    for i in range(len(rows)):
        bits = " ".join(str(b) for b in rows[i])
        print(bits + " | " + str(outputs[i]))


# ======================================================
# Part 4: calculating the outputs
# ======================================================
def convert_expression(text):
    # what it does: changes our expression to a python expression
    #               A'B + AC  becomes  N(A)&B|A&C
    #               (N means NOT, & means AND, | means OR)
    # it takes: text (the expression)
    # it returns: the python expression as text

    text = text.replace(" ", "")
    out = []  # the pieces of the python expression
    stack = []  # the places of the "(" that are still open
    unit = 0  # where the last variable or bracket group started
    prev = ""  # the character before the current one

    for ch in text:
        if ch.isalpha():
            # two things next to each other mean AND (like AB or A(B+C))
            if prev.isalpha() or prev == ")" or prev == "'":
                out.append("&")
            unit = len(out)
            out.append(ch)
        elif ch == "(":
            if prev.isalpha() or prev == ")" or prev == "'":
                out.append("&")
            stack.append(len(out))
            out.append("(")
        elif ch == ")":
            out.append(")")
            unit = stack.pop()  # the group started at the matching "("
        elif ch == "'":
            # put N( before the last variable/group and ) after it
            out.insert(unit, "N(")
            out.append(")")
        elif ch == "+":
            out.append("|")
        elif ch == "." or ch == "*":
            out.append("&")
        prev = ch

    return "".join(out)


def calculate_outputs(names, rows, expression):
    # what it does: calculates F for every row of the truth table
    # it takes: names, rows, expression
    # it returns: a list of 0 and 1 (the output column)

    python_expression = convert_expression(expression)
    outputs = []
    for row in rows:
        values = dict(zip(names, row))  # for example {"A": 0, "B": 1}
        result = eval(python_expression, {"N": lambda x: 1 - x}, values)
        outputs.append(result)
    return outputs


# ======================================================
# Part 5: simplifying (we use sympy for the hard work)
# ======================================================
def sympy_to_terms(expr):
    # what it does: changes a sympy expression to a simple list of terms
    #               A'B + AC  becomes  [[("A", True), ("B", False)], [("A", False), ("C", False)]]
    #               (True means the variable has a NOT on it)
    # it takes: expr (a sympy expression in sum-of-products form)
    # it returns: a list of terms ([] means F = 0, [[]] means F = 1)

    if expr == False:
        return []
    if expr == True:
        return [[]]

    # the expression is an OR of AND terms (or just one term)
    if isinstance(expr, Or):
        products = expr.args
    else:
        products = [expr]

    terms = []
    for product in products:
        if isinstance(product, And):
            literals = product.args
        else:
            literals = [product]
        term = []
        for lit in literals:
            if isinstance(lit, Not):
                term.append((str(lit.args[0]), True))
            else:
                term.append((str(lit), False))
        term.sort()
        terms.append(term)
    terms.sort()
    return terms


def literal_text(name, negated):
    # returns "A'" if negated, otherwise "A"
    if negated:
        return name + "'"
    return name


def terms_to_text(terms):
    # what it does: changes the list of terms to a readable expression
    if terms == []:
        return "0"
    if terms == [[]]:
        return "1"
    parts = []
    for term in terms:
        parts.append("".join(literal_text(n, neg) for n, neg in term))
    return " + ".join(parts)


def get_simplified_terms(names, outputs):
    # what it does: simplifies the function using minterms (Quine-McCluskey)
    #               this gives the same result as grouping in a K-Map
    # it takes: names, outputs
    # it returns: the simplified terms
    symbols = [Symbol(name) for name in names]
    minterms = [i for i in range(len(outputs)) if outputs[i] == 1]
    return sympy_to_terms(SOPform(symbols, minterms))


# ======================================================
# Part 6: menu option 1 - simplify using K-Map
# ======================================================
def gray_code(k):
    # what it does: makes the gray code of k bits (only one bit changes each step)
    #               k = 2 gives ["00", "01", "11", "10"]
    if k == 0:
        return [""]
    return [format(i ^ (i >> 1), "0" + str(k) + "b") for i in range(2**k)]


def print_kmap(names, outputs):
    # what it does: prints the K-Map table
    n = len(names)
    row_count = n // 2  # variables on the side
    col_count = n - row_count  # variables on the top
    row_codes = gray_code(row_count)
    col_codes = gray_code(col_count)

    corner = "".join(names[:row_count]) + "\\" + "".join(names[row_count:])
    print(corner.ljust(8) + "".join(c.ljust(6) for c in col_codes))
    for r in row_codes:
        line = r.ljust(8)
        for c in col_codes:
            index = int(r + c, 2)  # the row number in the truth table
            line += str(outputs[index]).ljust(6)
        print(line)


def simplify_kmap(names, outputs):
    print("\nK-Map:")
    print_kmap(names, outputs)
    terms = get_simplified_terms(names, outputs)
    print("\nSimplified expression (groups of 1s):")
    print("F = " + terms_to_text(terms))


# ======================================================
# Part 7: menu option 2 - simplify using Boolean Algebra
# ======================================================
def simplify_algebra(names, expression):
    # what it does: simplifies the expression the user wrote using boolean algebra laws
    symbols = {name: Symbol(name) for name in names}
    expr = eval(convert_expression(expression), {"N": Not}, symbols)
    simplified = simplify_logic(expr, form="dnf")  # dnf = sum of products
    terms = sympy_to_terms(simplified)
    print("\nOriginal  : F = " + expression)
    print("Simplified: F = " + terms_to_text(terms))


# ======================================================
# Part 8: menu option 3 - draw the logic circuit
# ======================================================
def draw_gate(inputs, gate_name, output_name):
    # what it does: draws one gate with text
    # it takes: inputs (list of names), gate_name ("AND" or "OR"), output_name
    if len(inputs) == 1:
        # one input only: no gate needed, just a wire
        print("  " + inputs[0].ljust(3) + " ---------- " + output_name)
        return

    label = gate_name.center(5)
    print(" " * 9 + "+-----+")
    for j in range(len(inputs)):
        line = "  " + inputs[j].ljust(3) + " ---|"
        if j == len(inputs) // 2:
            line += label + "|--- " + output_name
        else:
            line += "     |"
        print(line)
    print(" " * 9 + "+-----+")


def draw_circuit(names, outputs):
    # what it does: draws the simplified circuit (NOT gates -> AND gates -> OR gate)
    terms = get_simplified_terms(names, outputs)

    if terms == []:
        print("\nF = 0 (the output is always 0, no gates needed).")
        return
    if terms == [[]]:
        print("\nF = 1 (the output is always 1, no gates needed).")
        return

    print("\nF = " + terms_to_text(terms))

    # which variables need a NOT gate
    not_list = sorted({n for term in terms for n, neg in term if neg})
    if not_list:
        print(
            "NOT gates needed for: "
            + ", ".join(not_list)
            + "  (A' means A after a NOT gate)"
        )

    print("\nAND gates:")
    gate_outputs = []
    for i in range(len(terms)):
        gate_name = "G" + str(i + 1)
        lits = [literal_text(n, neg) for n, neg in terms[i]]
        draw_gate(lits, "AND", gate_name)
        gate_outputs.append(gate_name)
        print()

    print("OR gate:")
    draw_gate(gate_outputs, "OR", "F")


# ======================================================
# Part 9: menu option 4 - implement using a decoder
# ======================================================
def implement_decoder(names, outputs):
    # what it does: shows how to build F using a decoder and an OR gate
    n = len(names)
    minterms = [i for i in range(len(outputs)) if outputs[i] == 1]

    print("\nWe need one " + str(n) + "x" + str(2**n) + " decoder.")
    print("Decoder inputs: " + ", ".join(names) + "  (" + names[0] + " is the MSB)")
    print("Each decoder output Di is 1 only for input combination number i:")
    for i in range(2**n):
        bits = format(i, "0" + str(n) + "b")
        text = "".join(literal_text(names[j], bits[j] == "0") for j in range(n))
        print("  D" + str(i) + " = " + text)

    if minterms == []:
        print("\nF = 0, no decoder outputs are connected.")
    elif len(minterms) == 2**n:
        print("\nF = 1, the output is always 1.")
    else:
        print("\nF = sum of minterms m(" + ", ".join(str(m) for m in minterms) + ")")
        print("Connect these decoder outputs to one OR gate:\n")
        draw_gate(["D" + str(m) for m in minterms], "OR", "F")


# ======================================================
# Part 10: the menu and the main program
# ======================================================
def show_menu():
    print("\n========== MENU ==========")
    print("1. Simplify using K-Map")
    print("2. Simplify using Boolean Algebra")
    print("3. Draw the logic circuit")
    print("4. Implement using a Decoder")
    print("5. Exit")


def main():
    n = get_number_of_inputs()
    names = get_variable_names(n)
    rows = generate_combinations(n)
    expression = read_expression(names)
    outputs = calculate_outputs(names, rows, expression)

    print("\nThe expression is: F = " + expression)
    print("\nTruth table:")
    print_truth_table(names, rows, outputs)

    # the menu keeps coming back until the user chooses Exit
    while True:
        show_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            simplify_kmap(names, outputs)
        elif choice == "2":
            simplify_algebra(names, expression)
        elif choice == "3":
            draw_circuit(names, outputs)
        elif choice == "4":
            implement_decoder(names, outputs)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Error: please choose a number from 1 to 5.")


main()
