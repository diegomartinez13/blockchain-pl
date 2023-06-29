"""
Assignment #4: Lexical Analyzer + Syntax Analyzer + Semantic Analyzer + Web App
Author: Diego Martinez Garcia

Summary: The following program is a web application that allows the user to create a blockchain, add new data to it, print it, view it, and simulates running it, mining it and exporting it. The analyzer part of he program flashes information on the Front End of the web app, and the user can see the results of the commands on the web app.
"""
from ply import lex
import ply.yacc as yacc
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Lexical analysis
# Token List
tokens = [
    "ID",
    "BLOCK",
    "VAR",
    "ADD",
    "PRINT",
    "VIEW",
    "RUN",
    "MINE",
    "EXPORT",
    "STR",
    "INT",
    "LONG",
    "FLOAT",
    "LIST",
    "TUPLE",
    "DICT",
    "NUM",
    "ASSIGN",
    "TYPEASSIGN",
    "SEPARATOR",
    "LPAREN",
    "RPAREN",
    "NE",
    "LT",
    "GT",
    "LE",
    "GE",
    "PLUS",
    "MINUS",
    "STAR",
    "SLASH",
    "COMMENT",
    "WHITESPACE",
    "PCT",
    "STRING",
]

# Reserved keywords dictionary
reserved = {
    "block": "BLOCK",
    "var": "VAR",
    "add": "ADD",
    "print": "PRINT",
    "view": "VIEW",
    "run": "RUN",
    "mine": "MINE",
    "export": "EXPORT",
    "str": "STR",
    "int": "INT",
    "long": "LONG",
    "float": "FLOAT",
    "List": "LIST",
    "Tuple": "TUPLE",
    "Dict": "DICT",
}

# regular expressions for tokens:
t_ASSIGN = r"\="
t_TYPEASSIGN = r"\:"
t_SEPARATOR = r"\,"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_NE = r"\!="
t_LT = r"\<"
t_GT = r"\>"
t_LE = r"\<="
t_GE = r"\>="
t_PLUS = r"\+"
t_MINUS = r"\-"
t_STAR = r"\*"
t_PCT = r"%"
t_SLASH = r"\/"
t_ignore_COMMENT = r"\/\/.*"
t_ignore_WHITESPACE = r"\t|\r|\n|\s"


# functions to define tokens based on regular expressions:
def t_ID(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    t.type = reserved.get(str(t.value), "ID")
    t.value = str(t.value)
    return t


def t_NUM(t):
    r"-?\d*(\d\.|\.\d)\d* | \d+"
    t.value = int(t.value)
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_STRING(t):
    r"\".*?\" "
    t.value = t.value[1:-1]
    return t


def t_error(t):
    print(f"---- ERROR ----> Invalid Token: {t.value[0]} at line {t.lexer.lineno}")
    t.lexer.skip(1)


# Initializing lexer:
lexer = lex.lex()


# Parsing rules + Semantic rules
# Precedence rules for the arithmetic operators
precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "STAR", "SLASH", "PCT"),
    ("nonassoc", "LT", "LE", "GE", "GT", "NE"),
)

# Dictionary that will store the blockchains
blockchains = {'DiegoMartinezGarcia': [['Author', 'str']]}


# BNF grammar:
def p_block(p):
    """
    block : BLOCK ID ASSIGN LPAREN attributes RPAREN
          | ADD ID ASSIGN LPAREN new_atts RPAREN
          | PRINT ID
          | RUN ID
          | MINE ID
          | EXPORT ID
          | VIEW ID
          | test
    """
    keyword = p[1]
    if keyword == "block":
        try:
            if validate(p[5]):
                if p[2] in blockchains:
                    flash(
                        category="error",
                        message="Error detected: Blockchain already exists.",
                    )
                else:
                    blockchains[p[2]] = p[5]
                    flash(
                        message="Blockchain created successfully!", category="success"
                    )
        except Exception as e:
            flash(
                category="error",
                message=f"Error detected during creation of blockchain: {e}",
            )
    elif keyword == "add":
        try:
            data = p[5]
            data_to_add = {"new_data": data}
            if p[2] in blockchains:
                flash(
                    category="error",
                    message="Error detected: Blockchain already exists.",
                )
            else:
                blockchains[p[2]] = data_to_add
                flash(
                    category="success",
                    message="New data added to blockchains successfully!",
                )
        except Exception as e:
            flash(
                category="error",
                message=f"Error detected during adding new attrs to blockchain: {e}",
            )
    elif keyword == "print" or keyword == "view":
        try:
            id = p[2]
            message = blockchains[id]
            flash(category="info", message={id: message})
        except Exception as e:
            flash(category="error", message=f"Error detected: Key '{e}' not found.")
    else:
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]
            time.sleep(2)
            flash(message=f"Command: '{p[1]} {p[2]}' completed", category="success")


def p_type(p):
    """
    type : STR
         | INT
         | LONG
         | FLOAT
         | LIST
         | TUPLE
         | DICT
    """
    p[0] = p[1]


def p_attribute(p):
    """
    attribute : ID TYPEASSIGN type
    """
    p[0] = [p[1], p[3]]


def p_attributes(p):
    """
    attributes : attribute
               | attributes SEPARATOR attribute
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]


def p_new_att(p):
    """
    new_att : ID TYPEASSIGN STRING
            | ID TYPEASSIGN NUM
    """
    p[0] = [p[1], p[3]]


def p_new_atts(p):
    """
    new_atts : new_att
             | new_atts SEPARATOR new_att
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[3])
        p[0] = p[1]


def p_expr_term(p):
    """
    expr : term
         | expr PLUS term
         | expr MINUS term
    """
    try:
        if len(p) == 2:
            p[0] = p[1]
        elif p[2] == "-":
            p[0] = p[1] - p[3]
        else:
            p[0] = p[1] + p[3]
    except Exception as e:
        flash(
            category="error", message=f"--> Error detected during arithmetic opt: {e}"
        )


def p_term_factor(p):
    """
    term : factor
         | term STAR factor
         | term SLASH factor
         | term PCT factor
    """
    try:
        if len(p) == 2:
            p[0] = p[1]
        elif p[2] == "/":
            p[0] = p[1] / p[3]
        elif p[2] == "%":
            p[0] = p[1] % p[3]
        else:
            p[0] = p[1] * p[3]
    except Exception as e:
        flash(category="error", message=f"Error detected during arithmetic opt: {e}")


def p_factor_ID(p):
    """
    factor : ID
    """
    try:
        p[0] = p[1]
    except KeyError as e:
        flash(category="error", message=f"Error detected:  {e}")


def p_factor_NUM(p):
    """
    factor : NUM
    """
    p[0] = p[1]


def p_factor_expr_argsopt(p):
    """
    factor : LPAREN expr RPAREN
            | factor LPAREN argsopt RPAREN
    """
    if p[1] == "(":
        p[0] = p[2]
    else:
        p[0] = [p[1], p[3]]


def p_test(p):
    """
    test : expr NE expr
            | expr LT expr
            | expr LE expr
            | expr GE expr
            | expr GT expr
    """
    try:
        if p[2] == "!=":
            p[0] = p[1] != p[3]
            flash(
                message=f"Test: {p[1]} != {p[3]} | Test result: {p[0]}", category="info"
            )
        elif p[2] == "<":
            p[0] = p[1] < p[3]
            flash(
                message=f"Test: {p[1]} < {p[3]} | Test result: {p[0]}", category="info"
            )
        elif p[2] == "<=":
            p[0] = p[1] <= p[3]
            flash(
                message=f"Test: {p[1]} <= {p[3]} | Test result: {p[0]}", category="info"
            )
        elif p[2] == ">=":
            p[0] = p[1] >= p[3]
            flash(
                message=f"Test: {p[1]} >= {p[3]} | Test result: {p[0]}", category="info"
            )
        else:
            p[0] = p[1] > p[3]
            flash(
                message=f"Test: {p[1]} > {p[3]} | Test result: {p[0]}", category="info"
            )
    except Exception as e:
        flash(category="error", message=f"Error detected:  {e}")


def p_argsopt(p):
    """
    argsopt : args
            |
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = []


def p_args(p):
    """
    args : expr
         | expr SEPARATOR args
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1].append(p[3])


def p_error(p):
    if p:
        flash(
            category="error",
            message=f"Syntax error detected at line {p.lineno}, col {p.lexpos} of testing file, unexpected token '{p.value}'.",
        )
    else:
        flash(
            category="error", message="Syntax error detected: Missing token or tokens"
        )


# END OF PARSING RULES


# Helper functions:
def validate(attributes):
    valid_Types = ["List", "Dict", "int", "float", "long", "str", "Tuple"]
    for attribute in attributes:
        id, type = attribute[0], attribute[1]
        if type not in valid_Types:
            return False
    return True


# Building parser:
parser = yacc.yacc()


# Code implemented to run the parser and:
def main(line):
    if line == "\n" or line == "" or line == " " or line.startswith("//"):
        flash(category="error", message="Error: Empty line")
    else:
        lexer.input(line)
        result = parser.parse(line)


# Web app using flask framework
app = Flask(__name__)
app.config["SECRET_KEY"] = "A0Zr98j/3yXR~XHH!jmN]LWX/,?RT"


@app.route("/", methods=["GET", "POST"])
def index():
    # Getting command from user
    if request.method == "POST":
        command = request.form.get("command")
        # Analyzing command
        main(command)
    # Sendig blockchains to index.html for rendering
    return render_template("index.html", blockchains=blockchains)


if __name__ == "__main__":
    # Running web app
    app.run(host="localhost", port=5000, debug=True)
