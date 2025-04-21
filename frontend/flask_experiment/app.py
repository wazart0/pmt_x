# from dash import Dash, dash_table, dcc, html, Input, Output, callback
# from flask import Flask, request, render_template, session, redirect
# import pandas as pd

# app = Dash(__name__)

# params = [
#     'Weight', 'Torque', 'Width', 'Height',
#     'Efficiency', 'Power', 'Displacement'
# ]

# app.layout = html.Div([
#     dash_table.DataTable(
#         id='table-editing-simple',
#         columns=(
#             [{'id': 'Model', 'name': 'Model'}] +
#             [{'id': p, 'name': p} for p in params]
#         ),
#         data=[
#             dict(Model=i, **{param: 0 for param in params})
#             for i in range(1, 5)
#         ],
#         editable=True
#     ),
#     dcc.Graph(id='table-editing-simple-output')
# ])


# @callback(
#     Output('table-editing-simple-output', 'figure'),
#     Input('table-editing-simple', 'data'),
#     Input('table-editing-simple', 'columns'))
# def display_output(rows, columns):
#     df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
#     return {
#         'data': [{
#             'type': 'parcoords',
#             'dimensions': [{
#                 'label': col['name'],
#                 'values': df[col['id']]
#             } for col in columns]
#         }]
#     }


from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = "supersecret"

# Sample data
data = [
    {"id": 1, "name": "John", "email": "john@example.com"},
    {"id": 2, "name": "Jane", "email": "jane@example.com"}
]

class EditRowForm(FlaskForm):
    id = HiddenField()
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Save')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        row_id = int(request.form['id'])
        for row in data:
            if row["id"] == row_id:
                row["name"] = request.form['name']
                row["email"] = request.form['email']
                break
        return redirect(url_for('index'))
    return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

