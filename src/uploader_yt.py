import json
import random
import time
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
import src.constant as constant

def initialize_upload(youtube, options):
    tags = None
    if options["keywords"]:
        tags = options["keywords"].split(",")
    body=dict(
        snippet=dict(
            title=options["title"],
            description=options["description"],
            tags=tags,
            categoryId=options["category"]
        ),
        status=dict(
            privacyStatus=options["privacyStatus"],
            selfDeclaredMadeForKids=False,
            publishAt=options["publishAt"]
        )
    )
    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(list(body.keys())),
        body=body,
        media_body=MediaFileUpload(options["file"], chunksize=-1, resumable=True)
    )
    resumable_upload(insert_request, options)

def resumable_upload(insert_request, options):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()

                if response is not None:
                    if 'id' in response:
                        print("\n")
                        print(constant.GREEN % "Video id '%s' was successfully uploaded at link: https://youtube.com/shorts/%s" % (response['id'], response['id']))
                    else:
                        exit(constant.RED % "The upload failed with an unexpected response: %s" % response)
            except HttpError as e:
                if e.resp.status == 403 or e.resp.status == 400:
                    exit(constant.RED % "The request cannot be completed because you have exceeded your quota, wait 24h.")
                else:
                    raise
        except HttpError as e:
            if e.resp.status in constant.RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,e.content)
            else:
                raise
        except constant.RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e
        if error is not None:
            print(error)
            retry += 1
            if retry > constant.MAX_RETRIES:
                exit("No longer attempting to retry.")
            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)
    
    with open('./src/memory/uploaded.json') as json_file:
        data = json.load(json_file)
    
    video = {
        "id": response["id"],
        "title": options["title"],
        "description": options["description"],
        "tags": options["keywords"],
        "category": options["category"],
        "privacyStatus": options["privacyStatus"],
        "publishAt": options["publishAt"],
        "link": f"https://youtube.com/shorts/{response['id']}"
    }
    data["uploaded_video"].append(video)
    with open('./src/memory/uploaded.json', 'w') as outfile:
        json.dump(data, outfile)

