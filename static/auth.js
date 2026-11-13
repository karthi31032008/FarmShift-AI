import { initializeApp } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-app.js";

import {
    getAuth,
    GoogleAuthProvider
} from "https://www.gstatic.com/firebasejs/11.0.1/firebase-auth.js";

// Replace with your Firebase project configuration
const firebaseConfig = {
  apiKey: "AIzaSyBZgf92RYgXlbD8BsD2QV7psrfsBPUsogU",
  authDomain: "farmshift-ai.firebaseapp.com",
  projectId: "farmshift-ai",
  storageBucket: "farmshift-ai.firebasestorage.app",
  messagingSenderId: "760961979434",
  appId: "1:760961979434:web:7c5fab125e076788959f53"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Authentication
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export { app, auth, googleProvider };
