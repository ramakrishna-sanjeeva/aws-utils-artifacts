# Leveraging Amazon Managed Service for Prometheus and Amazon Managed Grafana for monitoring BigBlueButton (https://github.com/bigbluebutton/bigbluebutton) 

Documents configuration for setting up monitoring of BigBlueButton deployment (https://github.com/aws-samples/aws-scalable-big-blue-button-example) using AMP and AMG. 

The monitoring and observability stack for BBB is documented at [BigBlueButton Exporter (greenstatic.dev)](https://bigbluebutton-exporter.greenstatic.dev/) . The project leverages Docker based deployment of Prometheus and Grafana and provides configuration files @ [bigbluebutton-exporter/extras/all_in_one_monitoring at master · greenstatic/bigbluebutton-exporter (github.com)](https://github.com/greenstatic/bigbluebutton-exporter/tree/master/extras/all_in_one_monitoring) . 

This repository documents the configuration for using AMP and AMG. Steps are documented below. 

1. Provision a workspace in Amazon Managed Service for Prometheus. Note down the Endpoint - remote write URL.
2. Provision a workspace in Amazon Managed Grafana.
3. Update the file bbb_exporter_secrets.env with the API_BASE_URL and API_SECRET by executing the command "bbb-conf --secret"
4. Update the docker-compose.yaml removing reference to Grafana container
5. Update the prometheus.yml adding remote write configuration (Provided below). 
--------

    remote_write:
    - url: https://aps-workspaces.<AWS-REGION>.amazonaws.com/workspaces/<WORKSPACE-ID>/api/v1/remote_write 
	    queue_config: 
		    max_samples_per_send: 1000 
		    max_shards: 200 
		    capacity: 2500 
		    sigv4: region: <AWS-REGION>

Reference configuration is available in bbb-exporter folder. 

