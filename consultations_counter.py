from openpyxl import load_workbook
from flask import Flask, render_template, request, redirect, flash
import os
from werkzeug.utils import secure_filename
import pandas as pd

UPLOAD_FOLDER = './uploads'
ALLOWED_FILE_TYPES = {'xlsx', 'csv'}

app = Flask(__name__)
app.secret_key = "skrivesenteret"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def count_column(column, title):
    """
    Counts all the unique values in a certain column in Excel.

    Args:
        column (tuple): the excel-column to aggregate the data.
        title (str): the string that explains where the values belong to.

    Returns:
        items (dict): the unique values with the aggregated counts.
    """

    items = {}
    for cell in column:
        if cell.value == title:
            continue

        item = cell.value

        if item == None:
            if 'Annet' in items:
                items['Annet'] += 1
            else:
                items['Annet'] = 1
        elif item .strip() in items:
            items[item.strip()] += 1
        else:
            items[item.strip()] = 1

    total = sum(items.values())
    items['Totalt'] = total

    return items

def count_consultations(file):
    """
    Counts all the unique values for each column in the Excel file.

    Args:
        file (str): the path to the Excel file.

    Returns:
        items (dict): the unique values for each row with the aggregated data.
    """

    workbook = load_workbook(filename=file)
    sheet = workbook.active

    month = count_column(sheet['A'], sheet['A1'].value)
    sex = count_column(sheet['C'], sheet['C1'].value)
    level = count_column(sheet['D'], sheet['D1'].value)
    faculty = count_column(sheet['E'], sheet['E1'].value)
    language = count_column(sheet['F'], sheet['F1'].value)
    first_time_visitor = count_column(sheet['G'], sheet['G1'].value)
    drop_in = count_column(sheet['H'], sheet['H1'].value)

    return {sheet['A1'].value: month, sheet['C1'].value: sex, sheet['D1'].value: level, sheet['E1'].value: faculty, sheet['F1'].value: language, sheet['G1'].value: first_time_visitor, sheet['H1'].value: drop_in}

def count_topics(file, semester):
    """
    Counts all the unique values in the .csv-file.

    Args:
        file (str): the path to the csv-file that contains monthly data.
        semester (str): the semester to filter the data on.

    Returns:
        items (dict): the unique values with the aggregated data.
    """

    ACTIVITES_COLUMN = 0
    MONTH_COLUMN = 2
    SEMESTER_DELIMITER = 7

    dataframe = pd.read_csv(file, delimiter = ";")

    if (semester == "spring"):
        df = dataframe.loc[dataframe.iloc[:, MONTH_COLUMN] < SEMESTER_DELIMITER]
    else:
        df = dataframe.loc[dataframe.iloc[:, MONTH_COLUMN] >= SEMESTER_DELIMITER]

    group_by_activities = df.groupby(df.iloc[:, ACTIVITES_COLUMN])
    sum_per_activity = group_by_activities['Antall'].sum()

    items = {}
    for activity, count in zip(group_by_activities, sum_per_activity):
        items[activity[0]] = count

    return items

def allowed_file_type(filename):
    """
    Checks if the file is an allowed file type.

    Args:
        filename (str): the filename to check the type for.

    Returns:
        allowed (bool): a value that states whether the filename is allowed or not.
    """

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_FILE_TYPES

def delete_all_files():
    """
    Delete all the files in the upload folder.
    """

    for file in os.scandir(UPLOAD_FOLDER):
        os.remove(file.path)

@app.route("/skrivesenteret/", methods=['GET', 'POST'])
def skrivesenter():
    delete_all_files()

    if request.method == 'POST':
        error_message = "Noen av feltene er ikke fylt ut. Husk å fylle ut alle feltene."

        # Check if the post request has the file part
        if 'consultations' not in request.files or 'topics' not in request.files:
            flash(error_message)

            delete_all_files()
            return redirect(request.url)

        consultations_file = request.files['consultations']
        topics_file = request.files['topics']

        # User does not select a .xlsx and a .csv file
        if consultations_file.filename == '' or topics_file.filename == '':
            flash(error_message)

            delete_all_files()
            return redirect(request.url)

        # User uploads correct filetypes
        if consultations_file and allowed_file_type(consultations_file.filename) and topics_file and allowed_file_type(topics_file.filename):
            semester = request.form['semester']

            consultations_filename = secure_filename(consultations_file.filename)
            consultations_file.save(os.path.join(app.config['UPLOAD_FOLDER'], consultations_filename))
            consultations_values = count_consultations(os.path.join(app.config['UPLOAD_FOLDER'], consultations_filename))

            topics_filename = secure_filename(topics_file.filename)
            topics_file.save(os.path.join(app.config['UPLOAD_FOLDER'], topics_filename))
            topics_values = count_topics(os.path.join(app.config['UPLOAD_FOLDER'], topics_filename), semester)

            delete_all_files()
            return render_template('skrivesenter.html', consultations_data = consultations_values, topics_data = topics_values, consultations_file = consultations_filename, topics_file = topics_filename, semester = semester)

    delete_all_files()
    return render_template('skrivesenter.html')

if __name__ == "__main__":
    delete_all_files()
    app.run(debug=True, port=5000)
