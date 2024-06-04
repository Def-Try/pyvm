def parse(string):
    flags = [""]
    args = [""]
    flag = False
    one_letter_flag = False
    for ch in string:
        if ch == "-":
            if flag and one_letter_flag:
                one_letter_flag = False
                continue
            if flag and not one_letter_flag:
                flags[-1] += "-"
                continue
            flag = True
            one_letter_flag = True
            continue
        if ch == " ":
            if flag:
                flags.append("")
            else:
                args.append("")
            flag = False
            one_letter_flag = False
        if flag and not one_letter_flag:
            flags[-1] += ch
        elif flag:
            flags[-1] += ch
            flags.append("")
        else:
            args[-1] += ch
    return [i.strip() for i in flags], [i.strip() for i in args]
