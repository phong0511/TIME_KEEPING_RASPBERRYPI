from flask import Flask, request, jsonify
import subprocess
import os
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("path/to/your-firebase-adminsdk.json")  # Thay bằng file JSON của bạn
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://your-database-name.firebaseio.com/"  # Thay bằng URL database của bạn
})

# Reference to the employees node in Firebase
employees_ref = db.reference("employees")

# Route: Fetch all employees from Firebase
@app.route('/get_employees', methods=['GET'])
def get_employees():
    employees = employees_ref.get()
    return jsonify(employees if employees else {})

# Route: Add new employee to Firebase and start data collection
@app.route('/register_employee', methods=['POST'])
def register_employee():
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"status": "error", "message": "Name is required"}), 400

    # Add employee to Firebase
    new_employee = {
        "name": name,
        "time": "Đăng ký",
        "session": "N/A",
        "status": "Đăng ký mới",
        "schedule": "N/A"
    }
    employees_ref.push(new_employee)

    # Run image_capture.py to collect data
    try:
        subprocess.run(["python", "image_capture.py"], check=True)
        # Run model_training.py to train model
        subprocess.run(["python", "model_training.py"], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": f"Error: {e}"}), 500

    return jsonify({"status": "success", "message": "Employee registered successfully"})

# Route: Delete an employee from Firebase
@app.route('/delete_employee/<string:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    employee_ref = employees_ref.child(employee_id)
    if not employee_ref.get():
        return jsonify({"status": "error", "message": "Employee not found"}), 404

    employee_ref.delete()
    return jsonify({"status": "success", "message": "Employee deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)
