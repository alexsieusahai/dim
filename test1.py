from pygments.lexers import PythonLexer

pylex = PythonLexer()
for i in pylex.get_tokens("""
        from subprocess import PIPE

        for i in range(10):
            print(i)

        """):
    print(i)
