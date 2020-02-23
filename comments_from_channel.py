"""
-*- coding: utf-8 -*-
========================
Python YouTube API
========================

Developed by: Chirag Rathod (Srce Cde)
Email: chiragr83@gmail.com

========================
"""

import json
import sys
from urllib import *
import argparse
from urllib.parse import urlparse, urlencode, parse_qs
from urllib.request import  urlopen
import traceback
import csv

YOUTUBE_COMMENT_URL = 'https://www.googleapis.com/youtube/v3/commentThreads'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'


class YouTubeApi():

    def __init__(self):
        super().__init__()
        self.comment_count = 0

    def load_comments(self, mat, fp):
        for item in mat["items"]:
            comment = item["snippet"]["topLevelComment"]
            author = comment["snippet"]["authorDisplayName"]
            text = comment["snippet"]["textDisplay"]
            
            fp.writerow([self.comment_count, text])
            self.comment_count += 1
            # print("Comment by {}: {}".format(author, text))
            if 'replies' in item.keys():
                for reply in item['replies']['comments']:
                    rauthor = reply['snippet']['authorDisplayName']
                    rtext = reply["snippet"]["textDisplay"]
                    fp.writerow([self.comment_count, rtext])
                    self.comment_count += 1

                # print("\n\tReply by {}: {}".format(rauthor, rtext), "\n")

    def get_video_comment(self, fp, max_result, video_id, api_key):
        parser = argparse.ArgumentParser()
        mxRes = 20
        vid = str()
        


        try:
            videourl = 'https://www.youtube.com/watch?v=' + video_id
            video_id = urlparse(str(videourl))
            q = parse_qs(video_id.query)
            vid = q["v"][0]

        except:
            print("Invalid YouTube URL")

        parms = {
                    'part': 'snippet,replies',
                    'maxResults': max_result,
                    'videoId': vid,
                    'textFormat': 'plainText',
                    'key': api_key
                }

        try:

            matches = self.openURL(YOUTUBE_COMMENT_URL, parms)
            i = 2
            mat = json.loads(matches)
            nextPageToken = mat.get("nextPageToken")
            print("\nPage : 1")
            print("------------------------------------------------------------------")
            self.load_comments(mat, fp)

            while nextPageToken:
                parms.update({'pageToken': nextPageToken})
                matches = self.openURL(YOUTUBE_COMMENT_URL, parms)
                mat = json.loads(matches)
                nextPageToken = mat.get("nextPageToken")
                print("\nPage : ", i)
                print("------------------------------------------------------------------")

                self.load_comments(mat, fp)

                i += 1
        except KeyboardInterrupt:
            print("User Aborted the Operation")

        except:
            print("Cannot Open URL or Fetch comments at a moment")

    def load_channel_vid(self, search_response):
        video_ids = []
        videos = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append("{} ({})".format(search_result["snippet"]["title"],
                                         search_result["id"]["videoId"]))
                video_ids.append(search_result["id"]["videoId"])

        # print("###Videos:###\n", "\n".join(videos), "\n")
        return video_ids

    def channel_videos(self, channel_id, max_result, api_key):
        

        parms = {
                   'part': 'id,snippet',
                   'channelId': channel_id,
                   'maxResults': max_result,
                   'key': api_key
               }

        try:
            matches = self.openURL(YOUTUBE_SEARCH_URL, parms)

            search_response = json.loads(matches)

            i = 2

            nextPageToken = search_response.get("nextPageToken")
            print("\nPage : 1")
            print("------------------------------------------------------------------")

            video_ids = self.load_channel_vid(search_response)

            while nextPageToken:
                self.parms.update({'pageToken': nextPageToken})
                matches = self.openURL(YOUTUBE_SEARCH_URL, parms)

                search_response = json.loads(matches)
                nextPageToken = search_response.get("nextPageToken")
                print("Page : ", i)
                print("------------------------------------------------------------------")

                video_ids += self.load_channel_vid(search_response)

                i += 1

        except KeyboardInterrupt:
            print("User Aborted the Operation")

        except Exception as exception:
            traceback.print_exc()
            print("Cannot Open URL or Fetch comments at a moment")
        return video_ids

    def openURL(self, url, parms):
            f = urlopen(url + '?' + urlencode(parms))
            data = f.read()
            f.close()
            matches = data.decode("utf-8")
            return matches





    
if __name__ == '__main__':
    y = YouTubeApi()
    max_result = 20
    with open('api_key.json') as fp:
        api_key = json.load(fp).get('api_key')
    with open('channel_id.json') as fp:
        channels = json.load(fp)
    for channel_name, channel_id  in channels.items():
        video_ids = y.channel_videos(channel_id, max_result, api_key)
        fp = open('scrapped_comments/' + channel_name + '_comments.csv', 'w')
        writer = csv.writer(fp)
        writer.writerow(['comment_id', 'comment'])
        for video_id in video_ids:
            y.get_video_comment(writer, max_result, video_id, api_key)
        fp.close()
