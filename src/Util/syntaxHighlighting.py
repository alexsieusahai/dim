import pygments
from pygments.lexers import Python3Lexer
from constants import SyntaxColors, Colors

def setColors(editorObj, colorMap):
    """
    Sets the colors of the editorObj for every line
    in editorObj.lineLinkedList.

    Assumes every file is a python file, need to use
    different lexers later (possibly check with something
    else then pass it in as an argument).

    colorMap is a dictionary which maps the kind of syntax
    to a certain color.
    """
    pylex = Python3Lexer()
    # lets build the string to parse
    syntax = ''
    walk = editorObj.lineLinkedList.start
    while walk != None:
        syntax += walk.value
        walk = walk.nextNode

    walk = editorObj.lineLinkedList.start

    i = 0 # index of where i am walking through the string

    for token in pylex.get_tokens(syntax):

        if token[1] == '\n':
            walk = walk.nextNode
            i = -1
            if walk == None:
                break

        #tokenType = SyntaxColors.TEXT.value # assume everything is text and find contradiction
        tokenType = colorMap['TEXT'] # assume everything is text and find contradiction

        if pygments.token.Comment.Single == token[0]:
            #tokenType = SyntaxColors.COMMENT.value
            tokenType = colorMap['COMMENT']

        if pygments.token.Keyword.Namespace == token[0]:
            #tokenType = SyntaxColors.NAMESPACE.value
            tokenType = colorMap['NAMESPACE']

        if pygments.token.Keyword == token[0]:
            #tokenType = SyntaxColors.KEYWORD.value
            tokenType = colorMap['KEYWORD']

        if pygments.token.Name.Builtin == token[0]:
            #tokenType = SyntaxColors.BUILTIN.value
            tokenType = colorMap['BUILTIN']

        if pygments.token.Name.Function == token[0]:
            #tokenType = SyntaxColors.FUNCTION.value
            tokenType = colorMap['FUNCTION']

        if pygments.token.Literal.Number.Integer == token[0] or pygments.token.Literal.Number.Float == token[0]:
            #tokenType = SyntaxColors.LITERAL.value
            tokenType = colorMap['LITERAL']

        if pygments.token.Operator == token[0]:
            #tokenType = SyntaxColors.OPERATOR.value
            tokenType = colorMap['OPERATOR']

        if pygments.token.Literal.String.Single == token[0] or pygments.token.Literal.String.Double == token[0]:
            #tokenType = SyntaxColors.STRING_LITERAL.value
            tokenType = colorMap['STRING_LITERAL']


        for c in token[1]:
            walk.colors[i] = tokenType
            i += 1
