import pygments
from pygments.lexers import Python3Lexer
from constants import SyntaxColors, Colors

from Util.cursesUtil import kill

def setColors(editorObj):
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

            tokenType = SyntaxColors.TEXT.value # assume everything is text and find contradiction

            if pygments.token.Comment.Single == token[0]:
                tokenType = SyntaxColors.COMMENT.value

            if pygments.token.Keyword.Namespace == token[0]:
                tokenType = SyntaxColors.NAMESPACE.value

            if pygments.token.Keyword == token[0]:
                tokenType = SyntaxColors.KEYWORD.value

            if pygments.token.Name.Builtin == token[0]:
                tokenType = SyntaxColors.BUILTIN.value

            if pygments.token.Name.Function == token[0]:
                tokenType = SyntaxColors.FUNCTION.value

            if pygments.token.Literal.Number.Integer == token[0] or pygments.token.Literal.Number.Float == token[0]:
                tokenType = SyntaxColors.LITERAL.value

            if pygments.token.Operator == token[0]:
                tokenType = SyntaxColors.OPERATOR.value

            if pygments.token.Literal.String.Single == token[0] or pygments.token.Literal.String.Double == token[0]:
                tokenType = SyntaxColors.STRING_LITERAL.value


            for c in token[1]:
                walk.colors[i] = tokenType
                i += 1
