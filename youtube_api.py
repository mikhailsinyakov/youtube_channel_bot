from dotenv import dotenv_values
import requests
from urllib.parse import urlencode

config = dotenv_values(".env")

def get_channel_ids(query, n_results):
    search_url = "https://www.googleapis.com/youtube/v3/search?"

    def get_ids(n_res, page_token=None):
        if n_res <= 0:
            return []
        max_results = 50 if n_res > 50 else 5 if n_res < 5 else n_res
        query_params = {
            "key": config["GOOGLE_API_KEY"],
            "part": "snippet",
            "q": query,
            "type": "channel",
            "maxResults": max_results
        }
        if page_token is not None:
            query_params["pageToken"] = page_token
        r = requests.get(search_url + urlencode(query_params))
        if r.status_code != 200:
            return []
        results = r.json()
        next_page_token = results["nextPageToken"]
        items = [channel["id"]["channelId"] for channel in results["items"]]

        return items[:n_res] + get_ids(n_res-max_results, next_page_token)
    
    return get_ids(n_results)

def get_channel_info(channel_id):
    channel_url = "https://www.googleapis.com/youtube/v3/channels?"
    query_params = {
        "key": config["GOOGLE_API_KEY"],
        "part": "snippet,statistics",
        "id": channel_id
    }
    
    r = requests.get(channel_url + urlencode(query_params))
    if r.status_code != 200:
        return {}
    channel_info = r.json()["items"][0]
    stats = channel_info["statistics"]
    
    return {
        "title": channel_info["snippet"]["title"],
        "subscribers_count": int(stats["subscriberCount"]),
        "videos_count": int(stats["videoCount"]),
        "total_views": int(stats["viewCount"]),
        "average_views_by_video": int(stats["viewCount"]) / int(stats["videoCount"])
    }

def get_channels(query, n_results):
    return [get_channel_info(ch_id) for ch_id in get_channel_ids(query, n_results)]

if __name__ == "__main__":
    print(get_channels("zenit", 5))