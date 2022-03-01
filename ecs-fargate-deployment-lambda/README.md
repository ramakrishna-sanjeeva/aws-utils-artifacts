# Lambda for deploying updated container image to ECS Service 

Deployment of updated image to ECS Service entails the following steps. 
1. Push the image to ECR with the updated image tag 
2. Create a new version of ECS task definition with the updated image tag
3. Update the ECS Service definition with the updated ECS task definition and initiate depoyment. 

To automate the deployment, this solution leverages a Lambda which performs the steps 2 and 3. The Lambda would be invoked with a JSON payload which specifies the image tag to the updated post pushing the image to the ECR. 
Sample Payload: 20220217 is the image tag being updated to. 

    {
      "imageTag": "20220217"
    }

Lambda will be associated with the role which grants the permission to perform the listing of ECR image versions for validation, listing and updated ECS Task definition and ECS service.

Steps for deploying the IAM role and Lambda. 

1. Update the following placeholder variables in the JSON files in the deploy folder. 
>     aws-region
>     aws-account-id
>     ecs-task-execution-role-name
>     ecs-repository-name
>     ecs-cluster-name
>     ecs-service-name
>     ecs-task-definition-name

2. Create a IAM role with the Lambda execution trust policy.

> aws iam create-role --role-name \<lambda-name> --assume-role-policy-document file://lambda-trust-policy.json

3. Associate a role policy which grants access to the ECR and ECS. 

> aws iam put-role-policy --role-name \<role-name> --policy-name \<role-policy-name> --policy-document file://lambda-inline-policy.json

4. Associate the inbuilt policy for basic Lambda execution access. 

> aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole --role-name \<role-name>

5. Zip the Python file for deployment.

> zip ecs-service-deployment-update-lambda.zip ecs-service-deployment-update-lambda.py

6. Create a Lambda function for deployment.

> aws lambda create-function \
> --function-name m-ticket-stat-ecs-deployment-dev \
> --runtime python3.9 \
> --timeout 1
> --role arn:aws:iam::\<aws-account-id>:role/\<role-name>
> --environment environment.json

