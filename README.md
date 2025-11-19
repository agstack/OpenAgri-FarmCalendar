# OpenAgri Digital Farm Calendar
🇪🇺
*"This service was created in the context of OpenAgri project (https://horizon-openagri.eu/). OpenAgri has received funding from the EU’s Horizon Europe research and innovation programme under Grant Agreement no. 101134083."*


A Web User Interface (UI) is provided which allows the users the visualize and navigate through the farm calendar of activities and to facilitate the management of the farm assets.
Moreover, all these operations and farm assets can be managed through a REST API, which provides these resources in a linked data format (i.e., using JSON-LD) and conforms to the OpenAgri Common Semantic Model (OCSM).


## Prerequisites

Before you start, make sure Docker and Docker Compose are installed on your system.
Later versions of Docker also include now Docker Compose, but it is used as `docker compose` instead of `docker-compose`.

## Service Setup

### Setting up Configurations (.env file)
If you wish to start up this Farm Calendar service from this repository, you'll need to first copy the `.env.sample` file into a new file called `.env`, which will be the source of all configurations for this service, and its database.

In this new `.env` file you should change the configurations of the service to meet your deployment scenario. We strongly suggest changing configurations for the default usernames and passwords of the services used.

The details for the configuration variables that are not self-explanatory are:
* **GATEKEEPER_LOGIN_URL**: This should be set to the OpenAgri Gatekeeper login endpoint if you wish to use this as the authentication method. Alternativelly, not setting this variable will fall-back to a local session based user authentication on this FarmCalendar service.
* **JWT_SIGNING_KEY**: If using the Gatekeeper for authentication, this should be set to the JWT signing key used by the Gatekeeper.
* **JWT_COOKIE_NAME**: Name of the auth cookie that will carry the JWT token (when using the Web User Interface). Eg: OpenAgriAuth. For the REST API endpoints, the JWT token is expected to be passed in the request header instead.
* **AUTO_CREATE_AUTH_USER**: True or False, if the FarmCalendar service should automatically create a user if it receives a request with an authenticated user token that does not exist in its local database. If set to false, it will not authenticate the non-existing local using, if its set to true (default) it will create the user and successfully authenticate it.

## Running
There is already a simple and ready to use `docker-compose.yml` file for your convinience. Nonetheless, you should be able to use the existing file as a base, and adapt it to your own deployment setup.

To run the service, execute the following command:
```
$ docker compose up -d
```

## Stopping/Restarting

To stop the service related containers, run:

```commandline
docker compose stop
```
And to start again the stopped containers:

```commandline
docker compose start
```

To stop and remove the containers, use:

```commandline
docker-compose down
```

## Local Admin User (No Gatekeeper)
If you are not using the OpenAgri Gatekeeper service to provide authentication and user management, then you should remove the `GATEKEEPER_LOGIN_URL` configuration from your `.env` file. This will make your Farm Calendar service work with its own internal user authentication (using Django's auth and password process).

In this case, you need to first run the following for initial setup:
```
$ docker compose run --rm web python3 manage.py initial_setup
```

And then you can create your admin user by running:
```
$ docker compose run --rm web python3 manage.py createsuperuser
```
this will present you with inputs that will guide your creation of your admin user.


### Accessing your local Farm Calendar

After starting the services, the Farm Calendar Web UI will be available at: [http://localhost:8002/](http://localhost:8002/)

Meanwhile, the REST API root is available at: [http://localhost:8002/api/v1/](http://localhost:8002/api/v1/)

Both the Web UI and REST API are only available after login in in the OpenAgri Gatekeeper, or if no Gatekeeper is bying used, then username and password of the local admin user sould be used.

# API Docs
## Overview
An overview of the endpoints provided by the FarmCalendar API can be seen at the [API.md](/API.md) file.
## Swagger Live Docs
Use the [Online Swagger Editor](https://editor-next.swagger.io/?url=https://raw.githubusercontent.com/agstack/OpenAgri-FarmCalendar/refs/heads/main/schema.yml) to visualise the current API specification and documentation.



# License
This project code is licensed under the EUPL 1.2 license, see the LICENSE file for more details.
Please note that each service may have different licenses, which can be found their specific source code repository.
