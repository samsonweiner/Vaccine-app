from flask import Flask, request, render_template, url_for
from google.cloud import bigquery

PROJECT_ID = 'project-name'
client = bigquery.Client(project = PROJECT_ID, location = "US")

def get_patient_data(ID):
    name_group_query = """
    SELECT patient.patientId, vaccineCode.text, occurrence.dateTime, status FROM `project-name.dataset-name.Immunization`
"""
    query_results = client.query(name_group_query)
    vaccines = {}
    for result in query_results:
        if ID == result[0]:
            vaccine, date, status = result[1], result[2], result[3]
            if ',' in vaccine:
                vaccine, info = vaccine[:vaccine.index(',')], vaccine[vaccine.index(',')+1:]
            elif '(' in vaccine:
                vaccine, info = vaccine[:vaccine.index('(')], vaccine[vaccine.index('(')+1:]
                info.replace(')', '')
            else:
                info = ''
            date = date[:date.index('T')]#.split('-')
            if vaccine not in vaccines:
                vaccines[vaccine] = {'type': vaccine, 'info': info, 'status': status, 'dates': [date]}
            else:
                vaccines[vaccine]['dates'].append(date)
    return list(vaccines.values())

def get_patient_suggestions(vaccines):
    f = open('static/vaccine_freqs.txt')
    lines = f.readlines()
    f.close()
    all_vacs = [line[:-1] for line in lines]
    current_vacs = [vac['type'] for vac in vaccines]
    missing_vacs = [vac for vac in all_vacs if vac not in current_vacs]

    suggestions = []
    for i in range(min(3, len(missing_vacs))):
        suggestions.append({'type': missing_vacs[i], 'status': 'suggested'})

    return suggestions

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route('/', methods=['POST'])
def my_form_post():
    pat_id = request.form['patient']
    vaccines = get_patient_data(pat_id)
    suggested_vaccines = get_patient_suggestions(vaccines)
    if len(vaccines) == 0:
        return render_template('invalid.html')
    else:
        return render_template('profile.html', current_vaccines=vaccines, suggested_vaccines=suggested_vaccines)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)