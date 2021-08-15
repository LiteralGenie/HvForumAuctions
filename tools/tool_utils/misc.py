def strip_para(text, appos=True):
    split= text.split("\n")
    split= [x.strip() for x in split]
    ret= "\n".join(split)

    if not appos:
        ret= ret.replace("'", "\\'")

    return ret