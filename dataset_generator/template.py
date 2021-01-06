latex_strap = """
\\documentclass[preview, margin=5pt]{{{{standalone}}}}
\\begin{{{{document}}}}
$$ {expression} $$
\\end{{{{document}}}}
"""

def generate_latex_template(expression):
    return latex_strap.format(expression=expression)

