
# AWS Cloud Data Migration & Validation Platform

## Overview
An AWS-based data migration pipeline that ingests synthetic customer and account CSV files, validates records, separates valid and rejected data, and performs SQL-based reconciliation.

The project demonstrates cloud data engineering, ETL, data quality controls, orchestration, and monitoring.

## Architecture
1. Raw CSV files are stored in Amazon S3.
2. AWS Step Functions orchestrates customer and account validation.
3. AWS Lambda runs Python validation logic.
4. Valid and rejected records are written to separate S3 locations.
5. AWS Glue Data Catalog registers curated datasets.
6. Amazon Athena runs SQL queries for reconciliation and analysis.
7. Amazon CloudWatch captures logs and monitors Lambda errors.

## AWS Services
- Amazon S3 — raw, curated, rejected, and query-result storage
- AWS Lambda — serverless data validation
- AWS Step Functions — workflow orchestration
- AWS Glue — data catalog
- Amazon Athena — SQL analytics and reconciliation
- Amazon CloudWatch — logs, metrics, and alarms
- AWS IAM — permissions and access control
- AWS SAM / CloudFormation — infrastructure deployment

## Data Quality Checks
- Required-field and format validation
- Duplicate identifier detection
- Customer-account referential integrity
- Valid/rejected record separation
- SQL-based record-count reconciliation
- Account balance aggregation and analysis

## Current Test Dataset
| Dataset | Source records | Valid records | Rejected records |
|---|---:|---:|---:|
| Customers | 100 | 96 | 4 |
| Accounts | 150 | 138 | 12 |

These counts are based on the synthetic dataset used during development.

## Technologies
Python, SQL, AWS Lambda, Amazon S3, AWS Step Functions, AWS Glue, Amazon Athena, Amazon CloudWatch, AWS SAM, CloudFormation.
