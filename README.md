# infra-sec-validations
This project contains Python scripts that ensure some security good practices in AWS.

# Instructions
Install the required dependencies using `pip install -r requirements.txt`. Then run `python3 infra_sec/s3_sec.py`.

# Notes
* Be aware of having your AWS Account credentials or profile configured, environment variables is an option.
* This can be a lambda running on a daily basis
* An SNS topic would be useful to notify about the risks