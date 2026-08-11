import re

def translate_mock(text_to_translate):
    # Mock translation that adds spaces and lowers cases
    return text_to_translate.lower().replace("mthblk", "mthblk ")

text = "Calculate the derivative of \(f(x) = x^2\) and \[ \\int x dx \]"
math_pattern = re.compile(r'(\\\(.*?\\\)|\\\[.*?\\\]|\$\$.*?\$\$)', re.DOTALL)
math_blocks = []

def replacer(match):
    math_blocks.append(match.group(0))
    return f" MTHBLK{len(math_blocks)-1} "

text_to_translate = math_pattern.sub(replacer, text)
print("Before translation:", text_to_translate)

translated_text = translate_mock(text_to_translate)
print("After translation:", translated_text)

for i, block in enumerate(math_blocks):
    placeholder_pattern = re.compile(r'mthblk\s*' + str(i), re.IGNORECASE)
    translated_text = placeholder_pattern.sub(lambda m: block, translated_text)

print("Restored:", translated_text)
