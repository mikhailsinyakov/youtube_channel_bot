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

def clear_filters(user):
    filters = {
            "subscribers_count": [0, "no_upper_limit"], 
            "videos_count": [0, "no_upper_limit"], 
            "total_views": [0, "no_upper_limit"], 
            "average_views_by_video": [0, "no_upper_limit"]
        }

    save_filters(user, filters)

def create_user_filters(user):
    clear_filters(user)