# OpenShift-rotate-certs
Rotate OpenShift certificates on demand.

The cluster certificates renewals should not be percived by any user workload. There is a reason all control place components are in triplicate. However, if more control is needed, then this is a tool for you.


# How to use

1. git clone the code
2. cd into folder
3. Build the container:

~~~
$ buildah build -t <YOUR_REGISTRY>/rotate-certs:latest . 
~~~

4. Push the container image to your registry:

~~~
$ podman push <YOUR_REGISTRY>/rotate-certs:latest --authfile /path/registry/credentials.json
~~~

5. Create the Kube object to support the application as a cluster-admin:

~~~
$ oc create -f create-infra.yaml
~~~

This will create a namespace, a service account for the app, and will add the service account to the Cluster Role "cluster-admin".

6. Choose your preferred method for deployment: pod, job, or cronjob.

7. Configure the variables in the YAML file:

  - API_SERVER          : The cluster public API endpoint.
  - TLS_SECRETS         : The list os secret in the format "ns/secret" seperated by commas.
  - VALIDITY_THRESHHOLD : Set this value according to the peridiocity of the execution. A 30 days certificate will renew after 15 days. If you run this application every week, then a value of "40" should force the manual rotation before the cluster auto-renewal.

8. Deploy the application with:

~~~
$ oc -n rotate-certs create -f cronjob.yaml
~~~

Enjoy.
