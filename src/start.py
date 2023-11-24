
import os
import requests
import json
import sys
import ssl
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
import httplib2
import datetime
import argparse
from src.uploader_tiktok import uploadVideo
from src.uploader_yt import initialize_upload
from src.download_video import download
import src.constant as const
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials



#dot env
from dotenv import load_dotenv
load_dotenv()



ssl._create_default_https_context = ssl._create_stdlib_context
os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   const.CLIENT_SECRETS_FILE))
should_upload_to_tiktok = False

def get_authenticated_service():
    #authenticate
    flow = flow_from_clientsecrets(const.CLIENT_SECRETS_FILE, scope=const.YOUTUBE_UPLOAD_SCOPE,
        message=const.MISSING_CLIENT_SECRETS_MESSAGE)
    #if %s-oauth2.json" % sys.argv[0] exist
    credentials = None
    storage = Storage("./src/memory/%s-oauth2.json" % sys.argv[0])
    if os.path.exists("./src/memory/%s-oauth2.json" % sys.argv[0]):
        credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)
    return build(const.YOUTUBE_API_SERVICE_NAME, const.YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()))

  



def download_video(url, id):
   
    video_path = download(url)
    if video_path == "Error":
        return 
    #from path keep only filename
    video_name = os.path.basename(video_path)
    #remove .mp4 from filename
    video_name = video_name.split(".")[0]
    #get video id from url
    url_request = f"https://www.googleapis.com/youtube/v3/videos?key=AIzaSyDkvH00R8o5ruYs7kpsp0IFYEtHwNNaWsI&fields=items(snippet(title,description,tags))&part=snippet&id={id}"
    response = requests.get(url_request)
    data = response.json()
    #get tags from video
    tags = ""
    tagsArray = ""
    try:
        tagsArray = data["items"][0]["snippet"]["tags"]
        tags = ",".join(tagsArray)
    except:
        pass
    

    print(video_name)
    #upload video to youtube
    youtube = get_authenticated_service()
    #check last upload time
    with open('./src/memory/uploaded.json') as json_file:
        data = json.load(json_file)

    last_upload = data["uploaded_video"][-1]["publishAt"]
    #upload video following hours_to_upload, if the last upload is at 22:00:00, upload at 10:00:00 of the next day
    #get date and hour from a date like 2023-06-06T15:00:00.000Z
    hour_uploaded_last = last_upload.split("T")[1].split(".")[0]
    date_uploaded_last = last_upload.split("T")[0]
    #find the index of the hour in the list
    index = const.HOURS_TO_UPLOAD.index(hour_uploaded_last)
    #if the index is the last one, upload at 10:00:00 of the next day
    if index == len(const.HOURS_TO_UPLOAD) - 1:
        index = 0
        date_uploaded_last = datetime.datetime.strptime(date_uploaded_last, '%Y-%m-%d')
        date_uploaded_last += datetime.timedelta(days=1)
        date_uploaded_last = date_uploaded_last.strftime('%Y-%m-%d')
    else:
        index += 1
    #get the hour to upload
    hour_to_upload = const.HOURS_TO_UPLOAD[index]
    #get the date to upload
    date_to_publish = f"{date_uploaded_last}T{hour_to_upload}.000Z"

    #convert date_to_publish to timestamp
    dateTikTok = datetime.datetime.strptime(date_to_publish, '%Y-%m-%dT%H:%M:%S.000Z')
    dateTikTok = dateTikTok.timestamp()
    int(dateTikTok)


    options = dict(
        file=video_path,
        title=video_name,
        description="Subscribe to @peakyclips for more videos like this! \n #shorts #peakyclips #podcast #andrewtate #sigma",
        keywords=tags,
        category="24",
        privacyStatus="private",
        publishAt= date_to_publish
    )
    initialize_upload(youtube, options)
    if should_upload_to_tiktok:
        #upload video to tiktok
        session_id = os.getenv("SESSION_ID")
        uploadVideo(session_id, video_path, "", tagsArray, [], "www")
    #delete video from downloaded folder
    os.remove(video_path)


def get_shorts_links(idChannel):
  
    api_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={idChannel}&maxResults=5&q=&type=video&key=AIzaSyDkvH00R8o5ruYs7kpsp0IFYEtHwNNaWsI"
    
    response = requests.get(api_url)
    data = response.json()

    ids = []
    shorts_links = []

    for item in data["items"]:
        video_id = item["id"]["videoId"]
        link = f"https://www.youtube.com/shorts/{video_id}"
        shorts_links.append(link)
        ids.append(video_id)
    
    with open('./src/memory/links.json') as json_file:
        data = json.load(json_file)

    links = []
    for linki in shorts_links:
        if linki not in data["links"]:
            links.append(linki)
        
    return links, ids


def upload_one_video_only(link):
    idLink = link.split("/")[4]
    download_video(link, idLink)

def upload_video_from_channels():
    idChannels = [
        "UCP-7Qvx57rJN7uz3k4zLf7A",
        "UCaM6K7gFbo4qBPNynPt7q2g",
        "UCQd6sUvKV4wh3jYCs647QKQ",
        "UCjqXzVkLqdWAVV3pp3BBsxQ",
        "UCC11jFT2F7OPOEPXZxs6GEw",
        "UCgh5l4MxpVw4SwQX3hbuxHg"
    ]
    for IDChannel in idChannels:
        links, ids = get_shorts_links(IDChannel)
        for index, link in enumerate(links):
            download_video(link, ids[index])
            with open('./src/memory/links.json') as json_file:
                data = json.load(json_file)
            print(const.YELLOW % "New link added to json file")
            data["links"].append(link)
            #write new link to json file
            with open('./src/memory/links.json', 'w') as outfile:
                json.dump(data, outfile)

def main():
    global should_upload_to_tiktok
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--link', help='Link to upload')
    parser.add_argument('-t', '--tiktok', help='should upload to tiktok', action='store_true')
    parser.add_argument('-c', '--channel', help='Upload from channels', action='store_true')
    args = parser.parse_args()

    #check if session id is set
 
    if os.path.exists("./src/memory/%s-oauth2.json" % sys.argv[0]):

        credentials = Credentials.from_authorized_user_file("./src/memory/%s-oauth2.json" % sys.argv[0])
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            print(const.GREEN % "Credentials refreshed")
        else:
            print(const.GREEN % "Credentials not expired")
    else:
          print(const.GREEN % "Token non trovato, verrà richiesto di crearne uno nuovo")

    if args.tiktok:
        should_upload_to_tiktok = True
        if os.getenv("SESSION_ID") is None:
            print(const.RED % "Session id not set")
            exit()
        else:
            print(const.GREEN % "Session id: ", os.getenv("SESSION_ID"))


    if args.link:
        print(const.GREEN % "Uploading one video only from link: ", args.link)
        upload_one_video_only(args.link)
    elif args.channel:
        print(const.GREEN % "Uploading from channels")
        #remove args.channel from sys.argv
        sys.argv.remove("-c")

        upload_video_from_channels()
    else:
        print(const.RED % "No arguments passed")
        print("\n")
        print(const.YELLOW % "use -h or --help for help")
        exit()

    
    print(const.GREEN % "Everything done")


