from openai import OpenAI

client = OpenAI(api_key="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")

chat_completion = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=[
        # Assistant message 1
        {
            "role": "assistant",
            "content": """
                    TextWindow.WriteLine("Hello World")
                    is tokenized into a stream,
                    ID . ID ( STR )

                    The term “TextWindow” is processed into an identifier represented by the terminal ID, while a text dot is interpreted as a terminal dot. 
                    Similarly, “WriteLine” is analyzed like TextWindow. Open and close parentheses undergo the same procedure as the dot, and the string 
                    literal "Hello World" is translated into the terminal STR. """
        },
        # Assistant message 2
        {
            "role": "assistant",""
            "content": """What are structural candidates ?
                          TextWindow.WriteLine("Hello World")
        ExprStatement ->  ID        . ID      ( Exprs )

                        For example, programmers have written “TextWindow.(dot)”. Currently cursor at this position after the dot. 
                        At this point, he /she wants the editor to complete the rest of the part of this line of code. 
                        Then our system looks for the appropriate production rule. Next, our system gets the rest of the symbols from 
                        that production rule. Our system considered this part as a structural candidate. We ask the ChatGPT to decorate 
                        the structural candidate by giving the prefix what the programmer writes before asking for code suggestions and 
                        the structural candidate."""
        },
        # Assistant message 3
        {
            "role": "assistant",""
            "content": """number = 100
                          While(number>1)
                          TextWindow.WriteLine(number)
                        Suggestions: 
                          ID = Expr

                        For instance, in the above example, the suggestion at the cursor position is an assignment statement formatted as ID = Expr. 
                        Here, the terminal ID signifies an identifier, the terminal = represents an assignment symbol, and the non-terminal “Expr” indicates 
                        an expression. Further, the third example in Figure 1 delves deeper into the syntax structures of “Expr”  after users input an identifier, 
                        number, followed by an assignment symbol. In contrast, Microsoft SmallBasic does not provide any suggestions at the same cursor position 
                        until the user starts typing the initial character n. Only then do suggestions appear, revealing one variable name, number, and one class 
                        name, Network, both beginning with that character."""
        },
        # Assistant message 4
        {
            "role": "assistant",""
            "content": """Terminal: A terminal symbol, also known as a terminal or token, is a basic unit of syntax in a programming language. Terminals are the smallest units that cannot be broken down further within the language's syntax rules.

            Identifier: An identifier is a name given to various programming language entities, such as variables, functions, classes, and labels. Identifiers serve as unique labels to refer to these entities within a program.

            Non-terminal: A non-terminal symbol represents a syntactic category that can be decomposed into other symbols according to the rules of the language's grammar.

            Expression: In programming languages, an expression is a combination of one or more operands (variables, constants, literals, function calls) and operators that can be evaluated to produce a value."""
        },
         # Assistant message 5
        {
            "role": "assistant",""
            "content": """ Problem statement: This is the incomplete SmallBasic programming language code:
               number = 100
               While(number>1)
               TextWindow
               'ID (Expr)'
               Complete the 'ID (Expr)' part of the code in the SmallBasic programming language.                    
               Just show your answer in place of 'ID (Expr)'. 
               
               Your solution: .WriteLine(number)

               Expected solution: .WriteLine(number) """
        },
          # Assistant message 6
        {
            "role": "assistant",""
            "content": """  Rule 0: Prog' -> Prog
                            This indicates that the program (Prog') consists of one or more statements defined by Prog. The prime (') usually denotes the start symbol in the grammar.
                            Rule 1: Prog -> MoreThanOneStmt
                            A program consists of one or more statements (MoreThanOneStmt).
                            Statement-Level (Control Flow and Expressions)
                            Rule 2: Stmt -> ExprStatement
                            A statement (Stmt) can be an expression statement (ExprStatement).
                            Rule 3: Stmt -> While Expr CRStmtCRs EndWhile
                            A while loop statement. It consists of the keyword While, followed by an expression (Expr), then a series of statements (CRStmtCRs), and finally EndWhile.
                            Rule 4: Stmt -> ID :
                            A statement could be an identifier followed by a colon, which could indicate a label for Goto.
                            Rule 5: Stmt -> Goto ID
                            A Goto statement that refers to an identifier (label) in the program.
                            Rule 6: Stmt -> For ID = Expr To Expr OptStep CRStmtCRs EndFor
                            A for loop statement. It starts with For, followed by an identifier, an expression for the initial value, another expression for the end value, and an optional step (OptStep). Inside the loop are statements (CRStmtCRs), and the loop ends with EndFor.
                            Rule 7: Stmt -> Sub ID CRStmtCRs EndSub
                            A subroutine definition. It starts with Sub, followed by an identifier (ID) and then a series of statements (CRStmtCRs), and ends with EndSub.
                            Rule 8: Stmt -> If Expr Then CRStmtCRs MoreThanZeroElseIf
                            An if statement. It begins with If and an expression (Expr), followed by Then, then some statements (CRStmtCRs), and may have one or more ElseIf blocks (MoreThanZeroElseIf).
                            Rule 9: Stmt ->
                            This is an empty statement (no operation). """

        },
        # Assistant message 7
        {
            "role": "assistant",""
            "content": """  Rule 10: MoreThanZeroElseIf -> OptionalElse
                            Indicates that there may be no ElseIf blocks, just an OptionalElse (either an Else block or an EndIf).
                            Rule 11: MoreThanZeroElseIf -> ElseIf Expr Then CRStmtCRs MoreThanZeroElseIf
                            Defines one or more ElseIf blocks, each with an expression and statements.
                            Rule 12: OptionalElse -> EndIf
                            No Else block; the If statement ends with EndIf.
                            Rule 13: OptionalElse -> Else CRStmtCRs EndIf
                            Defines an Else block with its own statements, followed by EndIf.
                            Expression Statements
                            Rule 14: ExprStatement -> ID = Expr
                            An assignment statement where an identifier (ID) is assigned the value of an expression (Expr).
                            Rule 15: ExprStatement -> ID . ID = Expr
                            A member assignment statement where a member of an object or class (ID . ID) is assigned the value of an expression.
                            Rule 16: ExprStatement -> ID . ID ( Exprs )
                            A method call where an object or class member (ID . ID) is invoked with arguments (Exprs).
                            Rule 17: ExprStatement -> ID ( )
                            A function or method call without any arguments.
                            Rule 18: ExprStatement -> ID Idxs = Expr
                            An array assignment where an array element (ID Idxs) is assigned the value of an expression.
                            8. Carriage Return and Statements
                            Rule 19: CRStmtCRs -> CR TheRest
                            A series of statements separated by carriage returns (CR), followed by the rest of the statements (TheRest).
                            Rule 20: TheRest ->
                            Defines an empty set of remaining statements (end of statement sequence).
                            Rule 21: TheRest -> Stmt CR TheRest
                            Defines one or more statements, each followed by a carriage return.
                            9. Handling Multiple Statements
                            Rule 22: MoreThanOneStmt -> Stmt
                            A block of one statement.
                            Rule 23: MoreThanOneStmt -> Stmt CR MoreThanOneStmt
                            A block of multiple statements, each followed by a carriage return.
                            Optional Step in For Loops
                            Rule 24: OptStep ->
                            Defines an empty step (i.e., no Step keyword is used, so the loop increments by 1 by default).
                            Rule 25: OptStep -> Step Expr
                            Defines an optional Step clause in a For loop, with an expression for the step value."""
 
        },
        # Assistant message 8
        {
            "role": "assistant",""
            "content": """  Rule 26: Expr -> CondExpr
                            An expression (Expr) can be a conditional expression (CondExpr).
                            Rules 27-30: Exprs, MoreThanOneExpr
                            Exprs can be empty (no arguments) or consist of one or more expressions, possibly separated by commas.
                            10. Logical and Comparison Operators
                            Rule 31: CondExpr -> OrExpr
                            A conditional expression is composed of Or expressions.
                            Rules 32-33: OrExpr -> OrExpr Or AndExpr | AndExpr
                            An OrExpr is a logical OR of two expressions, or simply an AndExpr.
                            Rules 34-35: AndExpr -> AndExpr And EqNeqExpr | EqNeqExpr
                            An AndExpr is a logical AND of two expressions, or an equality/inequality expression.
                            Rules 36-38: EqNeqExpr -> = | <> | CompExpr
                            An equality (=) or inequality (<>) expression compares two values. Alternatively, it can be a comparison expression (CompExpr).
                            11. Comparison Expressions
                            Rules 39-43: CompExpr -> < | <= | > | >= | AdditiveExpr
                            A comparison expression evaluates less than (<), less than or equal to (<=), greater than (>), or greater than or equal to (>=), or can be an additive expression.
                            Arithmetic Operations
                            Rules 44-46: AdditiveExpr -> + | - | MultiplicativeExpr
                            An additive expression uses + or - operators, or can be a multiplicative expression.
                            Rules 47-49: MultiplicativeExpr -> * | / | UnaryExpr
                            A multiplicative expression uses * or / operators, or can be a unary expression.
                            Unary Expressions and Primary Expressions
                            Rules 50-51: UnaryExpr -> - | Primary
                            A unary expression may negate a value or can be a primary expression.
                            Rules 52-58: Primary -> NUM | STR | ( Expr ) | ID | ID . ID | ID . ID ( Exprs ) | ID Idxs
                            Primary expressions include numbers (NUM), strings (STR), parentheses-enclosed expressions, identifiers, member accesses, method calls, or array indexing.
                            Array Indexing
                            Rules 59-60: Idxs -> [ Expr ] | [ Expr ] Idxs
                            Defines array indexing where one or more indices are provided within brackets.
                            """
 
        },
        # Assistant message 9
        {
            "role": "system",
            "content": "You are a helpful assistant that provides programming code suggestions while typing code in an IDE (Integrated Development Environment). Just answer concisely and place your answer after the provided code."
        },
    ]
)
print(chat_completion.choices[0].message.content, "\n")
 

# Promt-1 : This is the incomplete small basic programming language code:
#             Code here {candidate_structure} 
#           Compelete the last line of code following the candidate_structure:  {. ID = Expr } in Small basic Programming Language. 
#           Please complete the last line only or just show your answer in place of candidate structure.
# Promt-2:  You will be given an incomplete Small Basic Programming Language code snapshot. You should complete the line of the code. Rememeber your output should be based on last line of code or cuurent line :
#             Code here {candidate_structure} 
#           When I ask for complte the code, you will reply with a code that follows the candidate_structure. Please mention what will you replace in place of {candidate_structure}.
# Promt-3:  You will be given a piece of small basic programming language code where there are two parts, one is the 'incomplete code' and a candidate structue.
#            Code here {candidate_structure} 
#           You will reply with code in place of the candidate stucture.
#           Do not produce random code. You should follow the structure of the candidate.
# Promt-4:  This is the incomplete small basic programming language code:
#             Code here {candidate_structure} 
#           Complete just the carly brace part of the above code using candidate_structure:  {. Terminal = Expression } rules.
#           For example, if the  incomplete code struture like 
#          'TextWindow{candidate_structure}'. Then if the candidate_structure:  { .Indentifier(Expression) }. Then, the output should be just '.WriteLine("Hello World!")'. That means you will reply for the  unspacified candidate strcututre.
# Promt-5:  Problem statement: """<insert problem statement>"""
#           Your solution: """<insert model generated solution>"""

#           Expected solution: """<insert student's solution>"""]
# """ The program title is "Variables.sb". This is the incomplete small basic programming language code:
#             TextWindow.Write("Enter your Name: ") 
#             {candidate_structure} 
           
#             Compelete the last line of code following the candidate_structure:  { Indentifier = Expression } in Small Basic Programming Language. 
#             Please complete the last line only or just show your answer in place of candidate structure.
#             Complete just the content of the carly brace (inside)part of the above code. Do not produce carle brace in the output."""

# Terminal: A terminal symbol, also known as a terminal or token, is a basic unit of syntax in a programming language.
# Terminals are the smallest units that cannot be broken down further within the language's syntax rules.
# --------------
#  Identifier: An identifier is a name given to various programming language entities, such as variables, functions, classes, and labels. 
# Identifiers serve as unique labels to refer to these entities within a program. 
# ----------------------------
# Non-terminal: A non-terminal symbol represents a syntactic category that can be decomposed into other symbols according to the rules of the language's grammar.
# -------------------------------------
# Expression: In programming languages, an expression is a combination of one or more operands (variables, constants, literals, function calls) 
# and operators that can be evaluated to produce a value. 