import json

def load_filters():
    with open("search_filter.json") as file:
        filters = json.load(file)
        return filters

def save_filters(filters):
    with open("search_filter.json", "w") as file:
        json.dump(filters, file)

def change_filter_property(prop_name, lower_limit_new_val, upper_limit_new_val):
    filters = load_filters()
    filters[prop_name] = [lower_limit_new_val, upper_limit_new_val]
    save_filters(filters)
