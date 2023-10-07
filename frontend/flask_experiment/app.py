from flask import *
import pandas as pd


app = Flask(__name__)

@app.route("/")
def show_tables():
    data = pd.read_csv('dummy_data.csv')
    # data.set_index(['Name'], inplace=True)
    # data.index.name=None
    # females = data.loc[data.Gender=='f']
    # males = data.loc[data.Gender=='m']
    return render_template('view.html',tables=data)

if __name__ == "__main__":
    app.run()