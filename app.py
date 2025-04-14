from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import os
import random  # For demo purposes
import pandas as pd
import numpy as np
import pickle
from models import db, ContactMessage, Subscription, BlogPost
from email_validator import validate_email, EmailNotValidError




# Flask app
app = Flask(__name__)

# Use MySQL database if DATABASE_URL is provided, otherwise fallback to SQLite
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_diagnosis.db'
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_for_testing")

# Initialize database
db.init_app(app)

# Create all tables
with app.app_context():
    db.create_all()

# Create mock data structures for testing UI without actual models/datasets
class MockDataset:
    def __init__(self, data=None):
        self.data = data or {}
    
    def __getitem__(self, key):
        return MockDataset(self.data)
    
    @property
    def empty(self):
        return False
    
    @property
    def iloc(self):
        return MockDatasetItem()
    
    def tolist(self):
        return ["Exercise for 30 minutes daily", "Stay hydrated", "Get adequate rest"]

class MockDatasetItem:
    def __getitem__(self, key):
        return "Sample data for testing"

# Load real datasets
try:
    # Load description data
    description = pd.read_csv('datasets/description.csv')
    
    # Load precautions data
    precautions = pd.read_csv('datasets/precautions_df.csv')
    
    # Load workout data
    workout = pd.read_csv('datasets/workout_df.csv')
    
    # Load medication data
    medications = pd.read_csv('datasets/medications.csv')
    
    # Load diet data
    diets = pd.read_csv('datasets/diets.csv')
    
    # Load symptom description data if available
    try:
        sym_des = pd.read_csv('datasets/symtoms_df.csv')
    except:
        sym_des = MockDataset()  # Fallback to mock data if needed
        
    # Load the trained model
    try:
        svc = pickle.load(open('models/svc.pkl', 'rb'))
    except Exception as e:
        print(f"Error loading model: {e}")
        # Fallback to mock model if needed
        class MockModel:
            def predict(self, input_vector):
                # Random disease for testing
                return [random.choice(list(diseases_list.keys()))]
        svc = MockModel()
        
except Exception as e:
    print(f"Error loading datasets: {e}")
    # Fallback to mock data if needed
    sym_des = MockDataset()
    precautions = MockDataset()
    workout = MockDataset()
    description = MockDataset()
    medications = MockDataset()
    diets = MockDataset()
    
    # Mock model
    class MockModel:
        def predict(self, input_vector):
            # Random disease for testing
            return [random.choice(list(diseases_list.keys()))]
            
    svc = MockModel()

# Helper function
def helper(dis):
    try:
        # Get disease description
        desc = description[description['Disease'] == dis]['Description']
        desc = " ".join([w for w in desc]) if not desc.empty else f"No description available for {dis}."

        # Get precautions
        pre = precautions[precautions['Disease'] == dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
        if pre.empty:
            pre = [["Consult with a healthcare professional", "Follow your doctor's advice", "Maintain a healthy lifestyle", "Stay hydrated"]]
        else:
            pre = [col for col in pre.values]

        # Get medications
        med = medications[medications['Disease'] == dis]['Medication']
        if not med.empty:
            # Clean the string format from the CSV
            med_str = med.iloc[0]
            med_str = med_str.replace('[', '').replace(']', '').replace("'", '')
            med_list = [item.strip() for item in med_str.split(',')]
            med = [med_list]
        else:
            med = [["Consult with your doctor for appropriate medications"]]

        # Get diet recommendations
        diet = diets[diets['Disease'] == dis]['Diet']
        if not diet.empty:
            # Clean the string format from the CSV
            diet_str = diet.iloc[0]
            diet_str = diet_str.replace('[', '').replace(']', '').replace("'", '')
            diet_list = [item.strip() for item in diet_str.split(',')]
            die = [diet_list]
        else:
            die = [["Follow a balanced diet as recommended by your healthcare provider"]]

        # Get workout recommendations
        wrkout_df = workout[workout['disease'] == dis]['workout']
        if not wrkout_df.empty:
            wrkout = wrkout_df.tolist()
        else:
            wrkout = ["Consult with your doctor before starting any exercise regime"]

        print(f"Disease: {dis}")
        print(f"Medications: {med}")
        print(f"Diet: {die}")
        print(f"Workout: {wrkout}")
        
        return desc, pre, med, die, wrkout
    except Exception as e:
        print(f"Error in helper function: {e}")
        # Return default values in case of error
        default_desc = f"Information for {dis} is currently unavailable."
        default_pre = [["Consult with a healthcare professional", "Follow your doctor's advice", "Maintain a healthy lifestyle", "Stay hydrated"]]
        default_med = [["Consult with your doctor for appropriate medications"]]
        default_diet = [["Follow a balanced diet as recommended by your healthcare provider"]]
        default_workout = ["Consult with your doctor before starting any exercise regime"]
        return default_desc, default_pre, default_med, default_diet, default_workout

# Symptoms dictionary
symptoms_dict = {
    'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4, 'chills': 5,
    'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11,
    'burning_micturition': 12, 'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16,
    'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21,
    'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26,
    'breathlessness': 27, 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32,
    'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37,
    'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42,
    'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46,
    'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51,
    'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56,
    'weakness_in_limbs': 57, 'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60,
    'bloody_stool': 61, 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66,
    'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71,
    'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75,
    'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79, 'muscle_weakness': 80,
    'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85,
    'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89,
    'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92, 'internal_itching': 93,
    'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98,
    'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 'dischromic _patches': 102,
    'watering_from_eyes': 103, 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107,
    'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111,
    'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115,
    'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119,
    'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124,
    'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128,
    'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131
}

# Diseases list
diseases_list = {
    15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction',
    33: 'Peptic ulcer diseae', 1: 'AIDS', 12: 'Diabetes ', 17: 'Gastroenteritis', 6: 'Bronchial Asthma',
    23: 'Hypertension ', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)',
    28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A',
    19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis',
    36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack',
    39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 31: 'Osteoarthristis',
    5: 'Arthritis', 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne', 38: 'Urinary tract infection',
    35: 'Psoriasis', 27: 'Impetigo'
}

# Model Prediction function
def get_predicted_value(patient_symptoms):
    input_vector = np.zeros(len(symptoms_dict))
    for item in patient_symptoms:
        input_vector[symptoms_dict[item]] = 1
    return diseases_list[svc.predict([input_vector])[0]]

# Home route
@app.route("/")
def index():
    return render_template("index.html", symptoms=list(symptoms_dict.keys()))

# Predict route
@app.route('/home', methods=['GET', 'POST'])
@app.route('/predict', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        print(symptoms)

        if not symptoms:
            message = "Please enter symptoms."
            return render_template('index.html', message=message, symptoms=list(symptoms_dict.keys()))

        # Split the symptoms and clean the input
        user_symptoms = [s.strip().lower() for s in symptoms.split(',')]

        # Check for invalid symptoms
        invalid_symptoms = [symptom for symptom in user_symptoms if symptom not in symptoms_dict]

        if invalid_symptoms:
            message = f"The following symptoms are invalid: {', '.join(invalid_symptoms)}. Please check and try again."
            return render_template('index.html', message=message, 
                               invalid_symptoms=", ".join(invalid_symptoms),
                               symptoms=list(symptoms_dict.keys()),
                               user_symptoms=symptoms)

        # Predict disease
        predicted_disease = get_predicted_value(user_symptoms)
        dis_des, precautions, medications, rec_diet, workout = helper(predicted_disease)

        # Check if precautions list is empty
        if not precautions or len(precautions) == 0:
            precautions = [["Consult with a healthcare professional", "Follow your doctor's advice", "Maintain a healthy lifestyle", "Stay hydrated"]]

        return render_template('index.html', predicted_disease=predicted_disease, dis_des=dis_des,
                               my_precautions=precautions[0], medications=medications, my_diet=rec_diet,
                               workout=workout, symptoms=list(symptoms_dict.keys()),
                               user_symptoms=symptoms)

    return render_template('index.html', symptoms=list(symptoms_dict.keys()))

# About route
@app.route('/about')
def about():
    return render_template("about.html")

# Contact route with form processing
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Validate form inputs
        if not name or not email or not subject or not message:
            flash('All fields are required', 'danger')
            return render_template("contact.html")
        
        # Create new message
        new_message = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Save to database
        db.session.add(new_message)
        db.session.commit()
        
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    
    return render_template("contact.html")

# Developer route
@app.route('/developer')
def developer():
    return render_template("developer.html")

# Blog route
@app.route('/blog')
def blog():
    return render_template("blog.html")

# Subscription handler
@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        # For AJAX requests
        if request.headers.get('Content-Type') == 'application/json':
            data = request.get_json()
            email = data.get('email', '')
        else:
            # For form submissions
            email = request.form.get('email', '')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email address is required.'})
        
        try:
            # Validate email format
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            return jsonify({'success': False, 'message': str(e)})
            
        # Check if already subscribed
        existing_subscription = Subscription.query.filter_by(email=email).first()
        if existing_subscription:
            if existing_subscription.is_active:
                return jsonify({'success': False, 'message': 'This email is already subscribed.'})
            else:
                # Reactivate subscription
                existing_subscription.is_active = True
                db.session.commit()
                return jsonify({'success': True, 'message': 'Your subscription has been reactivated!'})
        
        # Create new subscription
        new_subscription = Subscription(email=email)
        db.session.add(new_subscription)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Thank you for subscribing to our newsletter!'})
    except Exception as e:
        print(f"Error in subscription process: {e}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again later.'})

# Blog article pages
@app.route('/blog/latest/<slug>')
def blog_article(slug):
    # For a fully functional blog, fetch the article from database
    # Since we're just demonstrating, we'll return a message
    return render_template('blog.html')

# Blog category pages
@app.route('/blog/category/<category>')
def blog_category(category):
    # For a fully functional blog, fetch articles by category
    # Since we're just demonstrating, we'll return to the main blog
    return render_template('blog.html')

# Get all symptoms for autocomplete
@app.route('/symptoms')
def get_symptoms():
    return {'symptoms': list(symptoms_dict.keys())}

# Admin messages route
@app.route('/admin/messages')
def admin_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin_messages.html', messages=messages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)