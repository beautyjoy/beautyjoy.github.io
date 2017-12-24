# BJC Utilities

These are utilities used in the website, but are a part of other services.

## Contact Form

Based off:
https://codehabitude.com/2016/04/05/forms-to-emails-using-aws-lambda-api-gateway/

We use AWS Lambda to build an email, and AWS SES to send it.
The form on /contact makes a POST request to an API that triggers the lambda function.
