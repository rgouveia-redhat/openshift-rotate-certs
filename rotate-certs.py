import os
import time
from datetime import datetime
from kubernetes import client, config


### Authentication ###
configuration = client.Configuration()

## Note that the CA_cert and Token are obtained from the service account
configuration.host = os.environ.get('API_SERVER')
configuration.ssl_ca_cert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
configuration.api_key_prefix['authorization'] = 'Bearer'

with open('/var/run/secrets/kubernetes.io/serviceaccount/token', "r") as token:
    configuration.api_key['authorization'] = token.read()

### Create API access object
v1api = client.CoreV1Api(client.ApiClient(configuration))


### Read secrets to verify ###
secrets = os.environ.get('TLS_SECRETS')


### Process each secret
for cert in secrets.split(","):

    (namespace, secret_name) = cert.split("/")
    print( "\nProcessing: ns=%s / secret=%s" % (namespace, secret_name) )

    ### get the initial and end dates, and determine the number of days
    secret = v1api.read_namespaced_secret(secret_name, namespace)

    init_date = secret.metadata.annotations['auth.openshift.io/certificate-not-before']
    end_date  = secret.metadata.annotations['auth.openshift.io/certificate-not-after']
    print( "Certificate validaty dates: %s - %s" % (init_date, end_date) )

    date_format = "%Y-%m-%dT%H:%M:%SZ"   # 2023-03-09T16:24:45Z
    delta = datetime.strptime(end_date, date_format) - datetime.strptime(init_date, date_format)
    print( "Certificate days range: %s" % (delta.days) )


    ### check if the current date is close to the percentage threshold of the cert validaty
    used_days = datetime.now() - datetime.strptime(init_date, date_format)
    used_percentage = (used_days / delta) * 100
    print( "Certificate used days: %s (%s percentage)" % (used_days, used_percentage) )


    ### if yes, force the renewal of the certificate
    if used_percentage >= float(os.environ.get('VALIDITY_THRESHHOLD')):
        print( "Patching secret %s ..." % (cert) )
        patch = {"metadata": {"annotations": {"auth.openshift.io/certificate-not-after": ""}}}
        res = v1api.patch_namespaced_secret(secret_name, namespace, body=patch)
