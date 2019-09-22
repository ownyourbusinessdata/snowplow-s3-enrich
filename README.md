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

Terraform will create:

* 3 Buckets:
  1. With __lt-src__ suffix. Public accessible for reading. Contains 1x1 pixel image for snowplow GET data.
  2. With __lt-logs__ suffix. Using for storing: cloudfront logs with __RAW__ prefix, enriched snowplow data with __Converted__ prefix and maxmind GeoLite2 database.
  3. With __lt-ath__ suffix. Using for storing Athena query results.

* Cloudfront distribution with __lt-src__ bucket as target and __lt-logs__ bucket for logs storing.

* Lambda function wich triggers on any __lt-logs__ bucket object creation with prefix __RAW__ and suffix __.gz__.

* Athena workgroup with suffix __wg__

* Athena database with prefix __eventsdb__

* Athena saved query with name __events__

To complete infrastructure deployment run created saved athena query in created workgroup, it will create table with enriched snowplow events.

# Configuring snowplow pixel tracker

Snowplow pixel tracker code looks like:

```javascript
<script type="text/javascript">
  ;(function(p,l,o,w,i,n,g){if(!p[i]){p.GlobalSnowplowNamespace=p.GlobalSnowplowNamespace||[];
  p.GlobalSnowplowNamespace.push(i);p[i]=function(){(p[i].q=p[i].q||[]).push(arguments)
  };p[i].q=p[i].q||[];n=l.createElement(o);g=l.getElementsByTagName(o)[0];n.async=1;
  n.src=w;g.parentNode.insertBefore(n,g)}}(window,document,"script","//d1fc8wv8zag5ca.cloudfront.net/2.6.2/sp.js","snowplow"));

  window.snowplow('newTracker', 'cf', 'dolaqvbw76wrx.cloudfront.net', {
    appId: 'site',
    cookieDomain: 'bostata.com',
  });
  window.snowplow('enableActivityTracking', 1, 5);
  window.snowplow('trackPageView');
  window.snowplow('enableLinkClickTracking');
  window.snowplow('enableFormTracking');
</script>
```

You have to change __window.snowplow__ cloudfront domain name to created cloudfront domain name and add code on pages you wanted to track with snowplow.

# How it works

Each time a page is loaded, the browser requests a __sp.js__ script. It's collects data from endpoint device.

All data compiles in GET request. Pixel tracker run that request to cloudfront distribution. Request string logs with cloudfront.

Log file puts into __lt-logs__ bucket. Lambda function start to porocess new data, enrich it according [snowplow event model](https://github.com/snowplow/snowplow/wiki/canonical-event-model) and put enriched data in Converted folder.