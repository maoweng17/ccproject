export PROJECT_ID="$(gcloud config get-value project -q)"

gcloud container clusters create cassandra --num-nodes=3 --machine-type "n1-standard-2"

kubectl create -f cassandra-peer-service.yml
kubectl create -f cassandra-service.yml
kubectl create -f cassandra-replication-controller.yml

kubectl get pods -l name=cassandra
kubectl scale rc cassandra --replicas=3

export CASSANDRA_ID="$(kubectl get pods -l name=cassandra --field-selector=status.phase=Running  -o go-template  --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'| head -n 1)"

kubectl exec -it ${CASSANDRA_ID} -- nodetool status

docker build -t gcr.io/${PROJECT_ID}/irene:v1 .
docker push gcr.io/${PROJECT_ID}/irene:v1

kubectl run service_name --image=gcr.io/${PROJECT_ID}/irene:v1 --port 8080
kubectl expose deployment service_name --type=LoadBalancer --port 80 --target-port 8080
