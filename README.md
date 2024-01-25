
# SNIPE-IT Import

### Description

This project automates the import and update process of device information into a Snipe-IT asset management system using data from an external API. It is designed to run periodically with a cron job, ensuring that the Snipe-IT system stays up-to-date with the latest device information.
### Table of Contents

* [Installation](#Installation)
* [Usage](#Usage)
* [Configuration](#Configuration)
* [Cron Job](#Cron-Job)
* [Dependencies](#Dependencies)

### <a name="Installation"></a>Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/project-name.git
cd project-name
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```
3. Set up the configuration file:

```bash
cp .env.example .env
```

Update the values in the .env file with your specific configurations.

### <a name="Usage"></a>Usage

Run the main script to start the import and update process:

```bash
python main.py
```
The script will fetch device information from microsft graph api, process the data, and update the Snipe-IT asset management system accordingly.

### <a name="Configuration"></a>Configuration

Configure the application by modifying the .env file. This file contains environment variables necessary for the proper functioning of the script. Update the following variables:

* SNIPE_API_KEY: API key for authenticating with the Snipe-IT API.
* MICROSOFT_CLIENT_ID: Client ID for authenticating with the Microsoft API.
* MICROSOFT_CLIENT_SECRET: Client secret for authenticating with the Microsoft API.
* SNIPE_URL: URL of the Snipe-IT instance.
* SNIPE_API_URL: Snipe-IT API URL.
* MICROSOFT_URL: Microsoft API URL.
* SLACK_URL: Slack webhook URL for sending notifications.
* DEVICE_PREFIX: Prefixes of supported devices, separated by commas.

### <a name="Cron-Job"></a>Cron Job

To set up a cron job for periodic execution, add the following line to your crontab file:

```bash
0 0 * * * /path/to/python /path/to/project-name/main.py
```
This example runs the script every day at midnight. Adjust the timing as needed.

### <a name="Dependencies"></a>Dependencies

    requests: HTTP library for making API requests.
    dotenv: Loads environment variables from a file.