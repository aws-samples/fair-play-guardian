# Fair Play Guardian - Collusion Detection in Multiplayer Online Gaming through Profile Picture Validation.

## Solution Overview 
Collusion detection in multiplayer online gaming has seen a rise, with players now uploading their 
profile pictures along with their cell phone numbers. This facilitates easy communication among players, enabling them to collaborate and engage in collusion or cheating activities aimed at gaining an unfair advantage over others during gameplay.   
Those participating in collusion efforts cooperate to assist one another, share information, or deliberately lose in order to favor a particular player or group of players.  
This solution provides a remedy for identifying collusion in multiplayer online gaming by verifying the profile picture. 
Upon the user's upload of the profile picture, the application uses Amazon Textract to recognize text within the image 
promptly. Subsequently, it applies a Gaussian blur filter to obscure the detected text.

## Architecture

![Diagram](/blob/main/FPG-Architecture.png)

## How it works
1. Users participating in online gaming can upload their profile pictures within the gaming application..
2. Uploaded profile pictures are securely stored in an S3 bucket with the PUT event functionality enabled.
3. The S3 PUT event serves as a trigger for a Lambda function, which executes the following steps: 
    - Utilizes the Amazon Textract API to identify and extract text from the image.
    - Applies a Gaussian blur filter to the text for privacy concerns.
    - Temporarily stores the blurred image in a processing bucket (_to avoid recursive invocation_).
    - Subsequently, replaces the original image in the primary bucket with the processed blurred image and deletes it from processing bnucket.
    - Sends a notification to the subscribed email address via SNS, providing information about the detection of potential collusion in the profile picture.

**Important Note:** 
This application leverages multiple AWS services, and there are associated costs beyond the Free Tier usage. Please refer to the [AWS Pricing page](https://aws.amazon.com/pricing/) for specific details. You are accountable for any incurred AWS costs. This example solution does not imply any warranty.

## Requirements
[Create an AWS account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in. The IAM user that you use must have sufficient permissions to make necessary AWS service calls and manage AWS resources.  
[AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured  
[Git Installed](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)  
[AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) (AWS SAM) installed  

## Deployment Instructions
Create a new directory, navigate to that directory in a terminal and clone the GitHub repository:  
    
    git clone https://github.com/sshekghub/fair-play-guardian.git

Change directory to the solution directory:  
    
    cd fair-play-guardian

From the command line, use AWS SAM to build and deploy the AWS resources as specified in the template.yml file.  

    sam build
    sam deploy --guided

**During the prompts:**  

**Stack Name:** {Enter your preferred stack name}  
**AWS Region:** {Enter your preferred region}  
**Parameter PrimaryBucketName:** {Enter the bucket name which will store the original profile pictures}  
**Parameter ProcessingBucketName:** {Enter the bucket name which will be used to store the processed images with text temporarily}  
**Parameter Email:** {Enter the email address for notifications pertaining to collusion detection}  
**Confirm changes before deploy:** Y  
**Allow SAM CLI IAM role creation:** Y  
**Disable rollback:** N  
**Save arguments to configuration file:** Y  
**SAM configuration file:** {Press enter to use default name}  
**SAM configuration environment:** {Press enter to use default name}  

## Testing

**Sample Pictures:**
- Few sample pictures are available in the "sample-profile-pictures" directory within this repository.
- You can use these samples or provide your own image files for testing purposes.

**Image Upload:**
- Upload the selected image(s) to the S3 Primary bucket, which was specified during deployment.

**Lambda Function:**
- The Lambda function is triggered by an S3 PUT event when a new profile picture is uploaded to the designated S3 bucket.
- The processed image with blurred text is stored back in the primary S3 bucket.

**Verification Steps:**
- Wait for a few seconds for the image with blurred text to be generated in the primary bucket.
- Download the processed image and verify whether all text elements in the image have been appropriately blurred.

**SNS Notifications:**
- An SNS topic is configured to send notifications.
- Notifications are sent to the email address specified during deployment.
- Confirm the SNS subscription to receive notifications.
- Verify that you receive an email with the appropriate details regarding the processed image and text blurring.      

## Cleanup
First delete/empty the objects in the S3 bucket.   

Then run the command  
    
    sam delete


[def]: FPG-Architecture.png
