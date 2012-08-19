def heading(text, level=2):
    return "{0} {1} {0}\n".format('#' * level, text)


def to_ascii(text):
    md = text
    charactermap = [["&#39;", "'"],
                    [u"\u2014", "-"],
                    [u"\xb5", "u"],
                    [u"\u2019", "'"],
                    [u"\u2295", "$% \oplus $%"],
                    [u"\xb7", "$% \cdot $%"],
                    [u"\u2192", "$% \to $%"],
                    [u"\xe9", "e"],
                    [u"\xe4", "a"]
                   ]

    for c in charactermap:
        md = md.replace(c[0], c[1])
    return md
