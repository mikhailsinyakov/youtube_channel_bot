import requests

from dotenv import dotenv_values
import prettytable as pt

from helpers import make_readable, prettify_number, trim_string

config = dotenv_values(".env")

def change_channel_keys(data):
    changes = {
        "title": "Title",
        "subscribers_count": "# subs",
        "videos_count": "# videos",
        "total_views": "# views",
        "average_views_by_video": "Avg views",
        "channel_id": "id"
    }

    new_data = []

    for channel_info in data:
        new_dict = {}

        for key in channel_info.keys():
            if key in changes.keys():
                new_dict[changes[key]] = channel_info[key]
            elif key != "channel_url":
                new_dict[key] = channel_info[key]
        new_data.append(new_dict)
    
    return new_data
    

def generate_html_table(data):
    html = "<table>"
    html += "<thead>"
    
    for key in data[0].keys():
        html += f"<th>{make_readable(key)}</th>"

    html += "</thead>"
    html += "<tbody>"

    for row in data:
        html += "<tr>"

        for val in row.values():
            html += f"<td>{prettify_number(val) if isinstance(val, int) else trim_string(val, 20)}</td>"

        html += "</tr>"

    html += "</tbody>"
    html += "</table>"

    return html

def create_image_url(html_table):
    with open("table.css") as f:
        css = f.read()

    user_id = config["HTMLCSS_TO_IMAGE_USER_ID"]
    api_key = config["HTMLCSS_TO_IMAGE_API_KEY"]
    api_url = "https://hcti.io/v1/image"

    data = {
        "html": html_table,
        "css": css,
        "selector": "table"
    }
    r = requests.post(api_url, auth=(user_id, api_key), json=data)
    
    if r.status_code not in [200, 201]:
        return None
    results = r.json()

    return results["url"]

def get_image(image_url):
    r = requests.get(image_url)
    return r.content

def get_table_image(data):
    data = change_channel_keys(data)
    html_table = generate_html_table(data)
    image_url = create_image_url(html_table)
    return None if image_url is None else get_image(image_url)

def get_pretty_table(data):
    data = change_channel_keys(data)
    table = pt.PrettyTable(data[0].keys())
    for channel in data:
        table.add_row([prettify_number(v) if isinstance(v, int) else trim_string(v, 15) for v in channel.values()])
    
    return f"<pre>{table}</pre>"