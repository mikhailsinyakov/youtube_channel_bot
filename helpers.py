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