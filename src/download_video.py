import pytube
import src.constant as constant
from src.watermark import add_watermark
def download(url):
    try:
        print(url)
        youtube = pytube.YouTube(url, use_oauth=True,  allow_oauth_cache=True)
        #get tags from video

        video_stream = youtube.streams.filter(file_extension='mp4').first()
        #download in downloaded folder
        video_path = video_stream.download('downloaded')
        add_watermark(video_path)
        return video_path
    except Exception as e:
        print(constant.RED % e)
        print(constant.RED % "Skipping video")
        return "Error"