import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
USER_EMAIL = "322103310047@gvpce.ac.in"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)
sheets_service = build('sheets', 'v4', credentials=credentials)

def get_or_create_folder(folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])
    if files:
        print(f"Folder '{folder_name}' already exists.")
        return files[0]['id']
    else:
        metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        folder = drive_service.files().create(body=metadata, fields='id').execute()
        share_with_user(folder['id'], USER_EMAIL)
        print(f"Folder '{folder_name}' created.")
        return folder['id']

def share_with_user(file_id, user_email):
    permission = {'type': 'user', 'role': 'writer', 'emailAddress': user_email}
    drive_service.permissions().create(fileId=file_id, body=permission, sendNotificationEmail=False).execute()

def get_or_create_sheet(sheet_name, parent_folder_id):
    query = f"name='{sheet_name}' and mimeType='application/vnd.google-apps.spreadsheet' and '{parent_folder_id}' in parents and trashed=false"
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])
    if files:
        print(f"Sheet '{sheet_name}' already exists. Returning to main menu.")
        return None
    else:
        metadata = {'name': sheet_name, 'mimeType': 'application/vnd.google-apps.spreadsheet', 'parents': [parent_folder_id]}
        sheet = drive_service.files().create(body=metadata, fields='id').execute()
        print(f"Sheet '{sheet_name}' created.")
        return sheet['id']

def sheet_tab_exists(sheet_id, tab_name):
    sheet = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    for s in sheet['sheets']:
        if s['properties']['title'] == tab_name:
            return True
    return False

def add_or_append_tab(sheet_id, tab_name, data):
    if not sheet_tab_exists(sheet_id, tab_name):
        request = {'requests': [{'addSheet': {'properties': {'title': tab_name}}}]}
        sheets_service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body=request).execute()
        print(f"Tab '{tab_name}' created.")
        range_name = f"{tab_name}!A1"
    else:
        print(f"Tab '{tab_name}' already exists. Appending data.")
        result = sheets_service.spreadsheets().values().get(spreadsheetId=sheet_id, range=f"{tab_name}!A:A").execute()
        existing_rows = len(result.get('values', []))
        range_name = f"{tab_name}!A{existing_rows + 1}"
    body = {'values': data}
    sheets_service.spreadsheets().values().update(spreadsheetId=sheet_id, range=range_name, valueInputOption="RAW", body=body).execute()

def list_folders():
    query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = response.get('files', [])
    print("FOLDERS:")
    for folder in folders:
        print(f"- {folder['name']} (ID: {folder['id']})")

def list_sheets_in_folder(folder_name):
    folder_id = get_or_create_folder(folder_name)
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    sheets = response.get('files', [])
    print(f"SHEETS in folder '{folder_name}':")
    for sheet in sheets:
        print(f"- {sheet['name']} (ID: {sheet['id']})")

def list_tabs_in_sheet(folder_name, sheet_name):
    folder_id = get_or_create_folder(folder_name)
    sheet_id = get_or_create_sheet(sheet_name, folder_id)
    if sheet_id is None:
        return
    sheet = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    print(f"TABS in sheet '{sheet_name}':")
    for s in sheet['sheets']:
        print(f"- {s['properties']['title']}")

def delete_file_by_name(name):
    query = f"name='{name}' and trashed=false"
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])
    if files:
        file_id = files[0]['id']
        drive_service.files().delete(fileId=file_id).execute()
        print(f"Deleted file '{name}' (ID: {file_id})")
    else:
        print(f"No file found with name '{name}'")

def upload_local_file_to_drive(local_path, folder_name):
    local_path = local_path.strip('"')
    if not os.path.exists(local_path):
        print(f"Local file '{local_path}' does not exist.")
        return
    folder_id = get_or_create_folder(folder_name)
    file_name = os.path.basename(local_path)
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload(local_path, resumable=True)
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded '{file_name}' to folder '{folder_name}'.")

def upload_multiple_files(file_paths, folder_name):
    for path in file_paths:
        upload_local_file_to_drive(path.strip(), folder_name)

def share_file_or_folder_by_name(name, email):
    query = f"name='{name}' and trashed=false"
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = response.get('files', [])
    if not files:
        print(f"No file or folder found with name '{name}'.")
        return
    file_id = files[0]['id']
    share_with_user(file_id, email)
    print(f"Shared '{name}' with '{email}' successfully.")

if __name__ == "__main__":
    try:
        while True:
            print("\nMENU:")
            print("1. Create Folder")
            print("2. Create Sheet in a Folder")
            print("3. Add Tab with Data to a Sheet")
            print("4. List all Folders")
            print("5. List all Sheets in a Folder")
            print("6. List all Tabs in a Sheet")
            print("7. Delete a Folder / Sheet")
            print("8. Upload a Local File to a Folder on Drive")
            print("9. Upload Multiple Local Files")
            print("10. Share a File or Folder with Email ID")
            print("0. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                folder_name = input("Enter folder name: ")
                get_or_create_folder(folder_name)

            elif choice == "2":
                folder_name = input("Enter folder name: ")
                folder_id = get_or_create_folder(folder_name)
                sheet_name = input("Enter sheet name: ")
                get_or_create_sheet(sheet_name, folder_id)

            elif choice == "3":
                folder_name = input("Enter folder name: ")
                folder_id = get_or_create_folder(folder_name)
                sheet_name = input("Enter sheet name: ")
                sheet_id = get_or_create_sheet(sheet_name, folder_id)
                if sheet_id:
                    tab_name = input("Enter tab name: ")
                    rows = int(input("How many rows? "))
                    cols = int(input("How many columns per row? "))
                    data = []
                    for i in range(rows):
                        while True:
                            row = input(f"Row {i+1} (comma-separated): ").split(",")
                            if len(row) == cols:
                                data.append([cell.strip() for cell in row])
                                break
                            else:
                                print(f"Expected {cols} columns.")
                    add_or_append_tab(sheet_id, tab_name, data)

            elif choice == "4":
                list_folders()

            elif choice == "5":
                folder_name = input("Enter folder name: ")
                list_sheets_in_folder(folder_name)

            elif choice == "6":
                folder_name = input("Enter folder name: ")
                sheet_name = input("Enter sheet name: ")
                list_tabs_in_sheet(folder_name, sheet_name)

            elif choice == "7":
                name = input("Enter file/folder name to delete: ")
                delete_file_by_name(name)

            elif choice == "8":
                file_path = input("Enter full local file path: ")
                folder_name = input("Enter destination folder name on Drive: ")
                upload_local_file_to_drive(file_path, folder_name)

            elif choice == "9":
                files = input("Enter file paths separated by commas: ").split(",")
                folder_name = input("Enter destination folder name on Drive: ")
                upload_multiple_files(files, folder_name)

            elif choice == "10":
                name = input("Enter file or folder name to share: ")
                email = input("Enter email ID to share with: ")
                share_file_or_folder_by_name(name, email)

            elif choice == "0":
                print("Exiting.")
                break

            else:
                print("Invalid choice. Try again.")

    except HttpError as error:
        print(f"An error occurred: {error}")
