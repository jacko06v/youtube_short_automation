import httplib2

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
CLIENT_SECRETS_FILE = "./src/memory/client_secret.json"

GREEN = "\x1b[0;32m%s\x1b[0m"
RED = "\x1b[0;31m%s\x1b[0m"
YELLOW = "\x1b[0;33m%s\x1b[0m"
PURPLE = "\x1b[0;35m%s\x1b[0m"
CYAN = "\x1b[0;36m%s\x1b[0m"



MISSING_CLIENT_SECRETS_MESSAGE = ""

MAX_RETRIES = 10

HOURS_TO_UPLOAD = [ "18:00:00", "19:00:00"]

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]