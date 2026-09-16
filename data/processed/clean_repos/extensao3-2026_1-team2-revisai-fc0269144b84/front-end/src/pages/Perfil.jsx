import { useState } from "react";
import { auth } from "../../firebase";
import { updateProfile, signOut } from "firebase/auth";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { User } from "lucide-react";

function formatMemberSince(dateString) {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("pt-BR", { month: "long", year: "numeric" });
}

export default function Perfil() {
  const user = auth.currentUser;
  const navigate = useNavigate();

  const [name, setName] = useState(user?.displayName || "");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    if (!user) return;
    setSaving(true);
    try {
      await updateProfile(user, { displayName: name });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleSignOut = async () => {
    await signOut(auth);
    navigate("/login");
  };

  const memberSince = formatMemberSince(user?.metadata?.creationTime);

  return (
    <Layout>
      <main className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold mb-1 text-gray-800">Meu Perfil</h2>
          <p className="text-sm text-gray-400 mb-6">
            Gerencie suas informações pessoais
          </p>

          {/* Informações pessoais */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm mb-6">
            <div className="px-6 pt-6 pb-2">
              <h3 className="text-base font-semibold text-gray-700">Informações pessoais</h3>
            </div>
            <div className="px-6 pb-6 space-y-5">
              {/* Avatar + nome */}
              <div className="flex items-center gap-4">
                {user?.photoURL ? (
                  <img
                    src={user.photoURL}
                    alt="avatar"
                    className="w-16 h-16 rounded-full object-cover border border-gray-100"
                  />
                ) : (
                  <div className="w-16 h-16 rounded-full bg-[#d8eddf] flex items-center justify-center">
                    <User className="w-7 h-7 text-[#2d6a4f]" />
                  </div>
                )}
                <div>
                  <p className="font-semibold text-gray-800">
                    {user?.displayName || "Usuário"}
                  </p>
                  {memberSince && (
                    <p className="text-sm text-gray-400">Membro desde {memberSince}</p>
                  )}
                </div>
              </div>

              {/* Campos */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Nome</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 bg-white focus:outline-none focus:ring-2 focus:ring-[#52b788]/40 focus:border-[#52b788] transition-all"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">E-mail</label>
                  <input
                    type="email"
                    value={user?.email || ""}
                    readOnly
                    className="w-full border border-gray-100 rounded-lg px-3 py-2 text-sm text-gray-400 bg-gray-50 cursor-not-allowed"
                  />
                </div>
              </div>

              <button
                onClick={handleSave}
                disabled={saving}
                className="px-5 py-2 bg-[#2d6a4f] text-white text-sm font-semibold rounded-lg hover:bg-[#1b4332] transition-colors disabled:opacity-60"
              >
                {saved ? "Salvo!" : saving ? "Salvando..." : "Salvar alterações"}
              </button>
            </div>
          </div>

          {/* Preferências */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm">
            <div className="px-6 pt-6 pb-2">
              <h3 className="text-base font-semibold text-gray-700">Preferências</h3>
            </div>
            <div className="px-6 pb-6 space-y-0">
              <div className="flex items-center justify-between py-3 border-b border-gray-50">
                <span className="text-sm text-gray-500">Plano atual</span>
                <span className="text-xs font-semibold bg-[#2d6a4f] text-white px-3 py-1 rounded-full">
                  Gratuito
                </span>
              </div>

              <div className="flex items-center justify-between py-3 mb-4">
                <span className="text-sm text-gray-500">Semana atual</span>
                <span className="text-sm text-gray-600 font-medium">Semana 1</span>
              </div>

              <button
                onClick={handleSignOut}
                className="w-full py-2.5 border border-gray-200 text-sm text-gray-600 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Sair da conta
              </button>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}
