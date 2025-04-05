// Firebase configuration
// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAlr8pC7jggZAb3fhIXL0vDh4ej4Mx7vQ4",
  authDomain: "gdc2025-e204b.firebaseapp.com",
  projectId: "gdc2025-e204b",
  storageBucket: "gdc2025-e204b.firebasestorage.app",
  messagingSenderId: "219904384281",
  appId: "1:219904384281:web:a728bbca4eb00e7ed13988",
  measurementId: "G-KCRYLCTHNT"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const analytics = getAnalytics(app);

export { auth }; 