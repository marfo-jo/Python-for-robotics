// Beginner-friendly explanations for Python errors. Each rule matches the
// exception type (and optionally the message) and teaches what the error
// means, the usual cause, and how to find it. The goal is to teach reading
// tracebacks, not to hide them: the raw traceback is always shown too.

const RULES = [
  { type: "SyntaxError", re: /expected ':'/, title: "Missing colon",
    explain: "Lines that start a block (if, elif, else, for, while, def, class, with, try) must end with a colon.",
    tip: "Look at the line the caret ^ points to and add `:` at the end." },
  { type: "SyntaxError", re: /unterminated string|EOL while scanning/, title: "A string was never closed",
    explain: "A quote opened a string but no matching quote closed it on the same line.",
    tip: "Count the quotes on that line. Every opening ' or \" needs a partner." },
  { type: "SyntaxError", re: /was never closed|unexpected EOF/, title: "A bracket was never closed",
    explain: "An opening (, [ or { has no matching closing bracket. Python only notices at the end, so the real mistake is often on an EARLIER line.",
    tip: "Check the lines above the one reported. Count opening and closing brackets." },
  { type: "SyntaxError", re: /invalid syntax.*=|cannot assign|Maybe you meant '=='/, title: "= versus ==",
    explain: "`=` stores a value in a variable. `==` compares two values. Inside an if or while you almost always want `==`.",
    tip: "Inside conditions, compare with `==`." },
  { type: "SyntaxError", title: "Python could not read this line",
    explain: "A SyntaxError means the code isn't valid Python, so NOTHING ran, not even the lines above it.",
    tip: "Read the line shown and the line just above it. Look for missing colons, brackets, quotes, or a stray character." },
  { type: "IndentationError", title: "Indentation is part of Python's grammar",
    explain: "Python uses indentation (leading spaces) to know which lines belong to an if, for, def, etc. A block must be indented consistently, and a line ending in ':' must be followed by an indented line.",
    tip: "Use 4 spaces per level. Make every line in the same block start at the same column." },
  { type: "TabError", title: "Tabs and spaces mixed",
    explain: "This line mixes tab characters and spaces for indentation. They look the same but Python counts them differently.",
    tip: "Re-indent the block with spaces only (the editor's Tab key inserts 4 spaces)." },
  { type: "NameError", re: /name '(\w+)' is not defined/, title: "Python doesn't know that name",
    explain: (m) => `\`${m[1]}\` is used before it was ever assigned, or it's spelled differently than where you defined it. Python names are case-sensitive: \`Total\` and \`total\` are different variables.`,
    tip: "Check spelling and capitalization. Make sure the assignment runs before this line (for example, not only inside an if that was skipped)." },
  { type: "TypeError", re: /can only concatenate str \(not "(\w+)"\) to str/, title: "Adding text and a number",
    explain: (m) => `You used + between a string and a ${m[1]}. Python won't guess whether you meant math or text.`,
    tip: "Convert first: str(number) to join text, or int(text)/float(text) to do math. An f-string avoids the problem: f\"speed = {v}\"." },
  { type: "TypeError", re: /unsupported operand type\(s\) for ([^:]+): '(\w+)' and '(\w+)'/, title: "An operator got the wrong types",
    explain: (m) => `The operator ${m[1].trim()} can't combine a ${m[2]} and a ${m[3]}. A common cause is a value read from a file or a split() that is still a string.`,
    tip: "Print type(x) for each side to see what you really have, then convert with int() or float()." },
  { type: "TypeError", re: /'NoneType' object is not (subscriptable|iterable)/, title: "Using the result of a function that returned nothing",
    explain: "A value is None. Usually a function printed its answer instead of returning it, or a method like list.sort() (which returns None) was assigned.",
    tip: "Check that your function has a `return` statement on every path." },
  { type: "TypeError", re: /'(\w+)' object is not callable/, title: "Calling something that isn't a function",
    explain: (m) => `You put parentheses after a ${m[1]}, as if it were a function. Often a variable has the same name as a function (for example \`list = [1, 2]\` then \`list(...)\`).`,
    tip: "Rename the variable so it doesn't hide the function." },
  { type: "TypeError", re: /missing (\d+) required positional argument/, title: "A function call is missing an argument",
    explain: "The function definition asks for more arguments than this call provides.",
    tip: "Compare the def line with the call. Count the parameters." },
  { type: "TypeError", re: /takes (\d+) positional arguments? but (\d+) (was|were) given/, title: "Too many arguments",
    explain: "The call passes more arguments than the function accepts.",
    tip: "Compare the def line with the call." },
  { type: "TypeError", re: /indices must be integers|slice indices must be/, title: "Index must be an integer",
    explain: "List and string positions must be integers. A float (like 2.0 from `/`) or a string (like '2') can't be an index.",
    tip: "Use // for integer division, or wrap the index in int()." },
  { type: "TypeError", title: "Wrong type of value",
    explain: "An operation received a value of a type it can't work with.",
    tip: "Read the message carefully. It names the types. Print type(x) to check your assumptions." },
  { type: "IndexError", title: "Index out of range",
    explain: "You asked for a position that doesn't exist. A list of length n has valid indexes 0 to n-1, so index n is already one past the end (the classic off-by-one).",
    tip: "Print len(the_list) and the index just before the failing line. Check loop bounds: range(len(x)) already stops at len(x)-1." },
  { type: "KeyError", re: /^'?(.*?)'?$/, title: "That key isn't in the dictionary",
    explain: (m) => `The dict has no key ${m[1] ? "`" + m[1] + "`" : ""}. Keys must match exactly, including case and type ('5' is not 5).`,
    tip: "Print the dict's keys(). Use d.get(key, default) when a key might be missing." },
  { type: "ValueError", re: /invalid literal for int\(\) with base 10: '(.*)'/, title: "That text isn't a whole number",
    explain: (m) => `int() was given '${m[1]}', which isn't a valid integer. Empty strings, spaces, and decimals like '4.5' all fail.`,
    tip: "Strip whitespace first, use float() for decimals, and handle empty fields (common in NMEA sentences with no fix)." },
  { type: "ValueError", re: /could not convert string to float: '(.*)'/, title: "That text isn't a number",
    explain: (m) => `float() was given '${m[1]}'. Empty fields are the usual culprit when parsing sensor data.`,
    tip: "Check for an empty string before converting, or catch ValueError." },
  { type: "ValueError", re: /too many values to unpack|not enough values to unpack/, title: "Unpacking count mismatch",
    explain: "You wrote `a, b = something`, but `something` has a different number of items than the names on the left.",
    tip: "Print the value and its len() before unpacking." },
  { type: "ValueError", title: "Right type, wrong value",
    explain: "The value has the right type but an invalid content.",
    tip: "Print the value right before the failing line." },
  { type: "ZeroDivisionError", title: "Division by zero",
    explain: "You divided by zero. In robotics this is often dt == 0 on the first loop iteration, or a count of zero samples.",
    tip: "Guard the division: `if dt > 0:` or check the count before averaging." },
  { type: "AttributeError", re: /'(\w+)' object has no attribute '(\w+)'/, title: "That value doesn't have that attribute",
    explain: (m) => `A ${m[1]} has no \`.${m[2]}\`. Either the value isn't the type you expected, or the name is misspelled.`,
    tip: "Print type(x). If it's NoneType, a function probably returned nothing." },
  { type: "ImportError", title: "Import failed",
    explain: "Python couldn't import that name. In a challenge, the tests import YOUR function by name, so it must be defined with exactly the name in the instructions.",
    tip: "Check the def line spelling against the instructions." },
  { type: "ModuleNotFoundError", title: "Module not available",
    explain: "That module isn't installed here. Some libraries (pyserial, PyTorch, rclpy) can't run in the browser. Those lessons provide local exercises instead.",
    tip: "Check the lesson instructions for the local run command." },
  { type: "RecursionError", title: "A function called itself forever",
    explain: "A function kept calling itself (directly or indirectly) without stopping.",
    tip: "Make sure there's a base case that returns without another call." },
  { type: "TimeoutError", title: "Your code took too long (probably an infinite loop)",
    explain: "The code was stopped after the time limit. The usual cause is a while loop whose condition never becomes False, because the variable it checks never changes inside the loop.",
    tip: "Find the while loop and check that something inside it moves the condition toward False. Add a print inside the loop to watch it." },
  { type: "RuntimeError", re: /input\(\)/, title: "input() isn't available",
    explain: "The browser editor can't pause for keyboard input.",
    tip: "Put test values in variables at the top of your code instead." },
];

const READING_GUIDE = [
  "Read the LAST line first: it names the error type and gives a message.",
  "Then find the last \"File \"solution.py\", line N\" entry: that's the line that was running when it failed.",
  "The lines above it show how the program got there (which function called which).",
  "The real mistake is often a little before the reported line, for example where a variable got a wrong value.",
];

export function explainError(error) {
  if (!error) return null;
  for (const rule of RULES) {
    if (rule.type !== error.type) continue;
    const match = rule.re ? rule.re.exec(error.message || "") : [];
    if (rule.re && !match) continue;
    const explain = typeof rule.explain === "function" ? rule.explain(match) : rule.explain;
    return { title: rule.title, explain, tip: rule.tip, guide: READING_GUIDE, lineno: error.lineno };
  }
  return {
    title: error.type,
    explain: "This error type isn't in the explainer yet. Read the message: it usually says exactly what went wrong.",
    tip: "Find the line number in the traceback and print the values used on that line.",
    guide: READING_GUIDE,
    lineno: error.lineno,
  };
}

export const RULE_COUNT = RULES.length;
