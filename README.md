Lambda script that enriches snowplow event data and puts it back to S3

Python based function for AWS lambda.

Function parses cloudfrront logs which requested by Snowplow pixel tracker.

Lambda should triggers on any object creation for bucket with cloudfront logs. Logfiles must be in RAW folder.

Enriched and processed logs puts in same bucket within Converted folder.

For more detailed description check our blog post at https://www.ownyourbusinessdata.net/enrich-snowplow-data-with-aws-lambda-function/

# Requirenments

* Terraform 0.12
* AWS user should have following recomended permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "iam:GetPolicyVersion",
                "glue:DeleteDatabase",
                "iam:DeletePolicy",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "athena:*",
                "iam:ListInstanceProfilesForRole",
                "cloudfront:GetDistribution",
                "iam:PassRole",
                "iam:DetachRolePolicy",
                "iam:ListAttachedRolePolicies",
                "cloudfront:UpdateDistribution",
                "iam:GetRole",
                "iam:GetPolicy",
                "glue:GetTables",
                "s3:*",
                "cloudfront:TagResource",
                "iam:DeleteRole",
                "cloudfront:CreateDistribution",
                "glue:GetDatabases",
                "iam:CreatePolicy",
                "glue:GetDatabase",
                "iam:ListPolicyVersions",
                "cloudfront:ListTagsForResource",
                "glue:CreateDatabase",
                "lambda:*",
                "cloudfront:DeleteDistribution"
            ],
            "Resource": "*"
        }
    ]
}
```

# Configuring terraform script

File ```variables.tf``` contains all configurable variables for script:

* __env__ - Service tag. May be used as billing reports tag.
* __creator__ - Personalization tag.
* __website__ - Website FQDN for plowing.
* __access_key__ - AWS user access key.
* __primary_domain__ - Cloudfront distribution CNAME.
* __secret_key__ - AWS user secret key.
* __region__ - AWS region.

# Deploying infrastructure

Inside repo directory run:

```bash
terraform init
terraform apply
```
