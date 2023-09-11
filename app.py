from flask import Flask, render_template, request
import pandas as pd
from openpyxl import load_workbook
import random
from recognition import upload, get_transcription


app = Flask(__name__)

uploaded_df = None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global uploaded_df
    global columns
    global filename

    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        file.save(filename)
        wb = load_workbook(filename)
        sheet = wb.active
        data = sheet.values
        columns = next(data)[0:]
        uploaded_df = pd.DataFrame(data, columns=columns)
        return render_template('index.html', filename=filename)

    return render_template('index.html', filename=None)

@app.route('/random_row')
def random_row_func():
    global uploaded_df
    global random_row
    global row_values

    if uploaded_df is not None and not uploaded_df.empty:
        random_row = uploaded_df.sample(n=1)
        columns = uploaded_df.columns.tolist()
        row_values = random_row.values.tolist()[0]
        return render_template('index.html', filename=filename, random_row=row_values[1])
    else:
        return render_template('index.html', filename=None)

@app.route('/check', methods=['POST'])
def check():
    global random_row

    if random_row is not None:
        user_input = request.form.get('user_input')
        first_column_value = random_row.iloc[0, 0]

        if user_input.lower().strip() == first_column_value.lower().strip():
            paragraph_text = 'Correct! Press "Get random word" to proceed'
        else:
            paragraph_text = 'Wrong or no input was given'

        return render_template('index.html', filename=filename, random_row=row_values[1], paragraph_text=paragraph_text)
    else:
        return render_template('index.html', filename=filename, random_row=row_values[1], paragraph_text='No input given')
    
@app.route('/record', methods=['POST'])
def record():
    if 'recorded_file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['recorded_file']
    if file.filename == '':
        return 'No selected file', 400

    file.save(file.filename)  # Save the file on the local machine
    audio_url = upload(file.filename)
    transcription, error = get_transcription(audio_url)
    if error: 
        print('error')
    transcription = transcription['text'].lower().replace('.', '')
    return render_template('index.html', filename=filename, random_row=row_values[1], default_value=transcription)

@app.route('/show_translation')
def show_translation():
    global random_row
    translation = random_row.iloc[0, 0]
    
    return render_template('index.html', filename=filename, random_row=row_values[1], paragraph_text=translation)
    
if __name__ == '__main__':
    app.run(debug=True, port = 5000)
