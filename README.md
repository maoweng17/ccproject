# ccproject
QMUL cloud computing mini project


## **Overall Description**
1. It's a REST-based service interface.
2. Use external REST service to retrieve data from Zomato API.
3. Use Cassandra database for accessing persistent information: user information (username and hashed password) and rating information.
4. Implemented cloud security measures including: hash-based authentication, user accounts and access management.




## **Run API, command line:**
If you want to run it on Google cloud platform,
you can execute the following command.
After this, you will have the external IP
```
gcloud config set compute/zone europe-west2-b
export PROJECT_ID=“$(gcloud config get-value project -q)”

# 3 node clusters
gcloud container clusters create cassandra —num-nodes=3 --machine-type "n1-standard-2"

kubectl create -f cassandra-peer-service.yml
kubectl create -f cassandra-service.yml
kubectl create -f cassandra-replication-controller.yml

kubectl get pods -l name=cassandra
# scale up our number of nodes
kubectl scale rc cassandra --replicas=3

kubectl exec -it cassandra-96b5t -- nodetool status
# kubectl exec -it cassandra-2nlrk cqlsh

docker build -t gcr.io/${PROJECT_ID}/irene:v1 .
docker push gcr.io/${PROJECT_ID}/irene:v1

kubectl run irene --image=gcr.io/${PROJECT_ID}/irene:v1 --port 8080
kubectl expose deployment irene --type=LoadBalancer --port 80 --target-port 8080

kubectl get services

kubectl describe pod irene3-654cdbf8-cgwmv
kubectl get services
```

If you want to run it on local machine, you can directly execure this command.
It will trigger main.py file and start the API
```
python main.py
```



## **Status Description:**
Log in and log out actions will affect which page user can access
![alt text](/description.png)
  
