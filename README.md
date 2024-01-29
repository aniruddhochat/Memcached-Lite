**Introduction.**
The project deals with designing, developing, and implementing a robust Key-Value Store and deploying the same in Google Cloud Platform (GCP). A Memcached Client-Server based architecture has been chosen to start with the designing part. TCP-socket server which listens to a host and port is used to start the server and consecutively connect to the clients. Three different types of storage system (VM Boot Disk, GCS Bucket, Redis Memory Store) have been used to save the data instead of the traditional Memcached server which store the data in memory and data is wiped off once the server is either restarted or shut down. “get” and “set” instructions have been used to either get the data from the Memcached server, insert, or update a new value. Concurrent connection of multiple clients connecting to a single server and performing the instructions have been considered.

![System Architecture - Memcached Lite](./GCP-Memcached.png)

**Prerequisites.**
•	Install Google SDK in your local machine to access Google Cloud Platform.
•	A Google Cloud account with active credits and projects are required.
•	Clone this Repo
•	Create a Redis Instance on Google Cloud (Included in the VirtualMachineCreation.sh bash script)
•	Create a Bucket and Blob in Google Cloud Storage (Not included in the Bash script since I created it manually and did not get the equivalent CLI command)
•	Mention respective bucket and blob details in the configFile.py

