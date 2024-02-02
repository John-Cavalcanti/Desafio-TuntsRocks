import os.path
from math import ceil

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sheets_url = "1Pu8mgHPVEqmpP62-QAjbbad5xthI3raknWR5FNDqCJc"
total_classes_number = 60
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = sheets_url
SAMPLE_RANGE_NAME = "engenharia_de_software!A1:H27"

def define_students_situation(sheets_arr):
    
    # only students array purpose is to get only the info of
    # the students from the sheet, since i do not want the titles
    only_students_array = []
    students_situation = []
    
    # logic for getting only the student infos(id, name, absences and grades)
    for i, student_info in enumerate(sheets_arr):
        if i > 2:
            only_students_array.append(student_info)
    
    # logic for defining the situation of all students
    # variable names are self-explanatory
    for student in only_students_array:
        student_absence_percentage = float(student[2])/total_classes_number
        
        if(student_absence_percentage > 0.25):
            students_situation.append(['Reprovado por falta',0])
        else:
            student_average_grade = (float(student[3]) + float(student[4]) + float(student[5])) / 3
            
            if(student_average_grade < 50):
                students_situation.append(['Reprovado por nota',0])
            elif(student_average_grade < 70):
                # naf = nota para aprovação final
                naf = ceil(100 - student_average_grade)
                students_situation.append(['Exame final',naf])
            else:
                students_situation.append(['Aprovado',0])
                
    
    return students_situation


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "./ChaveJson/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        standard_values = result.get("values", [])

        if not standard_values:
            print("No data found.")
            return

        students_situation = define_students_situation(standard_values)
        
        result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,range="G4",
                                        valueInputOption="USER_ENTERED",body={'values':students_situation}).execute()

    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()

