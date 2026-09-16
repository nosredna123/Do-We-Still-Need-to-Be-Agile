import { initializeApp, getApps } from "firebase/app";
import { getFirestore } from "firebase/firestore";

/**
 * Configuração do Firebase Client SDK para o projeto backend-revisai-596f7.
 * Obtenha as credenciais no Firebase Console:
 *   Configurações do projeto → Apps → Web → Config
 *
 * ATENÇÃO: estas são credenciais públicas (web), diferentes do service account
 * usado no back-end. É seguro expô-las no frontend.
 */
const firebaseConfig = {
  apiKey: "AIzaSyAoNqveAoaHynA-ahIos79zAjA2S9uTDPI",
  authDomain: "backend-revisai-c75c8.firebaseapp.com",
  projectId: "backend-revisai-c75c8",
  storageBucket: "backend-revisai-c75c8.firebasestorage.app",
  messagingSenderId: "505774412473",
  appId: "1:505774412473:web:42277ea1ead61888730168",
};

// Evita re-inicialização em hot reload do Vite
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

export const db = getFirestore(app);
