import streamlit as st
from PIL import Image
import google.generativeai as genai
import urllib.parse
from datetime import timedelta, date


# ----------------- Configure Gemini API -------------------
genai.configure(api_key="AIzaSyDL2k9_deJ-3Cs0AVB57PqjHZjtHoEvvZo")
model = genai.GenerativeModel("models/gemini-1.5-flash")

# ----------------- Streamlit Page Config ------------------
st.set_page_config(page_title="🐶 Pet Health Assistant", layout="wide")

st.sidebar.title("🐾 Pet Health Assistant")
page = st.sidebar.radio("Go to Section", [
    "1️⃣ Welcome",
    "2️⃣ Pet Details & Image Analysis",
    "3️⃣ Pet Vaccination Tracker",
    "4️⃣ Pet Diet Recommendation Based on Health Conditions",
    "5️⃣ Deworming Assistant"
])

# ----------------- Sidebar Pet Details ------------------
with st.sidebar.form("sidebar_pet_details"):
    st.markdown("### 📝 Add More Pet Details ")

    pet_name = st.text_input("Pet Name")
    
    pet_type = st.selectbox("Pet Type", ["Dog", "Cat", "Rabbit", "Bird", "Hamster", "Other"])
    if pet_type == "Other":
        pet_type_custom = st.text_input("Please specify your pet type")
        final_pet_type = pet_type_custom if pet_type_custom else "Other"
    else:
        final_pet_type = pet_type

    pet_age = st.number_input("Pet Age (in years)", min_value=0.0, step=0.1)
    pet_gender = st.selectbox("Gender", ["Male", "Female", "Unknown"])
    pet_breed = st.text_input("Breed (optional)")

    save = st.form_submit_button("Save Details")
    if save:
        st.sidebar.success(f"Details Saved for {pet_name} 🐾")

        # ✅ Use a different key that doesn't conflict with the form ID
        st.session_state['saved_pet_details'] = {
            "pet_name": pet_name,
            "pet_type": final_pet_type,
            "pet_age": pet_age,
            "pet_gender": pet_gender,
            "pet_breed": pet_breed
        }


# ----------------- Welcome Section ------------------
if page == "1️⃣ Welcome":
    st.markdown("<h1 style='text-align: center;'>🐶 Pet Health Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Welcome to the Virtual Vet Assistant. How can I help you today?</p>", unsafe_allow_html=True)


#----------------- Session Setup ------------------
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "analysis" not in st.session_state:
    st.session_state.analysis = ""

# ----------------- Upload Pet Photo + Symptom Checker ------------------


if page == "2️⃣ Pet Details & Image Analysis":
    st.subheader("📸 Pet Image & Symptom Analysis")

with st.form("pet_analysis_form"):
    uploaded_file = st.file_uploader("Upload a picture of your dog or cat", type=["jpg", "jpeg", "png"])
    symptom_description = st.text_area("Describe any symptoms or behaviors you've noticed (e.g., vomiting, not eating, sluggish, etc.)")
    analyze_btn = st.form_submit_button("🔍 Analyze Pet Health")

if analyze_btn:
    if uploaded_file is None:
        st.warning("⚠️ Please upload an image of your pet.")
    elif not symptom_description.strip():
        st.warning("⚠️ Please describe your pet's symptoms.")
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Pet", use_column_width=True)

        with st.spinner("Analyzing your pet's image and symptoms..."):

            # 🐾 Add pet details to prompt
            pet_intro = ""
            if pet_name:
                pet_intro += f"The pet's name is {pet_name}. "
            if pet_age:
                pet_intro += f"{pet_name} is {pet_age} years old. "
            if pet_gender != "Unknown":
                pet_intro += f"{pet_name} is a {pet_gender.lower()}. "
            if pet_breed:
                pet_intro += f"The breed is {pet_breed}. "

            prompt = (
                f"You are a pet health assistant. {pet_intro}"
                "Analyze this pet's image and the following symptoms:\n\n"
                f"Symptoms: {symptom_description}\n\n"
                "Please describe:\n"
                "- Any visible signs of good or poor health (coat, eyes, posture)\n"
                "- Possible causes for described symptoms\n"
                "- Friendly advice for next steps or home care\n"
                "Keep it short, helpful, and caring."
            )

            try:
                response = model.generate_content([prompt, image])
                analysis = response.text
                st.session_state.analysis = analysis

                st.session_state.chat_session = model.start_chat(history=[
                    {"role": "user", "parts": [prompt, image]},
                    {"role": "model", "parts": [analysis]}
                ])

                st.subheader("🩺 AI Health Analysis")
                st.markdown(analysis)

            except Exception as e:
                st.error(f"Error during analysis: {e}")

# Initialize vaccinations with interval (in days)
if "vaccinations" not in st.session_state:
    st.session_state.vaccinations = {
        "Dog": {
            "Rabies": {"interval": 365},
            "DHPP (5-in-1 combo)": {"interval": 1095},
            "Bordetella (Kennel Cough)": {"interval": 180},
            "Leptospirosis": {"interval": 365},
            "Lyme Disease": {"interval": 365},
            "Canine Influenza": {"interval": 365},
            "Coronavirus": {"interval": 365}
        },
        "Cat": {
            "Rabies": {"interval": 365},
            "FVRCP (Combo)": {"interval": 1095},
            "Feline Leukemia (FeLV)": {"interval": 365},
            "Chlamydia felis": {"interval": 365},
            "FIV": {"interval": 365},
            "Bordetella": {"interval": 180}
        },
        "Rabbit": {
            "Myxomatosis + RHDV (Combo)": {"interval": 365},
            "RHDV1": {"interval": 365},
            "RHDV2": {"interval": 365}
        }
    }

# Store records separately
if "records" not in st.session_state:
    st.session_state.records = {
        "Dog": {},
        "Cat": {},
        "Rabbit": {}
    }

page = "3️⃣ Pet Vaccination Tracker"  # simulate your page switch (replace with your real logic)


if page == "3️⃣ Pet Vaccination Tracker":
    st.markdown("### 💉 Pet Vaccination Tracker")


    # 🐶 Choose pet type
    pet_type = st.selectbox("Select your pet type", ["Dog", "Cat", "Rabbit"])

# 🐾 Show vaccine list
st.markdown(f"#### {pet_type} Vaccines")
for vac in st.session_state.vaccinations[pet_type]:
    status = st.session_state.records[pet_type].get(vac, {}).get("status", "Not recorded")
    date_given = st.session_state.records[pet_type].get(vac, {}).get("date", "—")
    st.markdown(f"- **{vac}**: {status} (📅 {date_given})")

# ✍️ Add or update vaccination record
with st.expander("➕ Add or Update Vaccination Record"):
    vaccine_name = st.selectbox("Select Vaccine", list(st.session_state.vaccinations[pet_type].keys()))
    vaccine_status = st.selectbox("Status", ["Done", "Due"])
    vaccine_date = st.date_input("Date (e.g. given or due)", date.today())

    def calculate_next_vaccine_date(vaccine_name, vaccine_date):
        interval_days = st.session_state.vaccinations[pet_type][vaccine_name]["interval"]
        return vaccine_date + timedelta(days=interval_days)

    if st.button("💾 Save Record"):
        next_vaccine_date = calculate_next_vaccine_date(vaccine_name, vaccine_date)
        st.session_state.records[pet_type][vaccine_name] = {
            "status": vaccine_status,
            "date": vaccine_date.strftime("%b %d, %Y"),
            "next_due": next_vaccine_date.strftime("%b %d, %Y")
        }
        st.success(f"{vaccine_name} record saved! Next dose expected by **{next_vaccine_date.strftime('%b %d, %Y')}**.")




###########DIET
import streamlit as st

# Dog Breeds List
dog_breeds = [
    "Labrador Retriever", "German Shepherd", "Golden Retriever", "French Bulldog", "Bulldog",
    "Poodle", "Beagle", "Rottweiler", "Yorkshire Terrier", "Boxer", "Dachshund", "Great Dane",
    "Siberian Husky", "Doberman Pinscher", "Australian Shepherd", "Shih Tzu", "Pomeranian",
    "Chihuahua", "Cocker Spaniel", "Border Collie", "Maltese", "Boston Terrier", "Bichon Frise",
    "Akita", "Pug", "Cane Corso", "Saint Bernard", "Bernese Mountain Dog", "English Springer Spaniel",
    "Miniature Schnauzer", "Havanese", "Collie", "Weimaraner", "Newfoundland", "West Highland White Terrier",
    "Bullmastiff", "Cavalier King Charles Spaniel", "Alaskan Malamute", "Papillon", "Basenji",
    "Whippet", "Samoyed", "Vizsla", "Tibetan Terrier", "Lhasa Apso", "Irish Setter", "Afghan Hound",
    "American Staffordshire Terrier", "Scottish Terrier"
]

# Health Conditions List
health_issues = [
    "Obesity / Overweight", "Diabetes", "Kidney Disease", "Heart Problems",
    "Allergies (e.g., Grain, Chicken, Dairy)", "Sensitive Stomach", "Dental Issues",
    "Skin/Fur Problems", "Arthritis", "Urinary Issues", "Pregnant/Nursing", "No known issues"
]
st.markdown("### 🐾 Get Diet Recommendation")  # This is the heading you want

# --- Pet Profile Form ---
with st.expander("📋 Fill Out Pet Profile"):
    pet_type = st.selectbox("Pet Type", ["Dog", "Cat", "Rabbit"])

    if pet_type == "Dog":
        breed = st.selectbox("Breed", dog_breeds)
    else:
        breed = st.text_input("Breed")

    age = st.number_input("Age (years)", min_value=0.0, step=0.5)
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
    gender = st.radio("Gender", ["Male", "Female"])
    activity_level = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
    neutered_spayed = st.radio("Neutered/Spayed", ["Yes", "No"])

    selected_issues = st.multiselect("❤️ Health Conditions", health_issues)
    other_health_notes = st.text_area("📝 Describe other health conditions (optional)")

    if st.button("🍽️ Get Diet Recommendation"):
        # Prepare prompt for dietary analysis
        diet_prompt = (
            f"You are a pet nutritionist. Suggest a diet plan for a {breed} "
            f"that has the following health condition: {', '.join(selected_issues) if selected_issues else 'No known issues'}. "
            f"Include recommended food types, feeding frequency, and any important notes or restrictions. "
            f"Make it easy to understand and friendly for a pet owner."
        )

        try:
            with st.spinner("Generating diet recommendations..."):
                diet_response = model.generate_content(diet_prompt)
                st.subheader("📋 Diet Recommendation")
                st.markdown(diet_response.text)
        except Exception as e:
            st.error(f"Could not fetch diet recommendation: {e}")

# For the page navigation
page = st.sidebar.selectbox("Select Page", ["1️⃣ Welcome", "2️⃣ Pet Details & Image Analysis", "3️⃣ Pet Vaccination Tracker", "4️⃣ Pet Diet Recommendation Based on Health Conditions"])

if page == "4️⃣ Pet Diet Recommendation Based on Health Conditions":
    st.markdown("### 🥗 Pet Diet Recommendation Based on Health Conditions")

    # Display the pet profile form here again for context (optional, depending on how you want to structure the UI)
    with st.expander("📋 Fill Out Pet Profile"):
        # Reusing the same form as above to capture pet details again
        pet_type = st.selectbox("Pet Type", ["Dog", "Cat", "Rabbit"])

        if pet_type == "Dog":
            breed = st.selectbox("Breed", dog_breeds)
        else:
            breed = st.text_input("Breed")

        age = st.number_input("Age (years)", min_value=0.0, step=0.5)
        weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
        gender = st.radio("Gender", ["Male", "Female"])
        activity_level = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
        neutered_spayed = st.radio("Neutered/Spayed", ["Yes", "No"])

        selected_issues = st.multiselect("❤️ Health Conditions", health_issues)
        other_health_notes = st.text_area("📝 Describe other health conditions (optional)")

        if st.button("🍽️ Get Diet Recommendation"):
            # Prepare prompt for dietary analysis
            diet_prompt = (
                f"You are a pet nutritionist. Suggest a diet plan for a {breed} "
                f"that has the following health condition: {', '.join(selected_issues) if selected_issues else 'No known issues'}. "
                f"Include recommended food types, feeding frequency, and any important notes or restrictions. "
                f"Make it easy to understand and friendly for a pet owner."
            )

            try:
                with st.spinner("Generating diet recommendations..."):
                    diet_response = model.generate_content(diet_prompt)
                    st.subheader("📋 Diet Recommendation")
                    st.markdown(diet_response.text)
            except Exception as e:
                st.error(f"Could not fetch diet recommendation: {e}")


###########DIET


import streamlit as st
import google.generativeai as genai
import datetime

# Configure Gemini API

# App Title
st.markdown("🐾 Pet Deworming Assistant")

# Sidebar Navigation
page = st.sidebar.radio("Go to", [
    "1️⃣ Educational Section",
    "2️⃣ Symptom Checker",
    "3️⃣ Smart Suggestion Engine",
    "4️⃣ My Pet’s Diary & Reminder",
    "5️⃣ Ask Gemini AI"
])

# ------------------- 1. Educational Section -------------------
if page == "1️⃣ Educational Section":
    st.header("📘 What is Deworming?")
    st.markdown("""
    Deworming is the process of removing internal parasites like roundworms, tapeworms, and hookworms from your pet's body.

    **Why it's important:** Worms can cause health issues like weight loss, vomiting, anemia, and even death.

    **Types of Worms:** 
    - 🌀 Roundworms
    - 📏 Tapeworms
    - 🩸 Hookworms
    - 🌫 Lungworms

    **Symptoms of Infection:** 
    - Worms in poop
    - Scooting
    - Vomiting/diarrhea
    - Bloated belly
    - Weight loss

    **Deworming Frequency:**
    - Puppies & Kittens: Every 2 weeks until 12 weeks old
    - Adult Pets: Every 3 months
    """)

# ------------------- 2. Interactive Q&A -------------------
elif page == "2️⃣ Symptom Checker":
    st.header("🩺 Symptom Checker")

    pet_type = st.selectbox("What kind of pet do you have?", ["Dog", "Cat", "Rabbit", "Other"])
    age = st.slider("Pet’s Age (in months)", 0, 120)
    weight = st.number_input("Pet’s Weight (kg)", min_value=0.1)
    living = st.radio("Is your pet indoor or outdoor?", ["Indoor", "Outdoor", "Both"])
    dewormed_before = st.radio("Has your pet ever been dewormed?", ["Yes", "No"])

    symptoms = st.multiselect("Select symptoms your pet has:", [
        "Visible worms in poop or around anus",
        "Scooting behavior",
        "Vomiting or diarrhea",
        "Bloated belly",
        "Weight loss",
        "Coughing",
        "Loss of appetite or energy"
    ])

    if st.button("🔍 Check Symptoms"):
        st.session_state['symptom_result'] = {
            "pet_type": pet_type,
            "age": age,
            "symptoms": symptoms,
            "dewormed": dewormed_before
        }
        st.success("Saved! Go to 'Smart Suggestion Engine'")

# ------------------- 3. Suggestion Engine -------------------
elif page == "3️⃣ Smart Suggestion Engine":
    st.header("📊 Deworming Suggestion")

    import google.generativeai as genai

    genai.configure(api_key="AIzaSyDL2k9_deJ-3Cs0AVB57PqjHZjtHoEvvZo")
    model = genai.GenerativeModel("models/gemini-1.5-flash")

    data = st.session_state.get('symptom_result', None)

    if data:
        # Let user ask a question
        user_question = st.text_input("💬 Ask Gemini about deworming medicine or schedule:")

        if user_question:
            prompt = f"""
            You are a veterinary expert helping a pet owner with deworming advice.

            The pet owner provided the following information:
            - Pet Type: {data['pet_type']}
            - Age: {data['age']} months
            - Weight: {data.get('weight', 'not specified')} kg
            - Living environment: {data.get('living', 'not specified')}
            - Symptoms: {", ".join(data['symptoms']) if data['symptoms'] else 'None'}
            - Previously dewormed: {data['dewormed']}

            Based on this, answer the following question in simple words:
            {user_question}
            """

            response = model.generate_content(prompt)
            st.markdown("### 🧠 Gemini's Answer")
            st.write(response.text)
    else:
        st.info("⚠️ Please complete the Symptom Checker first to ask Gemini questions.")

# ------------------- 4. Diary & Reminder -------------------
import streamlit as st
import datetime

# Check which page is selected
if page == "4️⃣ My Pet’s Diary & Reminder":
    st.header("📒 Pet’s Health Diary")

    # Basic Pet Details
    pet_name = st.text_input("🐶 Pet Name")
    pet_type = st.selectbox("🐾 Pet Type", ["Dog", "Cat"])
    dob = st.date_input("📅 Date of Birth (Approx)")
    last_deworm = st.date_input("💊 Last Deworming Date")

    # Calculate Pet Age
    today = datetime.date.today()
    age_in_days = (today - dob).days
    age_in_months = age_in_days // 30

    # Decide next deworming interval based on age
    if age_in_days < 84:  # Less than 12 weeks
        interval_days = 14
        schedule_info = "Every 2 weeks (for pets under 3 months)"
    elif age_in_months < 6:
        interval_days = 30
        schedule_info = "Every month (for pets 3–6 months old)"
    else:
        interval_days = 90
        schedule_info = "Every 3 months (for pets above 6 months)"

    # Calculate next deworming date
    reminder_date = last_deworm + datetime.timedelta(days=interval_days)

    # Save Button
    if st.button("📅 Save & Set Reminder"):
        st.success(f"Reminder set! Next deworming due on **{reminder_date.strftime('%Y-%m-%d')}**")
        st.info(f"🗓 Schedule: {schedule_info}")

    # Educational Info Section
    with st.expander("🧠 Learn About Deworming Types"):
        st.markdown("""
        **Common Types of Worms in Pets:**
        - 🌀 **Roundworms** – Common in puppies and kittens.
        - ⚓ **Hookworms** – Can cause anemia, especially dangerous for young animals.
        - 🧩 **Tapeworms** – Often transmitted by fleas.
        - 🧷 **Whipworms** – Typically affect dogs and can cause diarrhea.
        - ❤️ **Heartworms** – Spread by mosquitoes; require monthly preventives.

        **Deworming Medicines:**
        - Albendazole
        - Fenbendazole
        - Pyrantel pamoate
        - Praziquantel

        ⚠️ Always consult a vet before choosing a medicine.
        """)

# ------------------- 5. Ask Gemini AI -------------------
elif page == "5️⃣ Ask Gemini AI":
    st.header("🤖 Ask Gemini Anything About Pet Deworming")
    user_question = st.text_area("Type your question here:")

    if st.button("💬 Ask"):
        if user_question.strip():
            response = model.generate_content(user_question)
            st.markdown(f"**Gemini AI:** {response.text}")
        else:
            st.warning("Please type a question.")




# --------------- Chat Section -------------------
import urllib.parse

# --- State setup ---
if "location_asked" not in st.session_state:
    st.session_state.location_asked = False
if "user_location" not in st.session_state:
    st.session_state.user_location = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "latest_response" not in st.session_state:
    st.session_state.latest_response = None

# --- Chat Input Box at Bottom ---
user_input = st.chat_input("Ask about your pet, care tips, or nearby pet clinics...")

# --- Process Input ---
if user_input:
    st.session_state.chat_history.append(("user", user_input))

    # Check if it's a location-related query
    location_keywords = ["clinic", "hospital", "vet", "near me", "nearby", "where"]
    is_location_query = any(keyword in user_input.lower() for keyword in location_keywords)

    if is_location_query:
        # Extract location using Gemini
        location_prompt = (
            "Extract the **precise location** (like area, city, and country) from this sentence:\n"
            f"\"{user_input}\"\n"
            "Return only the location, for example: 'Commercial Market, Rawalpindi, Pakistan'"
        )
        location_response = model.generate_content(location_prompt)
        extracted_location = location_response.text.strip().strip('"')

        if extracted_location:
            st.session_state.user_location = extracted_location
            st.session_state.location_asked = True

            query = urllib.parse.quote(f"pet clinics near {extracted_location}")
            maps_url = f"https://www.google.com/maps/search/{query}"

            response = (
                f"📍 I found your location as **{extracted_location}**.\n\n"
                f"Here are some nearby pet clinics you can explore:\n"
                f"[🔍 View on Google Maps]({maps_url})\n\n"
                "Let me know if you'd like help with anything else!"
            )
        else:
            response = "Sorry, I couldn't understand the location. Can you rephrase it more clearly?"
    else:
        # --- Get saved pet details from session ---
        pet_info = st.session_state.get("saved_pet_details", None)

        pet_intro = ""
        if pet_info:
            name = pet_info.get("pet_name", "your pet")
            pet_intro += f"The pet's name is {name}. "
            if pet_info.get("pet_age"):
                pet_intro += f"{name} is {pet_info['pet_age']} years old. "
            if pet_info.get("pet_gender") and pet_info["pet_gender"] != "Unknown":
                pet_intro += f"{name} is a {pet_info['pet_gender'].lower()}. "
            if pet_info.get("pet_breed"):
                pet_intro += f"The breed is {pet_info['pet_breed']}. "
        else:
            name = "your pet"

        # --- Build prompt with pet context ---
        general_prompt = f"""
        You are a smart and caring pet assistant. {pet_intro}
        Now answer this user question with clear, gentle, and helpful advice:

        Question: {user_input}
        """

        gemini_general = model.generate_content(general_prompt)
        response = gemini_general.text.strip()

    # Store latest assistant response
    st.session_state.latest_response = response
    st.session_state.chat_history.append(("assistant", response))

# --- Show full chat history (except last response) ---
for role, message in st.session_state.chat_history[:-1]:
    with st.chat_message(role):
        st.markdown(message)

# --- Show latest response at the very bottom ---
if st.session_state.latest_response:
    with st.chat_message("assistant"):
        st.markdown(st.session_state.latest_response)
