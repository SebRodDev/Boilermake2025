from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/api/students', methods=['GET'])
def get_students():
    # Read the parquet file for at-risk students
    at_risk_df = pd.read_parquet('src/risks_week10.parquet')
    at_risk_students = at_risk_df.to_dict(orient='records')
    return jsonify(at_risk_students)

if __name__ == '__main__':
    app.run(debug=True)