# Digital Logic Design Project
import itertools  # we need this to make all the input combinations

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
    #               and checks that it is a correct expression
    #               (allowed characters, balanced brackets, correct syntax)
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

        # check every character alone
        for ch in text:
            # the character must be a variable name or an allowed symbol
            if ch not in names and ch not in ALLOWED_SYMBOLS:
                print("Error: the character '" + ch + "' is not allowed.")
                is_valid = False
                break

        # check that the number of "(" is equal to the number of ")"
        # we use a counter that goes up with "(" and goes down with ")"
        if is_valid:
            counter = 0
            for ch in text:
                if ch == "(":
                    counter += 1
                elif ch == ")":
                    counter -= 1
                # if the counter goes below 0 then we closed a bracket that was never opened
                if counter < 0:
                    break
            # at the end the counter must be exactly 0
            if counter != 0:
                print("Error: the brackets are not balanced.")
                is_valid = False

        # check that the expression has a correct form (for example "A+" or "+B" is wrong)
        # we do this by trying to parse it, if the parser fails the expression is wrong
        if is_valid:
            try:
                parse_expression(text, names)
            except ValueError as error:
                print("Error: invalid expression (" + str(error) + ").")
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
# Part 4: understanding the expression (parser)
# ======================================================
# The computer cannot calculate the text "A'B + AC" directly.
# So we change the text to a "tree" that shows the order of the operations.
# Example: A'B + AC becomes
#   ("OR", ("AND", ("NOT", ("VAR", "A")), ("VAR", "B")),
#          ("AND", ("VAR", "A"), ("VAR", "C")))
# The rules (from the weakest operator to the strongest):
#   expression = term + term + ...        (OR is the weakest)
#   term       = factor . factor ...      (AND, and "AB" with nothing between means AND too)
#   factor     = primary followed by ' ... (NOT)
#   primary    = a variable, or (expression)


class Parser:
    # what it does: reads the expression text and builds the tree
    # it takes: tokens (list of characters without spaces) and names (variable names)

    def __init__(self, tokens, names):
        self.tokens = tokens
        self.names = names
        self.pos = 0  # the position of the character we are reading now

    def peek(self):
        # what it does: looks at the current character without moving
        # it returns: the character, or None if we reached the end
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def parse(self):
        # what it does: builds the full tree and checks nothing is left after it
        # it returns: the tree
        tree = self.parse_or()
        if self.pos != len(self.tokens):
            raise ValueError("unexpected '" + self.tokens[self.pos] + "'")
        return tree

    def parse_or(self):
        # handles: term + term + term ...
        left = self.parse_and()
        while self.peek() == "+":
            self.pos += 1  # skip the +
            right = self.parse_and()
            left = ("OR", left, right)
        return left

    def parse_and(self):
        # handles: factor . factor, factor * factor, and factor factor (like AB)
        left = self.parse_not()
        while True:
            t = self.peek()
            if t == "." or t == "*":
                self.pos += 1  # skip the . or *
                right = self.parse_not()
                left = ("AND", left, right)
            elif t is not None and (t in self.names or t == "("):
                # a variable or a bracket directly after a factor means AND (like A'B or A(B+C))
                right = self.parse_not()
                left = ("AND", left, right)
            else:
                break
        return left

    def parse_not(self):
        # handles: primary followed by one or more '
        node = self.parse_primary()
        while self.peek() == "'":
            self.pos += 1  # skip the '
            node = ("NOT", node)
        return node

    def parse_primary(self):
        # handles: a variable, or an expression inside brackets
        t = self.peek()
        if t is None:
            raise ValueError("the expression ended too early")
        if t in self.names:
            self.pos += 1
            return ("VAR", t)
        if t == "(":
            self.pos += 1  # skip the (
            node = self.parse_or()
            if self.peek() != ")":
                raise ValueError("missing ')'")
            self.pos += 1  # skip the )
            return node
        raise ValueError("unexpected '" + t + "'")


def parse_expression(text, names):
    # what it does: changes the expression text to a tree
    # it takes: text (the expression) and names (the variable names)
    # it returns: the tree (it raises ValueError if the expression is wrong)

    # remove the spaces, then give the characters to the parser
    tokens = [ch for ch in text if ch != " "]
    return Parser(tokens, names).parse()


def evaluate_tree(tree, values):
    # what it does: calculates the value (0 or 1) of the tree for one input row
    # it takes: tree (from parse_expression) and values (a dictionary like {"A": 1, "B": 0})
    # it returns: 0 or 1

    kind = tree[0]
    if kind == "VAR":
        return values[tree[1]]
    if kind == "NOT":
        return 1 - evaluate_tree(tree[1], values)
    if kind == "AND":
        return evaluate_tree(tree[1], values) & evaluate_tree(tree[2], values)
    # the only kind left is OR
    return evaluate_tree(tree[1], values) | evaluate_tree(tree[2], values)


# ======================================================
# Part 5: calculating the output column
# ======================================================
def compute_outputs(tree, names, rows):
    # what it does: calculates F for every row of the truth table
    # it takes: tree (the expression tree), names (variable names), rows (input combinations)
    # it returns: a list of 0 and 1 (the output column), one value for every row

    outputs = []
    for row in rows:
        # connect every name with its bit, for example {"A": 0, "B": 1, "C": 1}
        values = dict(zip(names, row))
        outputs.append(evaluate_tree(tree, values))
    return outputs


def get_minterms(outputs):
    # what it does: finds the rows where F = 1
    # it takes: outputs (the output column)
    # it returns: a list of row numbers, for example [1, 3, 7]
    #             (row number = the binary value of the inputs, A is the left bit)

    return [i for i in range(len(outputs)) if outputs[i] == 1]


# ======================================================
# Part 6: finding the simplest form (Quine-McCluskey)
# ======================================================
# This is the math way to do exactly what we do in the K-map:
# join terms that are different in only one variable (like ABC + ABC' = AB).
# A term is written as a text of 0, 1 and -
#   1 = the variable is normal, 0 = the variable is complemented, - = the variable is removed
#   example for 3 variables: "01-" means A'B


def minterm_text(term, names):
    # what it does: changes a term like "01-" to a readable text like "A'B"
    # it takes: term (text of 0/1/-) and names (variable names)
    # it returns: the text of the product term ("1" if all variables were removed)

    text = ""
    for i in range(len(term)):
        if term[i] == "1":
            text += names[i]
        elif term[i] == "0":
            text += names[i] + "'"
    if text == "":
        text = "1"
    return text


def find_prime_implicants(minterms, n):
    # what it does: joins the terms again and again until no more joining is possible.
    #               the terms that cannot be joined anymore are the "prime implicants"
    #               (they are the biggest groups of the K-map)
    # it takes: minterms (list of row numbers where F = 1) and n (number of inputs)
    # it returns: primes (a set of terms) and log (a list of every joining we did, we use it
    #             to show the Boolean algebra steps)

    # start with every minterm as a binary text, for example 5 with n = 3 becomes "101"
    current = set(format(m, "0" + str(n) + "b") for m in minterms)
    primes = set()
    log = []

    while len(current) > 0:
        used = set()  # terms that were joined in this round
        next_round = set()  # the new terms made in this round
        pass_log = []
        items = sorted(current)

        # try every two terms
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a = items[i]
                b = items[j]
                diff_pos = -1
                diff_count = 0
                ok = True
                for k in range(n):
                    if a[k] != b[k]:
                        # the "-" must be in the same place in both terms
                        if a[k] == "-" or b[k] == "-":
                            ok = False
                            break
                        diff_count += 1
                        diff_pos = k
                # we can join them only if they differ in exactly one variable
                if ok and diff_count == 1:
                    merged = a[:diff_pos] + "-" + a[diff_pos + 1 :]
                    next_round.add(merged)
                    used.add(a)
                    used.add(b)
                    pass_log.append((a, b, merged))

        # the terms that were not joined with anyone are prime implicants
        primes = primes | (current - used)
        if len(pass_log) > 0:
            log.append(pass_log)
        current = next_round

    return primes, log


def covers(term, minterm, n):
    # what it does: checks if a term covers (includes) a minterm
    # it takes: term (text of 0/1/-), minterm (row number), n (number of inputs)
    # it returns: True or False

    bits = format(minterm, "0" + str(n) + "b")
    for i in range(n):
        if term[i] != "-" and term[i] != bits[i]:
            return False
    return True


def select_cover(primes, minterms, n):
    # what it does: chooses the smallest set of prime implicants that covers all the minterms
    #               step 1: take the essential ones (the only ones that cover some minterm)
    #               step 2: for what is left, keep taking the one that covers the most
    # it takes: primes, minterms, n
    # it returns: a sorted list of the chosen terms

    chosen = []
    ordered = sorted(primes)

    # step 1: essential prime implicants
    for m in minterms:
        candidates = [p for p in ordered if covers(p, m, n)]
        if len(candidates) == 1 and candidates[0] not in chosen:
            chosen.append(candidates[0])

    # remove the minterms that are already covered
    uncovered = set(minterms)
    for p in chosen:
        for m in minterms:
            if covers(p, m, n):
                uncovered.discard(m)

    # step 2: cover the rest
    while len(uncovered) > 0:
        best = max(
            ordered, key=lambda p: len([m for m in uncovered if covers(p, m, n)])
        )
        chosen.append(best)
        for m in minterms:
            if covers(best, m, n):
                uncovered.discard(m)

    return sorted(chosen)


def handle_constant(minterms, n):
    # what it does: checks if F is always 0 or always 1 (then there is nothing to simplify)
    # it takes: minterms and n
    # it returns: True if F is a constant (and prints the answer), otherwise False

    if len(minterms) == 0:
        print("F is always 0, so F = 0 (no gates are needed).")
        return True
    if len(minterms) == 2**n:
        print("F is always 1, so F = 1 (no gates are needed).")
        return True
    return False


def get_simplified_terms(minterms, n):
    # what it does: runs the whole simplification and gives the final terms
    # it takes: minterms and n
    # it returns: the list of chosen terms (text of 0/1/-)

    primes, log = find_prime_implicants(minterms, n)
    return select_cover(primes, minterms, n)


def terms_to_expression(terms, names):
    # what it does: changes a list of terms to a full expression like "A'B + C"
    # it takes: terms (list of 0/1/- texts) and names
    # it returns: the expression as text

    return " + ".join(minterm_text(t, names) for t in terms)


# ======================================================
# Part 7: option 1 - simplify using K-Map
# ======================================================
def gray_code(k):
    # what it does: makes the Gray code order for k bits (only one bit changes between neighbors)
    #               this is the order of the rows and columns of the K-map
    # it takes: k (number of bits)
    # it returns: a list of texts, for example k = 2 gives ["00", "01", "11", "10"]

    if k == 0:
        return [""]
    return [format(i ^ (i >> 1), "0" + str(k) + "b") for i in range(2**k)]


def print_single_kmap(var_names, outputs, offset):
    # what it does: prints one K-map table
    # it takes: var_names (the variables of this map), outputs (the output column)
    #           and offset (the start position in the outputs, used for the 5-variable case)
    # it returns: nothing, it only prints

    # half of the variables go to the rows and the rest go to the columns
    row_count = len(var_names) // 2
    col_count = len(var_names) - row_count
    row_codes = gray_code(row_count)
    col_codes = gray_code(col_count)

    label = "".join(var_names[:row_count]) + "\\" + "".join(var_names[row_count:])
    print(label.ljust(8) + "".join(c.center(5) for c in col_codes))
    for r in row_codes:
        line = r.ljust(8)
        for c in col_codes:
            # the number of the cell is the binary value of (row bits + column bits)
            index = offset + int(r + c, 2)
            line += str(outputs[index]).center(5)
        print(line)


def print_kmap(names, outputs, n):
    # what it does: prints the K-map (for 5 variables it prints two maps: A = 0 and A = 1)
    # it takes: names, outputs, n
    # it returns: nothing, it only prints

    if n == 5:
        for a in (0, 1):
            print("\nWhen A = " + str(a) + ":")
            print_single_kmap(names[1:], outputs, a * 16)
    else:
        print()
        print_single_kmap(names, outputs, 0)


def simplify_kmap(names, outputs, n):
    # what it does: shows the K-map, the groups, and the simplified expression
    # it takes: names, outputs, n
    # it returns: nothing, it only prints

    print("\n--- K-Map ---")
    print_kmap(names, outputs, n)

    minterms = get_minterms(outputs)
    print()
    if handle_constant(minterms, n):
        return

    chosen = get_simplified_terms(minterms, n)

    # every chosen term is one group in the K-map
    print("Groups (every group is a block of 1s in the K-map):")
    for i in range(len(chosen)):
        covered = [str(m) for m in minterms if covers(chosen[i], m, n)]
        print(
            "  Group "
            + str(i + 1)
            + ": cells (m"
            + ", m".join(covered)
            + ")  ->  "
            + minterm_text(chosen[i], names)
        )

    print("\nSimplified expression:")
    print("F = " + terms_to_expression(chosen, names))


# ======================================================
# Part 8: option 2 - simplify using Boolean Algebra
# ======================================================
MAX_STEPS_SHOWN = 10  # we show only this number of joinings in each round so the screen is not too long


def simplify_boolean_algebra(names, outputs, n):
    # what it does: shows the simplification steps using Boolean algebra laws
    # it takes: names, outputs, n
    # it returns: nothing, it only prints

    print("\n--- Simplify using Boolean Algebra ---")
    minterms = get_minterms(outputs)
    if handle_constant(minterms, n):
        return

    # step 1: write F as a sum of minterms (every row with F = 1)
    print("\nStep 1: write F as a sum of minterms (rows where F = 1):")
    canonical = [format(m, "0" + str(n) + "b") for m in minterms]
    print("F = " + terms_to_expression(canonical, names))

    primes, log = find_prime_implicants(minterms, n)

    # step 2: join the terms that differ in only one variable
    print("\nStep 2: join the terms using the law  X.Y + X.Y' = X")
    for r in range(len(log)):
        print(" Round " + str(r + 1) + ":")
        shown = 0
        for a, b, merged in log[r]:
            if shown >= MAX_STEPS_SHOWN:
                print(
                    "   ... and "
                    + str(len(log[r]) - MAX_STEPS_SHOWN)
                    + " more joinings"
                )
                break
            print(
                "   "
                + minterm_text(a, names)
                + " + "
                + minterm_text(b, names)
                + " = "
                + minterm_text(merged, names)
            )
            shown += 1
    print(" (If the same term appears twice we keep one only, using X + X = X)")

    # step 3: the terms that cannot be joined anymore
    print("\nStep 3: the terms that cannot be simplified more:")
    print("  " + terms_to_expression(sorted(primes), names))

    # step 4: remove the terms that are not needed
    chosen = select_cover(primes, minterms, n)
    removed = [p for p in sorted(primes) if p not in chosen]
    print(
        "\nStep 4: remove the terms that are not needed (absorption / redundant terms):"
    )
    if len(removed) == 0:
        print("  No term can be removed.")
    else:
        print("  Removed: " + terms_to_expression(removed, names))

    print("\nFinal simplified expression:")
    print("F = " + terms_to_expression(chosen, names))


# ======================================================
# Part 9: option 3 - draw the logic circuit
# ======================================================
def draw_gate(inputs, gate_name, output_name):
    # what it does: makes a small text drawing of one gate
    # it takes: inputs (list of input names), gate_name ("AND" or "OR") and output_name
    # it returns: a list of text lines (the drawing)

    width = max(len(s) for s in inputs)
    middle = len(inputs) // 2  # the line where we write the gate name and the output
    lines = []
    lines.append(" " * (width + 5) + "+-------+")
    for i in range(len(inputs)):
        left = inputs[i].ljust(width) + " ----"
        if i == middle:
            lines.append(left + "| " + gate_name.center(5) + " |---- " + output_name)
        else:
            lines.append(left + "|       |")
    lines.append(" " * (width + 5) + "+-------+")
    return lines


def draw_circuit(names, outputs, n):
    # what it does: draws the logic circuit of the simplified expression (AND gates then one OR gate)
    # it takes: names, outputs, n
    # it returns: nothing, it only prints

    print("\n--- Logic Circuit ---")
    minterms = get_minterms(outputs)
    if handle_constant(minterms, n):
        return

    chosen = get_simplified_terms(minterms, n)
    print("Circuit of: F = " + terms_to_expression(chosen, names))

    # collect the inputs of every product term (like ["A'", "B"])
    term_literals = []
    for t in chosen:
        literals = []
        for i in range(n):
            if t[i] == "1":
                literals.append(names[i])
            elif t[i] == "0":
                literals.append(names[i] + "'")
        term_literals.append(literals)

    # find which variables need a NOT gate
    not_needed = sorted(
        set(lit[:-1] for lits in term_literals for lit in lits if lit.endswith("'"))
    )
    print("\nInputs: " + ", ".join(names))
    if len(not_needed) > 0:
        print(
            "NOT gates needed: " + ", ".join(v + " -> " + v + "'" for v in not_needed)
        )
    else:
        print("NOT gates needed: none")

    # draw the AND gates (a term with one literal is only a wire, it needs no gate)
    or_inputs = []
    gate_number = 1
    for literals in term_literals:
        if len(literals) == 1:
            or_inputs.append(literals[0])
        else:
            gate_name = "G" + str(gate_number)
            gate_number += 1
            print("\nAND gate " + gate_name + ":")
            for line in draw_gate(literals, "AND", gate_name):
                print(line)
            or_inputs.append(gate_name)

    # draw the final OR gate (if we have only one term then no OR gate is needed)
    if len(or_inputs) == 1:
        print("\nOutput: F = " + or_inputs[0] + "  (no OR gate is needed)")
    else:
        print("\nOR gate (the final output):")
        for line in draw_gate(or_inputs, "OR", "F"):
            print(line)


# ======================================================
# Part 10: option 4 - implement using a Decoder
# ======================================================
def implement_with_decoder(names, outputs, n):
    # what it does: shows how to build F using an n-to-2^n decoder and one OR gate
    #               (the decoder gives one output line for every minterm, we OR the lines where F = 1)
    # it takes: names, outputs, n
    # it returns: nothing, it only prints

    print("\n--- Implementation using a Decoder ---")
    size = 2**n
    minterms = get_minterms(outputs)

    print(
        "Use a "
        + str(n)
        + "-to-"
        + str(size)
        + " decoder, its inputs are: "
        + ", ".join(names)
        + " ("
        + names[0]
        + " is the most significant bit)"
    )
    print("\nDecoder outputs:")
    for i in range(size):
        bits = format(i, "0" + str(n) + "b")
        if i in minterms:
            note = "-> connect to the OR gate"
        else:
            note = "-> not used"
        print("  D" + str(i) + "  (" + "".join(names) + " = " + bits + ")  " + note)

    print()
    if len(minterms) == 0:
        print("F = 0 (no decoder output is used, F is connected to ground).")
    elif len(minterms) == 1:
        print("F = D" + str(minterms[0]) + "  (no OR gate is needed)")
    else:
        print(
            "F = "
            + " + ".join("D" + str(m) for m in minterms)
            + "   (one OR gate with "
            + str(len(minterms))
            + " inputs)"
        )

    # a small hint: if F has more 1s than 0s it is cheaper to OR the unused lines and use NOR
    if len(minterms) > size // 2 and len(minterms) < size:
        zeros = [i for i in range(size) if i not in minterms]
        print(
            "Note: F has more 1s than 0s, so you can also use a NOR gate on "
            + ", ".join("D" + str(z) for z in zeros)
            + " (this gives F)."
        )


# ======================================================
# Part 11: the menu and the main program
# ======================================================
def show_menu():
    # what it does: prints the menu options
    # it takes: nothing
    # it returns: nothing, it only prints

    print("\n========== MENU ==========")
    print("1. Simplify using K-Map")
    print("2. Simplify using Boolean Algebra")
    print("3. Draw the logic circuit")
    print("4. Implement using a Decoder")
    print("5. Exit")


def get_menu_choice():
    # what it does: asks the user for a menu option and keeps asking until it is valid
    # it takes: nothing
    # it returns: the choice as a text ("1" to "5")

    while True:
        choice = input("Choose an option (1-5): ").strip()
        if choice in ["1", "2", "3", "4", "5"]:
            return choice
        # an invalid choice does not stop the program, we only show the error and ask again
        print("Error: invalid choice, please enter a number from 1 to 5.")


def main():
    # what it does: runs the whole program
    #               1) reads n and the expression, 2) prints the truth table,
    #               3) shows the menu again and again until the user chooses Exit
    # it takes: nothing
    # it returns: nothing

    n = get_number_of_inputs()
    names = get_variable_names(n)
    rows = generate_combinations(n)
    expression = read_expression(names)
    print("The expression is: F = " + expression)

    # calculate and print the truth table
    tree = parse_expression(expression, names)
    outputs = compute_outputs(tree, names, rows)
    print("\n--- Truth Table ---")
    print_truth_table(names, rows, outputs)

    # the menu loop: it stops only when the user chooses Exit
    while True:
        show_menu()
        choice = get_menu_choice()
        if choice == "1":
            simplify_kmap(names, outputs, n)
        elif choice == "2":
            simplify_boolean_algebra(names, outputs, n)
        elif choice == "3":
            draw_circuit(names, outputs, n)
        elif choice == "4":
            implement_with_decoder(names, outputs, n)
        else:
            print("Goodbye!")
            break


# start the program
main()
