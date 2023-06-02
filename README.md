# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource | Service Tier | Monthly Cost |

| ------------ | ------------ | ------------ |

| *Azure Postgres Database* |   General Purpose - D4ds5, 4 vCore     $259.88/Month    |

| *Azure Service Bus*   |   Standard      |      $9.81/Million/Month  |

| *Azure Function*   |    Consumption (Serverless)     |    $1.80/Million Execution/Month        |

| *Azure Storage Account*   |      Premium - Hot   |         $150.90/Month    |

| *Azure App Service*   |    Premium V2 2Core(s), 7 GB RAM, 250 GB Storage     |    $168.63/Month         |

Explanation and reasoning for my architecture selection:
### Azure Web App:

Drawbacks:

    - Long-running operations: If my web application performs time-consuming tasks, such as large file uploads, extensive database operations, or external API calls, it may exceed the default timeout duration (Azure Web App has timeout of 230 seconds for incoming requests)

    - Resource limitations: If my web application performs time-consuming tasks, such as large file uploads, extensive database operations, or external API calls, it may exceed the default timeout duration

    - Network issues: Timeout errors can also arise due to network connectivity problems. If there are network disruptions or delays between the client, Azure Web App, and any external dependencies, the request may exceed the timeout threshold.

### Azure Function:

Advantanges:

    - Reliable message delivery: Service Bus Queue provides reliable message delivery. Once a message is sent to the queue, it is stored safely until it is successfully processed by a receiver. This ensures that mail sending requests are not lost or discarded, even if there are temporary failures or downtime in the web app or the mail sending service.

    - Scalability and load balancing: The decoupling provided by the Service Bus Queue allows for horizontal scaling of the web app. Multiple instances of the web app can send messages to the queue concurrently, and the messages will be distributed across the available receivers. This enables efficient load balancing and helps handle increased message traffic or sudden bursts in demand.

    - Asynchronous processing: By utilizing a Service Bus Queue, the web app can offload the time-consuming task of sending emails to a separate component or service. This asynchronous processing frees up resources in the web app, allowing it to handle more requests and respond faster to user interactions.

Drawbacks:

    - Execution time limits: Azure Functions have execution time limits depending on the hosting plan and runtime version. If your function takes longer to execute than the allowed time, it can result in an HTTP timeout error. For example, the default execution timeout for consumption plan functions is 5 minutes.

    - Resource constraints: Functions hosted on lower-tier plans or with limited allocated resources may struggle to handle longer or resource-intensive operations within the specified timeout duration. Upgrading to a higher-tier plan or adjusting resource allocations can help address this issue.

    - External dependencies: If your function relies on external services, such as databases, APIs, or other services, delays or network connectivity issues with those dependencies can lead to timeout errors. Ensure that your function handles such scenarios gracefully and has appropriate error handling mechanisms.

-> In summary, Azure Web App is suitable for hosting web applications but may face issues with long-running operations and potential timeout errors. Azure Function offers advantages such as reliable message delivery, scalability, and asynchronous processing. However, it has execution time limits and resource constraints. Consider your specific application requirements to choose the most appropriate option.