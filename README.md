Lambda script that enriches snowplow event data and puts it back to S3

Python based function for AWS lambda.

Function parses cloudfrront logs which requested by Snowplow pixel tracker.

Lambda should triggers on any object creation for bucket with cloudfront logs. Logfiles must be in RAW folder.

Enriched and processed logs puts in same bucket within Converted folder.

For more detailed description check our blog post at https://www.ownyourbusinessdata.net/enrich-snowplow-data-with-aws-lambda-function/
