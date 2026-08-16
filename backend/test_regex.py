import re
math_pattern = re.compile(r'(\\\(.*?\\\)|\\\[.*?\\\]|\$\$.*?\$\$|\$.*?\$)', re.DOTALL)
text = r'The equation is $8x^2=99$ and $$y=mx+b$$.'
def replacer(match):
    print('MATCHED:', match.group(0))
    return 'BLOCK'
print(math_pattern.sub(replacer, text))
