import json

def load_filters(user):
    with open(f"user_filters/{user}_filter.json") as file:
        filters = json.load(file)
        return filters

def save_filters(user, filters):
    with open(f"user_filters/{user}_filter.json", "w") as file:
        json.dump(filters, file)

def change_filter_property(user, prop_name, lower_limit_new_val, upper_limit_new_val):
    filters = load_filters(user)
    filters[prop_name] = [lower_limit_new_val, upper_limit_new_val]
    save_filters(user, filters)
