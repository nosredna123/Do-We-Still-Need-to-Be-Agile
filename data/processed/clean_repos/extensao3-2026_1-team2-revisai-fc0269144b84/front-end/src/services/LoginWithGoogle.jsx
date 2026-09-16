import { auth } from "../../firebase";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";


export async function LoginWithGoogle() {
    const provider = new GoogleAuthProvider();

    provider.setCustomParameters({
      prompt: "select_account"
    
    });

    try {
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      console.log("Usuário logado:", user);
      return user;
  
    } catch (error) {
      console.error("Erro ao fazer login com Google:", error);
      throw error;
    }
  
}