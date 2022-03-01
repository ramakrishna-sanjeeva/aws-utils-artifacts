# Lambda for deployment of ECS Service 

Deployment of update image to ECS Service entails the following steps. 
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

