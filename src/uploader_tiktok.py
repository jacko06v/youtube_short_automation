import requests, json, time
from src.util import assertSuccess,printError,getTagsExtra,uploadToTikTok,log, getCreationId
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'

def uploadVideo(session_id, video, title, tags, users = [], url_prefix = "us", schedule_time = 0):
	session = requests.Session()

	session.cookies.set("sessionid", session_id, domain=".tiktok.com")
	session.verify = True
	headers = {
		'User-Agent': UA
	}
	url = f"https://{url_prefix}.tiktok.com/upload/"
	r = session.get(url,headers = headers)
	if not assertSuccess(url, r):
		return False
	creationid = getCreationId()
	url = f"https://{url_prefix}.tiktok.com/api/v1/web/project/create/?creation_id={creationid}&type=1&aid=1988"
	headers = {
		"X-Secsdk-Csrf-Request":"1",
		"X-Secsdk-Csrf-Version":"1.2.8"
	}
	r = session.post(url, headers=headers)
	if not assertSuccess(url, r):
		return False
	try:
		tempInfo = r.json()['project']
	except KeyError:
		print("[-] An error occured while reaching {url}")
		print("[-] Please try to change the --url_server argument to the adapted prefix for your account")
	creationID = tempInfo["creationID"]
	projectID = tempInfo["project_id"]
	url = f"https://{url_prefix}.tiktok.com/passport/web/account/info/"
	r = session.get(url)
	if not assertSuccess(url, r):
		return False
	log("Caricamento video su tiktok")
	video_id = uploadToTikTok(video,session)
	if not video_id:
		log('caricamento fallito')
		return False
	log("Video caricato correttamente")
	time.sleep(2)
	result = getTagsExtra(title,tags,users,session,url_prefix)
	time.sleep(3)
	title = result[0]
	text_extra = result[1]
	url = f"https://{url_prefix}.tiktok.com/api/v1/web/project/post/?aid=1988"
	data = {
		"upload_param": {
			"video_param": {
				"text": title,
				"text_extra": text_extra,
				"poster_delay": 0
			},
			"visibility_type": 0,
			"allow_comment": 1,
			"allow_duet": 1,
			"allow_stitch": 1,
			"sound_exemption": 0,
			"geofencing_regions": [],
			"creation_id": creationID,
			"is_uploaded_in_batch": False,
			"is_enable_playlist": False,
			"is_added_to_playlist": False,
			"schedule_time": schedule_time
		},
		"project_id": projectID,
		"draft": "",
		"single_upload_param": [],
		"video_id": video_id
	}
	headers = {
		# "X-Secsdk-Csrf-Token": x_csrf_token,
		'Host': f'{url_prefix}.tiktok.com',
		'authority': 'tiktok.com',
		'pragma': 'no-cache',
		'cache-control': 'no-cache',
		'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
		'accept': 'application/json, text/plain, */*',
		'content-type': 'application/json',
		'sec-ch-ua-mobile': '?0',
		'user-agent': UA,
		'sec-ch-ua-platform': '"macOS"',
		'origin': 'https://www.tiktok.com',
		'sec-fetch-site': 'same-site',
		'sec-fetch-mode': 'cors',
		'sec-fetch-dest': 'empty',
		'referer': 'https://www.tiktok.com/',    # network find vn tiktok, referer: https://us.tiktok.com/creator
		'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'
	}
	r = session.post(url, data=json.dumps(data), headers=headers)
	if not assertSuccess(url, r):
		log('Pubblicazione fallita')
		printError(url, r)
		return False
	if r.json()["status_code"] == 0:
		log('Video pubblicato correttamente')
	else:
		log('Pubblicazione fallita')
		printError(url, r)
		return False

	return True
