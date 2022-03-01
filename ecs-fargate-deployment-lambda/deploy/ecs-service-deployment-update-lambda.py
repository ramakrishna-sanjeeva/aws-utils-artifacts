import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    repository_name = os.environ['ECR_REPOSITORY_NAME']
    task_definition_name = os.environ['ECS_TASK_DEFINITION_NAME']
    ecs_cluster_name = os.environ['ECS_CLUSTER_NAME']
    ecs_service_name = os.environ['ECS_SERVICE_NAME']
    image_tag = event['imageTag']

    logger.info("\nRepository name: " + repository_name +
                "\nECS Task Definition name: " + task_definition_name +
                "\nECS Service name: " + ecs_service_name +
                "\nECS Cluster: " + ecs_cluster_name +
                "\nImage Tag: " + image_tag)

    valid = True
    if not (repository_name and not repository_name.isspace() and \
            task_definition_name and not task_definition_name.isspace() and \
            ecs_cluster_name and not ecs_cluster_name.isspace() and \
            ecs_service_name and not ecs_service_name.isspace() and \
            image_tag and not image_tag.isspace()):
        valid = False

    try:
        # Check if the Image exists
        if valid:
            ecr_client = boto3.client('ecr')
            describe_images_response = ecr_client.describe_images(
                repositoryName=repository_name,
                imageIds=[{'imageTag': image_tag}],
                filter={
                    'tagStatus': 'TAGGED'}
            )
            logger.info(describe_images_response)
            if len(describe_images_response['imageDetails']) != 1:
                valid = False

        ecs_client = boto3.client('ecs')

        # Check if Cluster, Service and Task Definition are valid
        if valid:
            logger.info("Validating the existing ECS service")
            describe_services_response = ecs_client.describe_services(
                cluster=ecs_cluster_name,
                services=[ecs_service_name]
            )
            if len(describe_services_response['services']) != 1:
                valid = False
            if valid:
                if describe_services_response['services'][0]['serviceName'] != ecs_service_name:
                    valid = False
                task_definition = describe_services_response['services'][0]['taskDefinition']
                task_definition_name_in_service = (task_definition.rsplit(':', 1)[0]).split('/', 1)[1]
                if task_definition_name_in_service != task_definition_name:
                    valid = False

        if not valid:
            logger.error("Validation failed")
            return {
                'statusCode': 400,
                'body': json.dumps("Configured Cluster,Service,Task Definition or Image name is invalid or such ECS "
                                   "service not exist exist")
            }

        # Get latest task definition
        logger.info("Getting the existing task definition")
        task_definition_response = ecs_client.describe_task_definition(
            taskDefinition=task_definition_name
        )
        logger.info("Task Definition: " + str(task_definition_response))

        container_definitions = task_definition_response['taskDefinition']['containerDefinitions']
        container_image_arn = container_definitions[0]['image'].split(':')[0]
        updated_container_image = container_image_arn + ":" + image_tag
        container_definitions[0]['image'] = updated_container_image

        logger.info("Updated Image to: " + updated_container_image)

        # Create updated task definition
        logger.info("Registering the updated task definition")
        task_definition_response = ecs_client.register_task_definition(
            family=task_definition_response['taskDefinition']['family'],
            taskRoleArn=task_definition_response['taskDefinition']['taskRoleArn'],
            executionRoleArn=task_definition_response['taskDefinition']['executionRoleArn'],
            networkMode=task_definition_response['taskDefinition']['networkMode'],
            containerDefinitions=container_definitions,
            requiresCompatibilities=task_definition_response['taskDefinition']['requiresCompatibilities'],
            cpu=task_definition_response['taskDefinition']['cpu'],
            memory=task_definition_response['taskDefinition']['memory']
        )
        logger.info("Task Definition Update response: " + str(task_definition_response))

        updated_task_definition_arn = task_definition_response['taskDefinition']['taskDefinitionArn']

        # Update ECS Service
        logger.info("Updating the ECS Service to deploy updated task definition")
        update_service_response = ecs_client.update_service(
            cluster=ecs_cluster_name,
            service=ecs_service_name,
            taskDefinition=updated_task_definition_arn)
        logger.info("ECS Service Update response: " + str(update_service_response))

        return {
            'statusCode': 200,
            'body': {
                "task_definition_arn": updated_task_definition_arn,
                "deployment_id": update_service_response['service']['deployments'][0]['id']
            }
        }
    except Exception as error:
        logger.error("Error in execution")
        logger.error(str(error))
        return {
            'statusCode': 500,
            'body': {
                "error": str(error)
            }
        }
