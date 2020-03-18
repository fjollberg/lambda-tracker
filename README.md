# lambda-tracker

Rewriting a simple tracker assignment as an AWS lambda solution for fun.

## About

This started as a simple assignment.

## Building lambda installation package

The lambda function requires a couple of supporting libraries for database
access. In particular the pymysql driver, but also the sqlalchemy orm
package, because I started out with that in the original assignment and
can't be bothered to refactorize out of the sqlalchemy dependency.

You need an environment with bash, Python >= 3.7 and corresponding pip.

Build with:

```bash
./build.sh
```

It installs the dependencies into a folder and zips the contents together with
track.py into a package to be deployed into AWS.

## AWS

I won't get into the details of setting up AWS, but you need an RDS mysql
instance, an application load balancer, the lambda function and all the
network topology and securit groups etc to hook these up to each other
and the internet.

### Configuration of the lambda function

The lambda function takes one environment variable for the sqlalchemy database
connection string. It should look something along the lines of this:

```bash
    LAMBDA_TRACKER_DB='mysql+pymysql://username:password@rds_dns_target_name/database'
```

## Some resources

<https://docs.aws.amazon.com/lambda/latest/dg/services-rds-tutorial.html>

<https://docs.aws.amazon.com/lambda/latest/dg/services-alb.html>
