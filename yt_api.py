from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError 

class Youtube: # Interactions with Youtube API
    def __init__(self, api_key: str):
        self.__youtube = build(serviceName = 'youtube', version = 'v3', developerKey = api_key, cache_discovery = False)
    
    def search_playlists(self, query: str) -> dict | None:
        try:
            response = self.__youtube.search().list(
            q = query,
            type = 'playlist',
            part = 'snippet',
            relevanceLanguage = 'en',
            maxResults = 5
            ).execute()
        except HttpError as e:
            print(f"Error: {e.resp.status}, {e.content}")
            return None
        return response
    
    def playlists_validator(self, playlists: dict) -> int:
        if playlists is None: # An error occurred or the quota has expired
            return 2
        elif len(playlists['items']) == 0: # Youtube can't find any playlists for this query
            return 1 
        else: # Everything is fine
            return 0 
        
    class Playlist: # Object with description of youtube playlist
        def __init__(self, playlist: dict, api_key: str):
            self.__youtube = build(serviceName = 'youtube', version = 'v3', developerKey = api_key, cache_discovery = False)
            self.title = playlist['snippet']['title']
            self.playlist_id = playlist['id']['playlistId']
            self.url = "https://www.youtube.com/playlist?list=" + self.playlist_id
            self.__videos = self.__get_videos_from_playlist()
            self.video_count = len(self.__videos)
            self.__videos_ids = self.__get_videos_ids()
            self.__videos_info = self.__get_videos_info()
            self.__summary_duration = self.__get_summary_duration()
            self.summary_duration_hours = self.__summary_duration[0]
            self.summary_duration_minutes = self.__summary_duration[1]
            self.summary_duration_seconds = self.__summary_duration[2]
            self.__statistics = self.__get_statistics()
            self.summary_like_count = self.__statistics[0]
            self.summary_comment_count = self.__statistics[1] 
        
        def __get_videos_from_playlist(self) -> list:
            videos = []
            request = self.__youtube.playlistItems().list(
                part = 'snippet',
                playlistId = self.playlist_id,
                maxResults = 50
                )
            while request is not None:
                response = request.execute()
                for item in response['items']: 
                    videos.append(item)
                request = self.__youtube.playlistItems().list_next(
                    previous_request = request,
                    previous_response = response
                    )
            return videos
        
        def __get_videos_ids(self) -> list:
            videos_ids = []
            for video in self.__videos:
                video_id = video["snippet"]["resourceId"]["videoId"]
                videos_ids.append(video_id)
            return videos_ids
        
        def __get_videos_info(self) -> list:
            videos_ids_strs = []
            while len(self.__videos_ids) != 0:
                videos_ids_str = ""
                videos_ids_str = str(self.__videos_ids.pop(0))
                i = 1
                while (i < 50) and (len(self.__videos_ids) != 0):
                    videos_ids_str += f",{str(self.__videos_ids.pop(0))}"
                    i += 1
                videos_ids_strs.append(videos_ids_str)
            videos_info = []
            for ids_str in videos_ids_strs:
                request = self.__youtube.videos().list(
                    part='statistics,contentDetails',
                    id=ids_str,
                    maxResults=50
                )
                response = request.execute()
                for item in response['items']:
                    videos_info.append(item)
            return videos_info
        
        def __get_summary_duration(self) -> list:
            import re
            pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
            hours = 0
            minutes = 0
            seconds = 0
            for video in self.__videos_info:
                matched_duration = pattern.match(video['contentDetails']['duration'])
                if matched_duration is None:
                    return [hours, minutes, seconds]
                hours += int(matched_duration.group(1)) if matched_duration.group(1) else 0
                minutes += int(matched_duration.group(2)) if matched_duration.group(2) else 0
                seconds += int(matched_duration.group(3)) if matched_duration.group(3) else 0
            minutes += seconds // 60
            seconds = seconds % 60
            hours += minutes // 60
            minutes = minutes % 60
            return [hours, minutes, seconds]
        
        def __get_statistics(self):
            summary_like_count = 0
            summary_comment_count = 0
            for video in self.__videos_info:
                if 'likeCount' in video['statistics']:
                    summary_like_count += int(video['statistics']['likeCount'])
                if 'commentCount' in video['statistics']:
                    summary_comment_count += int(video['statistics']['commentCount'])
            return [summary_like_count, summary_comment_count]