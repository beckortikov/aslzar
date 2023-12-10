import streamlit as st
import pandas as pd
import joblib
import gspread
# Загрузка модели
model = joblib.load('gboost_pipeline_2.0.pkl')
import pdfkit
# Функция для генерации PDF
from datetime import datetime
def generate_pdf(data, document_number, date):
    rendered = f'''
    <!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <title>Client Request</title>
</head>

<body>
    <div class="container">
        <br><br>
        <h4 class="text-center"><strong>Документ</strong></h4>
        <br><br>
        <table class="table table-bordered">
            <tbody>
                <tr>
                    <td style="width: 50%;">Имя</td>
                    <td style="width: 50%;">{data['Name'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Фамилия</td>
                    <td style="width: 50%;">{data['Surname'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Телефон номер</td>
                    <td style="width: 50%;">{data['Phone'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Ёши</td>
                    <td style="width: 50%;">{data['Age'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Жинси</td>
                    <td style="width: 50%;">{data['Gender'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Сумма</td>
                    <td style="width: 50%;">{data['Amount'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Муддат</td>
                    <td style="width: 50%;">{data['Age'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Оилавий статус</td>
                    <td style="width: 50%;">{data['MaritalStatus'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Даромади</td>
                    <td style="width: 50%;">{data['Income'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Карамогидагилар сони</td>
                    <td style="width: 50%;">{data['Dependants'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Иш сохаси</td>
                    <td style="width: 50%;">{data['OccupationBranch'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Лавозими</td>
                    <td style="width: 50%;">{data['Occupation'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Иш тажрибаси</td>
                    <td style="width: 50%;">{data['ExpCat'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Скоринг резултати</td>
                    <td style="width: 50%;">{data['Result'][0]}</td>
                </tr>
                <tr>
                    <td style="width: 50%;">Кайтариш эхтимоли</td>
                    <td style="width: 50%;">{data['Probability'][0]}</td>
                </tr>
            </tbody>
        </table>

   <br><br><br><br>
        <tr>
            <td colspan="2" style="text-align: right;">Дата {datetime.strptime(date,'%Y-%m-%d %H:%M:%S').date()}</td>
        </tr>
        </t>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <tr>
            <td colspan="2" style="text-align: right;">Подпись: ______________________</td>
    <br>
    <tr>
        <td colspan="2" style="text-align: right;">Уникальный номер документа: {document_number}</td>
    </tr>
    </div>
    </body>

    </html>
    '''
    pdfkit.from_string(rendered, 'result.pdf', options={'encoding': 'utf-8'})
    with open("result.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()

    st.download_button(label="Export_Report",
                       data=PDFbyte,
                       file_name="test.pdf",
                       mime='application/octet-stream')

# Ввод данных с использованием инпутов
st.title('Модель скоринга')
name = st.sidebar.text_input(r'$\textsf{\normalsize Исм}$', '')
surname = st.sidebar.text_input(r'$\textsf{\normalsize Фамилия}$', '')
phone = st.sidebar.number_input(r'$\textsf{\normalsize Телефон номер}$', value=None, step=1, placeholder="Номер теринг")
age = st.sidebar.number_input(r'$\textsf{\normalsize Ёш}$', value=None, step=1)
gender = st.sidebar.radio(r'$\textsf{\normalsize Жинси}$', ['Эркак', 'Аёл'])
amount = st.sidebar.number_input(r'$\textsf{\normalsize Сумма}$', value=None, step=1, placeholder="Товар нархи")
duration = st.sidebar.number_input(r'$\textsf{\normalsize Муддат}$', value=None, step=1, placeholder="Кредит муддати")
marital_status = st.sidebar.selectbox(r'$\textsf{\normalsize Оилавий статус}$', ['Оилали', 'Уйланмаган/Турмуш курмаган', 'Ажрашган', 'Бошка'])
income = st.sidebar.number_input(r'$\textsf{\normalsize Даромади}$', value=None, step=1, placeholder="Ойлик даромади")
dependants = st.sidebar.selectbox(r'$\textsf{\normalsize Карамогидагилар сони}$', [0, 1, 2, 3, 4, 5])
occupation_branch = st.sidebar.selectbox(r'$\textsf{\normalsize Иш сохаси}$', ['Ишлаб чикариш', 'Бошка соха', 'Савдо', 'Банк сохаси', 'Харбий', 'Таълим сохаси', 'Логистика', 'Кишлок хужалиги', 'Медицина сохаси',
                                                                        'Курилиш сохаси', 'ЖКХ', 'Пенсионер'])
occupation = st.sidebar.selectbox(r'$\textsf{\normalsize Лавозими}$', ['Оддий ишчи', 'Юкори малакали мутхассис', 'Пенсионер/Студент', 'Бошлиг/Хужаин'])
exp_cat = st.sidebar.selectbox(r'$\textsf{\normalsize Иш тажрибаси}$', ['3 йилдан 5 гача', '5 йилдан зиёд', '1 йилдан 3 гача', '1 йилдан кам', 'Тажрибаси йук'])

def authenticate_gspread():
    # Load Google Sheets API credentials
    sa = gspread.service_account(filename='credits_mobi.json')
    return sa

# Function to duplicate data to Google Sheets
def duplicate_to_gsheet(new_row):
    # Authenticate with Google Sheets
    gc = authenticate_gspread()

    # Create a new Google Sheets spreadsheet
    sh = gc.open("AslzarScoring")

    # Select the first sheet (index 0)
    worksheet = sh.worksheet("Scoring")

    # Check if there's any content in the worksheet
    existing_data = worksheet.get_all_values()

    # Get existing headers if they exist
    headers = existing_data[0] if existing_data else None

    if not headers:
        headers = ['Телефон номер', 'Имя', 'Фамилия', 'Возраст', 'Пол', 'Сумма кредита', 'Период', 'Семейное положение', 'Доход',
                   'Иждевенцы', 'Сфера занятости', 'Роль', 'Стаж работы', 'Результат', 'Вероятность возврата', 'Дата', 'Номер документа']
        worksheet.append_row(headers)

    # Convert the new_row DataFrame to a list and append it to the worksheet
    new_row = new_row[['Phone', 'Name', 'Surname', 'Age', 'Gender', 'Amount', 'Duration', 'MaritalStatus', 'Income',
                       'Dependants', 'OccupationBranch', 'Occupation', 'ExpCat', 'Result', 'Probability', 'Date', 'DocumentNumber']]
    new_row_list = new_row.values.tolist()
    worksheet.append_rows(new_row_list)

# Предсказание
if st.sidebar.button('Получить скоринг'):
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    document_number = f'Doc_{current_date.replace(" ", "_").replace(":", "_")}'

    input_data = pd.DataFrame({
        'Age': [age],
        'Gender': [1 if gender == 'Мужской' else 0],
        'Amount': [amount],
        'Duration': [duration],
        'MaritalStatus': [marital_status],
        'Income': [income],
        'Dependants': [dependants],
        'OccupationBranch': [occupation_branch],
        'Occupation': [occupation],
        'ExpCat': [exp_cat]
    })

    prediction = model.predict_proba(input_data)[:, 0]
    st.subheader('Результат:')
    st.write(f'Кредит кайтариш эхтимоли: {round(prediction[0]*100, 2)}%')

    input_data['Name'] = name
    input_data['Surname'] = surname
    input_data['Phone'] = phone
    input_data['Result'] = 'Одобрено' if prediction > 1 - 0.06 else 'Отказано'
    input_data['Gender'] = gender
    input_data['Probability'] = f'{round(prediction[0]*100, 2)}%'
    input_data['Date'] = current_date
    input_data['DocumentNumber'] = document_number

    if prediction > 1 - 0.06:
        st.success(r'$\textsf{\Large Кредит тасдикланди! 🎉}$')
        st.balloons()
        duplicate_to_gsheet(input_data)
    else:
        st.error(r'$\textsf{\Large Рад этилди. 😞}$')
        duplicate_to_gsheet(input_data)

    generate_pdf(input_data, document_number, current_date)