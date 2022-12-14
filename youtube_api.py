from dotenv import dotenv_values
import requests
from urllib.parse import urlencode
import os

from change_filter import load_filters

def get_channel_ids(query, page_token=None):
    search_url = "https://www.googleapis.com/youtube/v3/search?"

    query_params = {
        "key": os.environ.get("GOOGLE_API_KEY"),
        "part": "snippet",
        "q": query,
        "type": "channel",
        "maxResults": 50
    }
    if page_token is not None:
        query_params["pageToken"] = page_token
    r = requests.get(search_url + urlencode(query_params))
    if r.status_code != 200:
        return ([], None)
    results = r.json()
    next_page_token = results["nextPageToken"]
    items = [channel["id"]["channelId"] for channel in results["items"]]

    return (items, next_page_token)

def get_channel_info(channel_id, filters):
    channel_url = "https://www.googleapis.com/youtube/v3/channels?"
    query_params = {
        "key": os.environ.get("GOOGLE_API_KEY"),
        "part": "snippet,statistics",
        "id": channel_id
    }
    
    r = requests.get(channel_url + urlencode(query_params))
    if r.status_code != 200:
        return None
    channel_info = r.json()["items"][0]
    stats = channel_info["statistics"]

    info = {
        "title": channel_info["snippet"]["title"],
        "subscribers_count": int(stats["subscriberCount"]),
        "videos_count": int(stats["videoCount"]),
        "total_views": int(stats["viewCount"]),
        "average_views_by_video": int(int(stats["viewCount"]) / int(stats["videoCount"])) if int(stats["videoCount"]) != 0 else 0
    }
    custom_url = channel_info["snippet"].get("customUrl")
    info["channel_url"] = f"https://www.youtube.com/{f'c/{custom_url}' if custom_url else f'channel/{channel_id}'}"

    for filter_key in filters.keys():
        value = info[filter_key]
        lower_limit = filters[filter_key][0]
        upper_limit = filters[filter_key][1]
        if not isinstance(upper_limit, int):
            upper_limit = float("inf")
        if value < lower_limit or value > upper_limit:
            return None

    return info

def get_filtered_channels(query, n_channels, filters):
    channels = []
    page_token = None
    keep_up = True
    while keep_up:
        channel_ids, next_page_token = get_channel_ids(query, page_token)
        keep_up = False
        for channel_id in channel_ids:
            channel_info = get_channel_info(channel_id, filters)
            if channel_info is not None:
                channels.append(channel_info)
                n_channels -= 1
                keep_up = n_channels > 0
                if not keep_up:
                    break
            
        page_token = next_page_token
    
    return channels

def get_channels(query, n_channels, user, keys=None):
    filters = load_filters(user)
    channels = get_filtered_channels(query, n_channels, filters)
    if keys is None:
        return channels
    
    channels_with_keys = []
    for i, channel in enumerate(channels):
        new_channel = {}
        new_channel["#"] = i + 1
        for key in keys:
            if key in channel:
                new_channel[key] = channel[key]
        channels_with_keys.append(new_channel)
    return channels_with_keys