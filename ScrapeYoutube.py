import googleapiclient.discovery
import pandas as pd


def get_youtube_service():
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "Your Api_KEy"

    return googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)


def get_channel_videos(channel_id, max_results=50):
    youtube = get_youtube_service()
    video_ids = []
    next_page_token = None

    while True:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=max_results,
            type="video",
            pageToken=next_page_token
        )
        response = request.execute()

        video_ids.extend(item['id']['videoId'] for item in response.get('items', []))

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids


def get_video_details(video_ids):
    youtube = get_youtube_service()

    videos = []
    for i in range(0, len(video_ids), 50):  # YouTube API allows up to 50 IDs per request
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics,status,topicDetails",
            id=",".join(video_ids[i:i + 50])
        )
        response = request.execute()

        for item in response.get('items', []):
            content_details = item.get('contentDetails', {})
            video_data = {
                "video_id": item['id'],
                "title": item['snippet']['title'],
                "description": item['snippet'].get('description', ''),
                "published_at": item['snippet']['publishedAt'],
                "channel_id": item['snippet']['channelId'],
                "channel_title": item['snippet']['channelTitle'],
                "tags": item['snippet'].get('tags', []),
                "category_id": item['snippet']['categoryId'],
                "length": content_details.get('duration', ''),
                "definition": content_details.get('definition', ''),
                "caption": content_details.get('caption', ''),
                "licensed_content": content_details.get('licensedContent', False),
                "view_count": item['statistics'].get('viewCount', 0),
                "like_count": item['statistics'].get('likeCount', 0),
                "dislike_count": item['statistics'].get('dislikeCount', 0),
                # Note: YouTube may not provide this anymore
                "favorite_count": item['statistics'].get('favoriteCount', 0),
                "comment_count": item['statistics'].get('commentCount', 0),
                "privacy_status": item['status']['privacyStatus'],
                "license": item['status'].get('license', ''),
                "embeddable": item['status'].get('embeddable', False),
                "public_stats_viewable": item['status'].get('publicStatsViewable', False),
                "age_restricted": 'ytRating' in content_details.get('contentRating', {}),
                # Check if age restriction is present
                "made_for_kids": item['status'].get('madeForKids', False)  # Check if video is made for kids
            }
            videos.append(video_data)

    return videos


# Fetch data
channel_id = "UCfbnTUxUech4P1XgYUwYuKA"  # Cold Ones Official Channel To Try
video_ids = get_channel_videos(channel_id)
if video_ids:
    video_details = get_video_details(video_ids)

    # Convert to DataFrame
    df = pd.DataFrame(video_details)

    # Save to CSV
    csv_file_path = channel_id+"youtube_videos.csv"
    df.to_csv(csv_file_path, index=False)
    print(f"Data saved to {csv_file_path}")
else:
    print("No videos found for the specified channel.")
