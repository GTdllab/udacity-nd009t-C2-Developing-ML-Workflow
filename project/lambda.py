### first lambda function is responsible for data generation
# c2projectlambda1
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']## TODO: fill in
    bucket = event['s3_bucket']## TODO: fill in
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key, "/tmp/image.png")

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }
###The second one is responsible for image classification
# c2projectlambda2
import json
import base64
import boto3

runtime = boto3.client('sagemaker-runtime')
# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2025-05-27-09-31-58-702" 

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']['image_data']) 

    # Instantiate a Predictor
    predictor = runtime.invoke_endpoint(EndpointName=ENDPOINT,Body=image,ContentType='image/png') 


    # Make a prediction:
    inferences = predictor['Body'].read().decode('utf-8')

    # We return the data back to the Step Function    
    event['inferences'] = json.loads(inferences)

    return {
        'statusCode': 200,
         'body': {
            "image_data": event['body']['image_data'],
            "s3_bucket": event['body']['s3_bucket'],
            "s3_key": event['body']['s3_key'],
            "inferences": event['inferences'],
       }
    }

###The third one is to filter low-confidence inferences
# c2projectlambda3
import json

THRESHOLD = .93

def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event['body']['inferences'] ## TODO: fill in

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(inferences)>THRESHOLD ## TODO: fill in

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': {
            "image_data": event['body']['image_data'],
            "s3_bucket": event['body']['s3_bucket'],
            "s3_key": event['body']['s3_key'],
            "inferences": event['body']['inferences'],
       }
    }