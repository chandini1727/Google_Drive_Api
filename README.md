## Google Drive and Sheets Automation Tool

This project is a Python-based tool that automates the management of Google Drive folders, Google Sheets, and their tabs. It allows users to create, list, and delete folders and sheets, upload files, share resources, and append data to spreadsheets via a command-line interface, leveraging the Google Drive and Sheets APIs.

## Features

-Create and manage Google Drive folders.
-Create Google Sheets within specified folders.
-Add or append data to specific tabs in Google Sheets.
-List all folders, sheets in a folder, or tabs in a sheet.
-Delete folders or sheets by name.
-Upload single or multiple local files to a specified Drive folder.
-Share files or folders with a specified email address.
-Error handling for robust API interactions.

## Prerequisites

-Python 3.6 or higher
-A Google Cloud Platform (GCP) project with Google Drive and Sheets APIs enabled
-A service account with appropriate permissions
-A JSON key file for the service account (service_account.json)

## Setup
**Install Dependencies**
Install the required Python packages using pip:
``` bash
   pip install google-api-python-client google-auth-oauthlib google-auth
