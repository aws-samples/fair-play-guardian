'''
Fair Play Guardian - Collusion Detection in Multiplayer Online Gaming through Profile Picture Validation.

Collusion detection in multiplayer online gaming has seen a rise, with players now uploading their 
profile pictures along with their cell phone numbers. 
This facilitates easy communication among players, enabling them to collaborate and engage in collusion 
or cheating activities aimed at gaining an unfair advantage over others during gameplay. 
Those participating in collusion efforts cooperate to assist one another, share information, 
or deliberately lose in order to favor a particular player or group of players.

This application provides a remedy for identifying collusion in multiplayer online gaming by verifying the profile picture. 
Upon the user's upload of the profile picture, the application uses Amazon Textract to recognize text within the image 
promptly. Subsequently, it applies a Gaussian blur filter to obscure the detected text.

'''   

import os
import sys
import traceback
import logging
import json
import boto3
import io
from urllib.parse import unquote_plus
from PIL import Image, ImageDraw, ImageFilter
from constants import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)

'''
This function is used to process errors that occur during the execution of the lambda function.

Returns
------
It returns a dictionary containing the error type, error message, and stack trace.
The error type, error message, and stack trace are then logged using the logger for further troubleshooting.
'''
def process_error() -> dict:
    exType, exValue, exTraceback = sys.exc_info()
    tracebackString = traceback.format_exception(exType, exValue, exTraceback)
    errorMsg = json.dumps(
        {
            ERROR_TYPE: exType.__name__,
            ERROR_MESSAGE: str(exValue),
            STACK_TRACE: tracebackString,
        }
    )
    return errorMsg

'''
This function is used to blur the text detected by Amazon Textract in the image.
It uses the GaussianBlur filter to blur the text in the image

Parameters
----------
It takes in the source image, and the text box coordinates of the image to blur as input

Returns
------
It returns the blurred image for further processing as needed
'''
def blur_text_in_image(imageToProcess, textBox):
    # Get the image width and height, use that
    # along with the textBox coordinates to get 
    # the exact coordinates to mask/blur
    imgwidth, imgheight = imageToProcess.size
    left = int(imgwidth * textBox[LEFT])
    top = int(imgheight * textBox[TOP])
    width = int(imgwidth * textBox[WIDTH])
    height = int(imgheight * textBox[HEIGHT])
    logging.info(f"Left: {left}, Top: {top}, Width: {width}, Height: {height}")

    # Create a mask to blur the text in the image
    mask = Image.new('L', imageToProcess.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle([left,top, left + width, top + height], fill=255)
    blurredText = imageToProcess.filter(ImageFilter.GaussianBlur(52))
    imageToProcess.paste(blurredText, mask=mask)

    return imageToProcess    

'''
This lambda function is triggered by an S3 PUT event when a new profile picture is uploaded to the S3 bucket.
It uses Amazon Textract to detect text in the image and then blurs the text using a Gaussian blur filter.
An SNS topic is also configured to send a notification to the collusion fraud detection team to review the 
blurred image and determine the future course of action. 

Parameters
----------
event: dict, required
    
context: object, required
    Lambda Context runtime methods and attributes

'''
def lambda_handler(event, context):
    
    textract    = boto3.client(TEXTRACT)
    sns         = boto3.client(SNS)
    s3          = boto3.client(S3)
    textList   = []
    
    try:
        if RECORDS in event:
            # Get the bucket and file name for processing  
            imageFileObj = event[RECORDS][0]
            bucketName = str(imageFileObj[S3][BUCKET][NAME])
            fileName = unquote_plus(str(imageFileObj[S3][OBJECT][KEY]))
            
            logging.info(f"Bucket: {bucketName} ::: Key: {fileName}")

            # We need to get the file format as some file formats 
            # need some pre-procesing to be done before validation
            picFileNname = os.path.basename(fileName)
            originalFile = os.path.splitext(picFileNname)  
            logging.info(f"Filename: {originalFile[0]} ::: Extension: {originalFile[1]}")
            fileFormat = originalFile[1].replace('.', '')
            logging.info(f"File Format: {fileFormat}")

            # Download the image from S3 into a BytesIO object
            s3Response = s3.get_object(Bucket=bucketName, Key=fileName)
            imageToProcess = Image.open(io.BytesIO(s3Response[BODY].read()))
            
            # if fileformat is png convert the file to RGB before processing
            if fileFormat == PNG:
                imageToProcess = imageToProcess.convert(RGB)

            # Detect all text elements in image file
            textractresponse = textract.detect_document_text(
                Document={
                    S3OBJECT: {
                        BUCKETNAME: bucketName,
                        FILENAME: fileName,
                    }
                }
            )
            
            # Loop through textract response blocks and blur text regions  
            for block in textractresponse[BLOCKS]:
                # We can also parse by LINE if required
                if block[BLOCK_TYPE] == WORD:
                    # Got a text block in the image
                    logging.info("Got text:- "+block[TEXT])
                    # Save the text in list for notification 
                    textList.append(block[TEXT])
                    # Get the text box coordinates to blur
                    textBox = block[GEOMETRY][BOUNDINGBOX]
                    # Invoke method to blur the text in the image
                    finalBlurredImage = blur_text_in_image(imageToProcess, textBox)
                    
            # If profile picture contained any text then upload the blurred image to a different  
            # processing bucket temporarily. Processing bucket is used to avoid a recursive invocation.
            # Copy the blurred image from processing bucket to the primary bucket
            # COPY event is not enbaled on primary bucket to prevent recursive invocation.   
            snsTopicArn = os.environ[SNS_TOPIC_ARN]
            if textList:
                
                # Save the blurred image temporarily in processing bucket. 
                processedImageOutput = io.BytesIO()
                # If file format is JPG convert it to JPEG
                if fileFormat == JPG:
                    fileFormat = JPEG
                finalBlurredImage.save(processedImageOutput, format=fileFormat)
                processedImageOutput.seek(0)
                s3.upload_fileobj(processedImageOutput, os.environ[PROCESSING_BUCKET_NAME], fileName)
                logging.info("Blurred image uploaded to processing bucket successfully")
                
                # Copy the blurred image from processing bucket to primary bucket
                copy_source = {BUCKETNAME: os.environ[PROCESSING_BUCKET_NAME], KEYNAME: fileName}
                s3.copy_object(CopySource=copy_source, Bucket=bucketName, Key=fileName)    
                logging.info("Blurred image copied to primary bucket successfully")
                
                # Delete the temporary blurred image from processing bucket
                s3.delete_object(Bucket=os.environ[PROCESSING_BUCKET_NAME], Key=fileName)
                logging.info("Temporary Blurred Image deleted from processing bucket successfully")    

                # convert list of text to string for notification.
                textInImage = str("  ".join(textList))
                
                notificationMessage =   NOTIFICATION_TO + PROFILE_PICTURE_PROCESSED +fileName+ PROFILE_PICTURE_BUCKET + \
                                        bucketName+ DETECTED_TEXT + textInImage + NEXT_STEPS + NOTIFICATION_FROM
                
                snsResponse = sns.publish (
                    TargetArn = snsTopicArn,
                    Message = json.dumps({'default': notificationMessage}),
                    MessageStructure = JSON
                )
                logging.info(json.dumps(snsResponse))
            # This is just here for debugging. Comment the elif block to disable compliant notification
            elif not textList:  
                notificationMessage = "The profile picture "+fileName +" in S3 bucket "+bucketName +" is compliant."
                snsResponse = sns.publish (
                    TargetArn = snsTopicArn,
                    Message = json.dumps({DEFAULT: notificationMessage}),
                    MessageStructure = JSON
                )
                logging.info(json.dumps(snsResponse))

            return {
                STATUS_CODE: 200,
                MESSAGE_BODY: json.dumps(SUCCESSFULLY_PROCESSED),
            }
    except:
        errorMsg = process_error()
        logger.error(errorMsg)

    return {STATUS_CODE: 500, MESSAGE_BODY: json.dumps(PROCESSING_FAILED)}