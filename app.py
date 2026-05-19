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

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 class='section-header'>👤 Шахсий маълумотлар (Личные данные)</h3>", unsafe_allow_html=True)
    name = st.text_input('Исм (Имя)', '')
    surname = st.text_input('Фамилия', '')
    phone = st.number_input('Телефон номер', value=None, step=1, placeholder="998901234567")
    age = st.number_input('Ёш (Возраст)', value=None, step=1)
    gender = st.radio('Жинси (Пол)', ['Эркак', 'Аёл'], horizontal=True)
    marital_status = st.selectbox('Оилавий статус (Семейное положение)', ['Оилали', 'Уйланмаган/Турмуш курмаган', 'Ажрашган', 'Бошка'])
    dependants = st.selectbox('Карамогидагилар сони (Количество иждивенцев)', [0, 1, 2, 3, 4, 5])

with col2:
    st.markdown("<h3 class='section-header'>💼 Иш ва Даромад (Работа и доходы)</h3>", unsafe_allow_html=True)
    occupation_branch = st.selectbox('Иш сохаси (Сфера занятости)', ['Ишлаб чикариш', 'Савдо', 'Банк сохаси', 'Харбий', 'Таълим сохаси', 'Логистика', 'Кишлок хужалиги', 'Медицина сохаси', 'Курилиш сохаси', 'ЖКХ', 'Пенсионер', 'Бошка соха'])
    occupation = st.selectbox('Лавозими (Должность)', ['Оддий ишчи', 'Юкори малакали мутхассис', 'Пенсионер/Студент', 'Бошлиг/Хужаин'])
    exp_cat = st.selectbox('Иш тажрибаси (Стаж работы)', ['3 йилдан 5 гача', '5 йилдан зиёд', '1 йилдан 3 гача', '1 йилдан кам', 'Тажрибаси йук'])
    income = st.number_input('Даромади (Месячный доход)', value=None, step=1, placeholder="Ойлик даромади")
    
    st.markdown("<h3 class='section-header'>💰 Кредит тафсилотлари (Детали кредита)</h3>", unsafe_allow_html=True)
    region = st.selectbox('Худуд (Регион)', ["Andijon", "Farg'ona", "Marg'ilon", "Yangiqurg'on", "Namangan", "Uychi", "Chortoq", "Samarqand", "Qarshi"])
    amount = st.number_input('Сумма (Сумма кредита)', value=None, step=1, placeholder="Товар нархи")
    duration = st.number_input('Муддат (Срок в месяцах)', value=None, step=1, placeholder="Кредит муддати")

def authenticate_gspread():
    # Load Google Sheets API credentials from environment variable LINK
    link = os.getenv('LINK')
    if not link and os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#'):
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        key, value = parts
                        if key.strip() == 'LINK':
                            link = value.strip()
                            break
    
    if not link:
        raise ValueError("LINK environment variable not found")
        
    response = requests.get(link)
    response.raise_for_status()
    res_data = response.json()
    
    # Handle both wrapped (jsonbin.io) and direct JSON formats
    if isinstance(res_data, dict) and 'record' in res_data:
        credentials = res_data['record']
    else:
        credentials = res_data
        
    sa = gspread.service_account_from_dict(credentials)
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
        headers = ['Худуд', 'Телефон номер', 'Имя', 'Фамилия', 'Возраст', 'Пол', 'Сумма кредита', 'Период', 'Семейное положение', 'Доход',
                   'Иждевенцы', 'Сфера занятости', 'Роль', 'Стаж работы', 'Результат', 'Вероятность возврата', 'Дата', 'Номер документа']
        worksheet.append_row(headers)

    # Convert the new_row DataFrame to a list and append it to the worksheet
    new_row = new_row[["Region", 'Phone', 'Name', 'Surname', 'Age', 'Gender', 'Amount', 'Duration', 'MaritalStatus', 'Income',
                       'Dependants', 'OccupationBranch', 'Occupation', 'ExpCat', 'Result', 'Probability', 'Date', 'DocumentNumber']]
    new_row_list = new_row.values.tolist()
    worksheet.append_rows(new_row_list)

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

        st.markdown("---")
        st.markdown("<h3 style='color: #1E3A8A; font-weight: 700;'>🎯 Натижа (Результат скоринга)</h3>", unsafe_allow_html=True)
        
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.metric(label="Кайтариш эхтимоли (Вероятность возврата)", value=f"{prob_val}%")
            
        with res_col2:
            if is_approved:
                st.success("🎉 КРЕДИТ ТАСДИКЛАНДИ! (ОДОБРЕНО)")
                st.balloons()
            else:
                st.error("😞 РАД ЭТИЛДИ! (ОТКАЗАНО)")

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
        
        # Generate PDF and provide download button
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #4B5563;'>📥 Документни юклаб олиш (Скачать отчет)</h4>", unsafe_allow_html=True)
        generate_pdf(input_data, document_number, current_date)