import streamlit as st
import pandas as pd
import joblib
import gspread
import os
import requests
# Загрузка модели
model = joblib.load('gboost_pipeline_2.0.pkl')
from fpdf import FPDF

def download_font_if_not_exists(font_name, url):
    if not os.path.exists(font_name):
        try:
            r = requests.get(url)
            r.raise_for_status()
            with open(font_name, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            st.error(f"Error downloading font: {e}")

# Функция для генерации PDF
from datetime import datetime
def generate_pdf(data, document_number, date):
    # Download fonts if they are not already cached locally
    download_font_if_not_exists('Roboto-Regular.ttf', 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf')
    download_font_if_not_exists('Roboto-Bold.ttf', 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf')
    
    pdf = FPDF()
    pdf.add_page()
    
    # Add fonts to the PDF builder
    pdf.add_font("Roboto", "", "Roboto-Regular.ttf")
    pdf.add_font("Roboto", "B", "Roboto-Bold.ttf")
    
    # Document Header
    pdf.set_font("Roboto", "B", 16)
    pdf.cell(0, 10, "Документ", ln=True, align="C")
    pdf.ln(10)
    
    # Set up styling for the table
    pdf.set_font("Roboto", "", 11)
    
    table_data = [
        ("Имя", str(data['Name'][0])),
        ("Фамилия", str(data['Surname'][0])),
        ("Телефон номер", str(data['Phone'][0])),
        ("Ёши", str(data['Age'][0])),
        ("Жинси", str(data['Gender'][0])),
        ("Сумма", str(data['Amount'][0])),
        ("Муддат", str(data['Duration'][0] if 'Duration' in data else data['Age'][0])),
        ("Оилавий статус", str(data['MaritalStatus'][0])),
        ("Даромади", str(data['Income'][0])),
        ("Карамогидагилар сони", str(data['Dependants'][0])),
        ("Иш сохаси", str(data['OccupationBranch'][0])),
        ("Лавозими", str(data['Occupation'][0])),
        ("Иш тажрибаси", str(data['ExpCat'][0])),
        ("Скоринг резултати", str(data['Result'][0])),
        ("Кайтариш эхтимоли", str(data['Probability'][0])),
    ]
    
    # Calculate widths
    col_width = pdf.epw / 2
    line_height = pdf.font_size * 2
    
    # Render table
    for label, val in table_data:
        # Bold label
        pdf.set_font("Roboto", "B", 11)
        pdf.cell(col_width, line_height, label, border=1)
        # Regular value
        pdf.set_font("Roboto", "", 11)
        pdf.cell(col_width, line_height, val, border=1, ln=True)
        
    pdf.ln(15)
    
    # Date, Signature, Unique ID
    formatted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
    pdf.set_font("Roboto", "", 11)
    pdf.cell(0, 8, f"Дата: {formatted_date}", ln=True, align="R")
    pdf.cell(0, 8, "Подпись: ______________________", ln=True, align="R")
    pdf.cell(0, 8, f"Уникальный номер документа: {document_number}", ln=True, align="R")
    
    pdf.output("result.pdf")
    
    with open("result.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()
        
    st.download_button(label="Export_Report",
                       data=PDFbyte,
                       file_name="test.pdf",
                       mime='application/octet-stream')

# Ввод данных с использованием инпутов
st.set_page_config(page_title="Модель скоринга Aslzar", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1E3A8A;
        font-weight: 800;
        margin-bottom: 20px;
    }
    .section-header {
        color: #2563EB;
        font-weight: 600;
        border-bottom: 2px solid #DBEAFE;
        padding-bottom: 8px;
        margin-bottom: 15px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%);
        color: white !important;
        font-weight: bold;
        padding: 12px 24px;
        border-radius: 8px;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1D4ED8 0%, #1E40AF 100%);
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>📊 Модель скоринга Aslzar</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4B5563; font-size: 16px; margin-top: -15px;'>Заполните анкету клиента для автоматического расчета скорингового балла</p>", unsafe_allow_html=True)
st.markdown("---")

# Placeholder to display scoring results and PDF download button at the very top of the page
result_placeholder = st.empty()

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>👤 Шахсий маълумотлар (Личные данные)</h3>", unsafe_allow_html=True)
    
    # Имя и Фамилия рядом
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        name = st.text_input('Исм (Имя)', '')
    with sub_col2:
        surname = st.text_input('Фамилия', '')
        
    # Телефон номер и Возраст рядом
    sub_col3, sub_col4 = st.columns(2)
    with sub_col3:
        phone = st.number_input('Телефон номер', value=None, step=1, placeholder="998901234567")
    with sub_col4:
        age = st.number_input('Ёш (Возраст)', value=None, step=1)
        
    # Пол и Семейное положение рядом
    sub_col5, sub_col6 = st.columns(2)
    with sub_col5:
        gender = st.radio('Жинси (Пол)', ['Эркак', 'Аёл'], horizontal=True)
    with sub_col6:
        marital_status = st.selectbox('Оилавий статус (Семейное положение)', ['Оилали', 'Уйланмаган/Турмуш курмаган', 'Ажрашган', 'Бошка'])
        
    dependants = st.selectbox('Карамогидагилар сони (Количество иждивенцев)', [0, 1, 2, 3, 4, 5])

with col2:
    st.markdown("<h3 class='section-header'>💼 Иш ва Даромад (Работа и доходы)</h3>", unsafe_allow_html=True)
    
    # Сфера занятости и Должность рядом
    sub_col7, sub_col8 = st.columns(2)
    with sub_col7:
        occupation_branch = st.selectbox('Иш сохаси (Сфера занятости)', ['Ишлаб чикариш', 'Савдо', 'Банк сохаси', 'Харбий', 'Таълим сохаси', 'Логистика', 'Кишлок хужалиги', 'Медицина сохаси', 'Курилиш сохаси', 'ЖКХ', 'Пенсионер', 'Бошка соха'])
    with sub_col8:
        occupation = st.selectbox('Лавозими (Должность)', ['Оддий ишчи', 'Юкори малакали мутхассис', 'Пенсионер/Студент', 'Бошлиг/Хужаин'])
        
    # Стаж и Месячный доход рядом
    sub_col9, sub_col10 = st.columns(2)
    with sub_col9:
        exp_cat = st.selectbox('Иш тажрибаси (Стаж работы)', ['3 йилдан 5 гача', '5 йилдан зиёд', '1 йилдан 3 гача', '1 йилдан кам', 'Тажрибаси йук'])
    with sub_col10:
        income = st.number_input('Даромади (Месячный доход)', value=None, step=1, placeholder="Ойлик даромади")
    
    st.markdown("<h3 class='section-header'>💰 Кредит тафсилотлари (Детали кредита)</h3>", unsafe_allow_html=True)
    
    # Регион, Сумма и Срок в три колонки рядом
    sub_col11, sub_col12, sub_col13 = st.columns(3)
    with sub_col11:
        region = st.selectbox('Худуд (Регион)', ["Andijon", "Farg'ona", "Marg'ilon", "Yangiqurg'on", "Namangan", "Uychi", "Chortoq", "Samarqand", "Qarshi"])
    with sub_col12:
        amount = st.number_input('Сумма (Сумма кредита)', value=None, step=1, placeholder="Товар нархи")
    with sub_col13:
        duration = st.number_input('Муддат (Срок в месяцах)', value=None, step=1, placeholder="Кредит муддати")

def authenticate_gspread():
    # Active working credentials for scoring@store-gsheet.iam.gserviceaccount.com
    working_credentials = {
        "type": "service_account",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "client_id": "117961286477784237765",
        "token_uri": "https://oauth2.googleapis.com/token",
        "project_id": "store-gsheet",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC3imMnYSRTd/NZ\nMDOk6ShMLGm6qlMSz9Koumr38a/vhcstV7FDQ4dRXQwd1ds9IvtAM7MQyNpT0b2Q\nO+160MH1mA0fhnyAnJSUUhuJD4+oxXXL5o3PgHFEodbKm9q+OYqBXqMC9QDBwXBh\nlIb7J4/om2vOwkiEqJ/n0Gl1VqFsAarqcjA5rYjdYMwBi0SyXsq0xEkeYkn4AVih\nTOzzFkekCaAEpFsVnGQSG89z57uEshh/c8yTN+1zPAWGGXDDOV4KaKB3eEEhpOMY\nuv3M01e1nawKuYPe8EIJZ4xLDU09d2bWr76dSfhZ/rPeWY7iKZJtGlGPIhYbBod1\n1kVJ5A5XAgMBAAECgf8FdsfCtdAsnHExrsVuNsiL2RQ1bsVfrtfv2KSkKZlsdKKb\nsxQEXRlwATI4PMxlN/bWQ+oM51Kv3oq6hlQDzDryN6+/uME6KjjdSMrHHx/1TwLZ\nh1zIrbjBCJwDJktRKB+OumVthnEWmWHxhbxf9Ae9dIXzhqaaRKjqnsH5U49EXiBE\n2zM7EITXWJ0Qr1wMlqpYr7NTQmr8WfR7mLgqUyTv50pTJqASvFmZgI29ldc0u97W\nLt419ktiAYCexh8FbbXX7zxneloyJg0OZlFZc6u5iOWKY5L9BFQiB5G4I8UNZUI9\nCqDGOBXN67IO3QYyc3i0LRojPDO5Oa4qggBcb7kCgYEA43oYi6VLf5Qo7uMIYN8Q\nTYzcpFLCdpZ3xi6YasZAJiuFcSlzyvBtn138+dinQ++Wq5lRc9w0S+pvj5n611TX\ndbKuOrcxCqdeMGOOfCbqcBYnwA9AxWQiguQUeaQC4fz99Xt9WLx85JvLy1lKPb5p\nSFvgv6Z/gw2MnIZavO+83Y8CgYEAzo30Ygo4kcv4PTwuY1bUxI6aPBKyH6FFU9Gs\nMJlI7m5ChdocWtBGuXBOnZywwsqWkTXEcSWQbsJmdDtk3mefWNeyo6lQ6umz+K0p\nGp3fEIOwcdly2oV8WvCTiQVNdZiRmibeU6LBguxQ8FvkWMdx2PfoCqz0z3pJO/HQ\ngAhD7rkCgYAJ9U1fx6OveRf1pUC3pOw8yN7b3reeo2Wo6l9HxVgHk74qvwrPpojW\nAjJR6bcg1Ts+Vd7n+Irdi+zIV5BQnukzwNe5wE1ITx1jduhE7Rs0PvQMh15phcGx\nAzUWQiTSKdYgSgCpws6g32UjiMwkOdK4FTWYjjxky1INhCAyxzf4ZwKBgQC+0Jbm\nBykxTyu5biIwdSPDnTVQr7jLzZEdGMKodsLQOR3NR6wQHP5pCx4lLn6AxOSJqxEZ\nsakXGRHK6J+LclDboxANbzooedNftKAXTaanO/DBjC81PkGeRUcWOsbPDy3bKXMT\n8nQwPZ2cHlf5x+4dkQ9U5WiXTxHehcqmrHwNSQKBgQCKmZOpsinVFjYtXX6elhg6\n/vzbSLEe4b2GE2s9GRX+MV7VPcJ5gt9QRXFwIp8c7b9zAqAZ73vL0Jb7rv5VGFgh\n/HytspWiooRE25RIFeOE0e11TRd4lEOFQir7WnIUJPVHn7aFAMD5rS3m2r8jGLOl\n8A3E4aBmbFPj3aake7adaA==\n-----END PRIVATE KEY-----\n",
        "client_email": "scoring@store-gsheet.iam.gserviceaccount.com",
        "private_key_id": "f30172a3ecedeebfc8e1081e47715eafccba7e80",
        "universe_domain": "googleapis.com",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/scoring%40store-gsheet.iam.gserviceaccount.com",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
    }

    # Direct override to ensure we use the 100% working credentials
    sa = gspread.service_account_from_dict(working_credentials)
    return sa

# Function to duplicate data to Google Sheets
def duplicate_to_gsheet(new_row):
    try:
        # Authenticate with Google Sheets
        gc = authenticate_gspread()
    except Exception as auth_err:
        st.error(f"❌ Google Sheets-га уланишда хатолик: {auth_err} (Ошибка авторизации Google Sheets)")
        return

    try:
        # First, try to open the spreadsheet explicitly by your unique ID
        sh = gc.open_by_key("1183_faZnS3i7hGqWITilgpZU6QGK8ZpVrzKy6jUvXxY")
    except Exception:
        # Fallback to opening by name if opening by ID fails
        try:
            sh = gc.open("AslzarScoring")
        except gspread.exceptions.SpreadsheetNotFound:
            # Gracefully handle when spreadsheet is not found by creating a new one
            try:
                sh = gc.create("AslzarScoring")
                # Share it with Behzod's email if possible
                try:
                    sh.share('erifieder@gmail.com', perm_type='user', role='writer')
                except Exception:
                    pass
                st.info("ℹ️ Янги 'AslzarScoring' жадвали яратилди ва erifieder@gmail.com билан улашилди. (Создана новая таблица 'AslzarScoring')")
            except Exception as create_err:
                st.error(f"❌ Жадвални очиш ва яратишда хатолик: {create_err}")
                return

    try:
        # Select the worksheet
        try:
            worksheet = sh.worksheet("Scoring")
        except gspread.exceptions.WorksheetNotFound:
            # If worksheet is not found, create a new one
            worksheet = sh.add_worksheet(title="Scoring", rows="100", cols="20")
            
        # Check if there's any content in the worksheet
        existing_data = worksheet.get_all_values()

        # Get existing headers if they exist
        headers = existing_data[0] if existing_data else None

        if not headers:
            headers = ['Худуд', 'Телефон номер', 'Имя', 'Фамилия', 'Возраст', 'Пол', 'Сумма кредита', 'Период', 'Семейное положение', 'Доход',
                       'Иждевенцы', 'Сфера занятости', 'Роль', 'Стаж работы', 'Результат', 'Вероятность возврата', 'Дата', 'Номер документа']
            worksheet.append_row(headers)

        # Convert the new_row DataFrame to a list and append it to the worksheet
        new_row = new_row[["Region", 'Phone', 'Name', 'Surname', 'Age', 'Gender', 'Amount', 'Duration', 'MaritalStatus', 'Income',
                           'Dependants', 'OccupationBranch', 'Occupation', 'ExpCat', 'Result', 'Probability', 'Date', 'DocumentNumber']]
        new_row_list = new_row.values.tolist()
        worksheet.append_rows(new_row_list)
    except Exception as e:
        client_email = gc.auth.service_account_email if (hasattr(gc, 'auth') and hasattr(gc.auth, 'service_account_email')) else 'unknown'
        st.error(f"❌ Жадвалга маълумот ёзишда хатолик: {e} (Ошибка записи данных в таблицу) | Active Account: {client_email}")

# Предсказание
# Предсказание
st.markdown("<br>", unsafe_allow_html=True)
if st.button('🚀 Получить скоринг'):
    if not name or not surname or phone is None or age is None or amount is None or duration is None or income is None:
        st.warning("⚠️ Илтимос, барча майдонларни тўлдиринг! (Пожалуйста, заполните все поля!)")
    else:
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        document_number = f'Doc_{current_date.replace(" ", "_").replace(":", "_")}'

        input_data = pd.DataFrame({
            'Age': [age],
            'Gender': [1 if gender == 'Эркак' else 0],
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
        prob_val = round(prediction[0]*100, 2)
        is_approved = prediction[0] > (1 - 0.06)

        # Prepare final input data for saving/PDF
        input_data['Region'] = region
        input_data['Name'] = name
        input_data['Surname'] = surname
        input_data['Phone'] = phone
        input_data['Result'] = 'Одобрено' if is_approved else 'Отказано'
        input_data['Gender'] = gender
        input_data['Probability'] = f'{prob_val}%'
        input_data['Date'] = current_date
        input_data['DocumentNumber'] = document_number

        # Duplicate to Google Sheets
        duplicate_to_gsheet(input_data)
        
        # Display the scoring result beautifully inside the placeholder at the top of the page
        with result_placeholder.container():
            st.markdown("""
            <div style='background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); padding: 20px; border-radius: 12px; border: 1px solid #BFDBFE; margin-bottom: 25px;'>
                <h3 style='color: #1E3A8A; font-weight: 700; margin-top: 0; margin-bottom: 5px; text-align: center;'>🎯 Скоринг Натижаси (Результат скоринга)</h3>
            </div>
            """, unsafe_allow_html=True)
            
            res_card_col1, res_card_col2 = st.columns([3, 2])
            
            with res_card_col1:
                if is_approved:
                    st.success("🎉 **КРЕДИТ ТАСДИКЛАНДИ! (ОДОБРЕНО)**")
                    st.balloons()
                else:
                    st.error("😞 **РАД ЭТИЛДИ! (ОТКАЗАНО)**")
                
                st.metric(label="Кайтариш эхтимоли (Вероятность возврата)", value=f"{prob_val}%")
                
            with res_card_col2:
                st.markdown("<h4 style='color: #1E3A8A; margin-top: 0; font-weight: 600; text-align: center;'>📥 Ҳисоботни юклаб олиш (Скачать отчет)</h4>", unsafe_allow_html=True)
                # Centering container for the button
                st.markdown("<div style='display: flex; justify-content: center; margin-top: 15px;'>", unsafe_allow_html=True)
                generate_pdf(input_data, document_number, current_date)
                st.markdown("</div>", unsafe_allow_html=True)
                
            st.markdown("<hr style='border: 1.5px solid #3B82F6; margin-bottom: 25px;'>", unsafe_allow_html=True)