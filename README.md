
# 🎓 Kids Support Foundation

**Empowering Underprivileged Kids through Donations, Mentorship, and AI-Powered Support**

[Home Page] ![Screenshot (139)](https://github.com/user-attachments/assets/240c0d66-5e2e-482e-87f2-0daf998a24cb)



---

## 🌟 Features

🔗 **Connects Students with Donors**  
- Students in need can create profiles and request financial aid.  
- Verified donors can browse these requests and directly support causes they resonate with.

👥 **Enables Mentorship & Guidance**  
- Donors or volunteers can sign up as mentors.  
- Students can initiate a Mentor Connect request to schedule chats or video meets for career, academic, or personal guidance.

🤖 **24/7 AI-Powered Assistant**  
Integrated with Google’s Gemini API, our intelligent chatbot helps students:  
- Understand the application process  
- Get answers to career and learning-related queries  
- Acts as a virtual advisor, ensuring no student is left unheard  

🗺️ **Map-Based Recipient Identification**  
- Locates and connects donors with nearby recipients using geolocation.

📄 **Document Verification**  
- Ensures authenticity by verifying ID, income, and education documents.

🎯 **Personalized Support**  
- Matches donors with recipients based on proximity and specific needs.

🔍 **Transparency**  
- Tracks request statuses and document approvals in real-time.

📈 **Scalability**  
- Supports rural and low-income students with tailored assistance.

---

## 📸 Screenshots

### 🧾 Donor Dashboard  
[Donor Dashboard]![Screenshot (122)](https://github.com/user-attachments/assets/c2183b12-9502-4dc5-97d7-b8adba12b295)



### 🎓 Mentorship Dashboard  
[Mentor Dashboard]![Screenshot (128)](https://github.com/user-attachments/assets/86257c41-0428-4adb-851c-2b511604ebc3)


### 📍 Nearby Students (Geolocation)  
[Nearby Students]![Screenshot (136)](https://github.com/user-attachments/assets/79d4409c-f5b7-471d-aaa4-0d7642549263)


### 🧒 Student Profile Dashboard  
[Student Dashboard]![Screenshot (129)](https://github.com/user-attachments/assets/1b9c2d81-e63b-40d5-8d16-0c41c84bbc06)


---

## 🛠️ Tech Stack

### 💻 Frontend

- **Django Templates + Widget Tweaks**  
  Enables server-side rendering of HTML pages.  
  `django-widget-tweaks` simplifies form customization and styling.  
  User-friendly UI for students, donors, and mentors.

### ⚙️ Backend

- **Django**  
  Handles routing, business logic, and user authentication.  
- **Django REST Framework** *(optional)*  
  Can be used to create APIs for mobile or decoupled frontends.  
- **Gunicorn + Whitenoise**  
  Gunicorn = WSGI server, Whitenoise = static file manager for smooth deployment.

### 🧠 AI Assistant Integration

- **Gemini API** (`google-generativeai`)  
  Powers the AI chatbot that answers student queries.

### 🔐 Authentication & Realtime Services

- **Firebase Admin SDK** (`firebase-admin`)  
  Secure user authentication via email/password or social login.  
- **Geopy** (`geopy==2.3.0`)  
  Enables donors to filter and find students by location.

### 🗃️ Database

- **PostgreSQL** with `psycopg2-binary`

### 🌍 Hosting

- **Heroku**  
  Combines Heroku + PostgreSQL + Firebase for scalability and security.

### 📦 Other Utilities

- `requests`, `urllib3`, `certifi` – for external APIs and secure HTTP connections.

---

## 🚀 Important Commands

### ⚙️ Create Admin

```bash
py manage.py createsuperuser
```

---

## 🧪 How to Run This Project

1. **Install Python 3.7.6**  
   ⚠️ *Don’t forget to tick "Add to PATH" during installation*

2. **Download this project (ZIP) and extract it**

3. **Open terminal inside the project folder and run:**

```bash
python -m pip install -r requirements.txt
py manage.py makemigrations
py manage.py migrate
py manage.py runserver
```

4. **Open the app in your browser**  
   Go to:  
   ```
   http://127.0.0.1:8000/
   ```

---

## 🤝 Contribution

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 🧠 Inspiration

Built with the vision to break educational inequality and offer a helping hand — not just a helping fund.

---

⭐ **Give this repo a star if you believe in the cause!**
