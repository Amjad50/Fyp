# taken from https://tex.stackexchange.com/questions/34054/tex-to-image-over-command-line
formula_strap = r"""
\ifdefined\formula
\else
    \def\formula{E = m c^2}
\fi
\documentclass[border=2pt,varwidth]{standalone}
\usepackage{standalone}
\usepackage{amsmath}
\begin{document}
\[ \formula \]
\end{document}
"""

latex_strap = "\\def\\formula{{{{{expression}}}}}\\input{{{{formula.tex}}}}"
#"""
#\\documentclass[preview, margin=5pt]{{{{standalone}}}}
#\\begin{{{{document}}}}
#$$ {expression} $$
#\\end{{{{document}}}}
#"""

def generate_latex_template(expression):
    return latex_strap.format(expression=expression)

