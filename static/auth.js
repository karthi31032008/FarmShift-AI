
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-app.js";

import {
    getAuth,
    GoogleAuthProvider
} from "https://www.gstatic.com/firebasejs/11.0.1/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyBZgf92RYgXlbD8BsD2QV7psrfsBPUsogU",
  authDomain: "farmshift-ai.firebaseapp.com",
  projectId: "farmshift-ai",
  storageBucket: "farmshift-ai.firebasestorage.app",
  messagingSenderId: "760961979434",
  appId: "1:760961979434:web:7c5fab125e076788959f53"
};

const app = initializeApp(firebaseConfig);

const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export { app, auth, googleProvider };
