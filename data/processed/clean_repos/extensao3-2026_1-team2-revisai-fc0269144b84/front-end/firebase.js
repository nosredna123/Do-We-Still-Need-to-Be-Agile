// ARQUIVO DE CONGFIGURAÇÃO DO FIREBASE

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth} from "firebase/auth";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries


// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAyL0ldr2QqQ2ZxDspdjd_pdZE_NT0hnUk",
  authDomain: "backend-revisai-596f7.firebaseapp.com",
  projectId: "backend-revisai-596f7",
  storageBucket: "backend-revisai-596f7.firebasestorage.app",
  messagingSenderId: "816988929709",
  appId: "1:816988929709:web:e9535e77c1edee2b3d5024"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
