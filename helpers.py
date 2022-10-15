import re

def make_readable(key):
    return key[0].upper() + key[1:].replace("_", " ")

def stringify_filters(filters):
    string_chunks = []
    for key in filters.keys():
        name = make_readable(key)
        val = filters[key]
        if val[0] == 0 and isinstance(val[1], str):
            filters_range = "all"
        elif val[0] == 0:
            filters_range = f"\u2264 {val[1]}"
        elif isinstance(val[1], str):
            filters_range = f"\u2265 {val[0]}"
        else:
            filters_range = f"{val[0]} \- {val[1]}"

        string_chunks.append(f"*{name}:* {filters_range}")
    return "\n".join(string_chunks)

def prettify_number(num):
    fourth_signif_digit = int(str(num)[3]) if num >= 1000 else 0
    signif_part = str(int(str(num)[:3]) + 1) if fourth_signif_digit > 4 else str(num)[:3]
    reduced_num = int(signif_part + re.sub(r"\d", "0", str(num)[3:]))
    letters = ["", "K", "M", "B"]

    for letter in letters:
        if reduced_num < 1000:
            break
        elif letter != "B":
            reduced_num /= 1000
    
    num_str = str(reduced_num)
    num_str = num_str.rstrip("0").rstrip(".") if "." in num_str else num_str

    return num_str + letter

def trim_string(string, max_len):
    if len(string) <= max_len:
        return string
    
    return string[:max_len-2] + ".."