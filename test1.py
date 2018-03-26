from pygments.lexers import Python3Lexer
import pygments

pylex = Python3Lexer()
for i in pylex.get_tokens("""
        from subprocess import PIPE

        ' this is a string literal '
        for i in range(10):
            print(i)

        def sum(a,b):
            return a+b

        print(sum(1,2))

        0.1213

        """):
    print(i)
