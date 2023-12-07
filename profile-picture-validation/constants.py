# Constants - constants.py

# AWS Service
SNS = "sns"
TEXTRACT = "textract"
S3 = "s3"

# AWS S3
BODY = "Body"
BUCKET = "bucket"
KEY = "key"
NAME = "name"
OBJECT = "object"
PROCESSING_BUCKET_NAME = "PROCESSING_BUCKET_NAME"
SOURCE_BUCKET_NAME = "SOURCE_BUCKET_NAME"
S3OBJECT = "S3Object"
BUCKETNAME = "Bucket"
FILENAME = "Name"
KEYNAME = "Key"

# AWS SNS
SNS_TOPIC_ARN = "SNS_TOPIC_ARN"
DEFAULT = "default"
JSON = "json"
SUCCESSFULLY_PROCESSED = "Profile Picture has been verified sucessfully !"
PROCESSING_FAILED = "There was an error while verifying the profile picture !"
PROFILE_PICTURE_PROCESSED = "The profile picture uploaded by a player :- "
PROFILE_PICTURE_BUCKET = " stored in this S3 bucket :- "
DETECTED_TEXT = " has been identified as non-compliant as per the security standards pertaining to collusion detection.\n\nIt was observed to contain the following text elements: - \n"
NEXT_STEPS = "\n\nTo address this concern, the text elements in the image have been masked. We kindly request you to review the image and implement necessary actions."
NOTIFICATION_FROM="\n\nSincerely,\nFair Play Guardian (FPG) Application Team"
NOTIFICATION_TO="Dear Collusion Detection Security Team, \n\n"

# AWS LAMBDA Event
RECORDS = "Records"

# AWS Textract Response
BLOCKS = "Blocks"
BLOCK_TYPE = "BlockType"
PAGE = "Page"
LINE = "LINE"
WORD = "WORD"
LEFT  = "Left"
RIGHT = "Right"
TOP = "Top"
WIDTH = "Width"
HEIGHT = "Height"
GEOMETRY = "Geometry"
BOUNDINGBOX = "BoundingBox"
TEXT = "Text"

# IMAGE Processing
PNG = "png"
JPEG = "jpeg"
JPG = "jpg"
RGB = "RGB"

# ERROR & LOG Management
ERROR = "ERROR"
ERROR_MESSAGE = "errorMessage"
ERROR_TYPE = "errorType"
STACK_TRACE = "stackTrace"
STATUS_CODE = "statusCode"
MESSAGE_BODY = "body"
