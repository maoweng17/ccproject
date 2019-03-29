# ccproject
QMUL cloud computing mini project


## **Overall Description**
1. It's a REST-based service interface.
2. Use external REST service to retrieve data from Zomato API.
3. Use Cassandra database for accessing persistent information: user information (username and hashed password) and rating information.
4. Implemented cloud security measures including: hash-based authentication, user accounts and access management.




## **Run API, command line:**
If you want to run it on Google cloud platform, you can execute the following command.
After this, you will have the external IP
```
sh cmd_all.sh
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
  
