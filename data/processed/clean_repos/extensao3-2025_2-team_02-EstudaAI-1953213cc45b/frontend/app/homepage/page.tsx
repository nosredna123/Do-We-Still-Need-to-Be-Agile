"use client";
import { Navbar } from "../components/navbar";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";


type Disciplina = {
  id: number,
  name: string,
  userId: number
}
const disciplinasIniciais = [
  { id: "estrutura-de-dados", nome: "Estrutura de Dados" },
  { id: "poo", nome: "Programação Orientada a Objetos" },
  { id: "aps", nome: "Análise e Projeto de Software" },
  { id: "algebra-linear", nome: "Álgebra Linear" }
];

export default function HomePage() {
  const router = useRouter();
  const [disciplinas, setDisciplinas] = useState<Disciplina[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [novaDisciplina, setNovaDisciplina] = useState("");

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [disciplinaToDelete, setDisciplinaToDelete] = useState<Disciplina | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  async function createSubject() {
    try {
      const response = await fetch("http://localhost:8080/students/subjects/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
        },
        body: JSON.stringify({ name: novaDisciplina }),
      });

      if (!response.ok) {
        const text = await response.text();
        console.error("Erro ao criar disciplina:", text || response.status);
        return;
      }

      const data = await response.json();

      setDisciplinas((prev) => [...prev, data]);

      setNovaDisciplina("");
      setShowModal(false);
      router.push(`grupos/${data.id}?nomeDisciplina=${data.name}`)
    } catch (err) {
      console.error("Erro ao criar disciplina:", err);
    }
  }

  useEffect(() => {
    async function fetchUser() {
      try {
        const response = await fetch("http://localhost:8080/students/subjects", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          },
        });

        if (!response.ok) {
          const text = await response.text();
          console.error("Erro ao buscar disciplinas:", text || response.status);
          return;
        }

        const data = await response.json();
        setDisciplinas(data)
        console.log("User:", data);
      } catch (err) {
        console.error("Erro ao buscar disciplinas:", err);
      }
    }

    fetchUser();
  }, []);

  const handleLogout = () => {
    try {
      localStorage.removeItem("accessToken");
    } catch (e) {
      console.warn("Erro ao remover token:", e);
    }

    router.push("/");
  };

  const openDeleteModal = (d: Disciplina) => {
    setDisciplinaToDelete(d);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!disciplinaToDelete) return;
    setIsDeleting(true);

    try {
      const url = `http://localhost:8080/students/subject/delete?subjectId=${disciplinaToDelete.id}`;

      const res = await fetch(url, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
        }
      });

      if (!res.ok) {
        const text = await res.text();
        console.error("Erro ao deletar disciplina:", text);
        alert("Erro ao deletar disciplina:\n" + text);
        setIsDeleting(false);
        return;
      }

      setDisciplinas(prev => prev.filter(d => d.id !== disciplinaToDelete.id));
      setShowDeleteModal(false);
      setDisciplinaToDelete(null);

    } catch (err) {
        console.error("Erro ao deletar:", err);
        alert("Erro ao deletar disciplina. Veja o console.");
    } finally {
        setIsDeleting(false);
    }
  };


  return (
    <div className="w-screen min-h-screen">
      <Navbar />
      <div className="flex min-w-screen min-h-screen bg-white text-[#494949]">
        <div className="w-72 bg-[#C2DFC0] border-r border-[#098842] drop-shadow h-screen p-6 flex flex-col">
          <div className="mb-8">
            <h1 className="text-2xl font-normal text-center">Disciplinas</h1>
          </div>

          <div className="overflow-y-auto pr-2 flex-1" style={{ maxHeight: 'calc(100vh - 280px)' }}>
            <nav className="space-y-4">
              {disciplinas.map((disciplina) => (
                <div key={disciplina.id} className="relative">
                  <Link
                    href={`/grupos/${disciplina.id}?nomeDisciplina=${disciplina.name}`}
                    className="block p-3 bg-[#098842] text-white hover:bg-white hover:text-[#098842] rounded-xl whitespace-nowrap overflow-hidden text-ellipsis pr-12"
                  >
                    {disciplina.name}
                  </Link>

                  <button
                    aria-label={`Apagar ${disciplina.name}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      e.preventDefault();
                      openDeleteModal(disciplina);
                    }}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1 bg-white rounded-md hover:bg-gray-100 cursor-pointer"
                    title="Apagar disciplina"
                  >
                    <Image src="/imagens/apagar.svg" width={18} height={18} alt="Apagar" />
                  </button>
                </div>
              ))}
            </nav>
          </div>

          <div className="mt-6">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 p-3 w-1/2 border border-[#098842] bg-[#F5F5F5] hover:text-red-600 rounded-xl cursor-pointer"
            >
              <Image
                src="/imagens/sair.svg"
                width={20}
                height={20}
                alt="Sair"
              />
              <span>Logout</span>
            </button>
          </div>
        </div>

        <div className="flex-1 flex flex-col items-center justify-center">
          <div className="text-center">
            <div className="mb-4">
              <Image
                src="/imagens/livro.svg"
                width={200}
                height={200}
                alt="Livro"
                className="mx-auto"
              />
            </div>

            <button
              onClick={() => setShowModal(true)}
              className="mb-4 cursor-pointer hover:opacity-80"
            >
              <Image
                src="/imagens/add.svg"
                width={40}
                height={40}
                alt="Adicionar Disciplina"
                className="mx-auto"
              />
            </button>
            <p className="text-xl">Adicionar Disciplina</p>
          </div>
        </div>

        {showModal && (
          <div className="fixed inset-0 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl w-96 shadow-lg">
              <div className="bg-[#098842] rounded-t-xl p-6">
                <div className="flex justify-between items-center">
                  <div className="w-6 h-6"></div>

                  <h2 className="text-xl font-semibold text-white text-center flex-1">
                    Criar Disciplina
                  </h2>

                  <button
                    onClick={() => setShowModal(false)}
                  >
                    <Image
                      src="/imagens/X-branco.svg"
                      width={16}
                      height={16}
                      alt="Fechar"
                    />
                  </button>
                </div>
              </div>

              <div className="p-6">
                <div className="mb-6">
                  <input
                    type="text"
                    value={novaDisciplina}
                    onChange={(e) => setNovaDisciplina(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg text-black focus:outline-none focus:ring-2 focus:ring-[#098842] focus:border-transparent"
                    placeholder="Digite o nome da disciplina"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && novaDisciplina.trim()) {
                        createSubject();
                      }
                    }}
                  />
                </div>

                <button
                  onClick={createSubject}
                  className="w-full py-3 bg-[#098842] text-white rounded-lg hover:bg-[#098842]/90 font-medium"
                  disabled={!novaDisciplina.trim()}
                >
                  Criar Disciplina
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modal de confirmação de exclusão de disciplina */}
      {showDeleteModal && disciplinaToDelete && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-[640px] shadow-lg overflow-hidden">
            <div className="bg-[#098842] p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-semibold text-white">Confirmar exclusão</h2>
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setDisciplinaToDelete(null);
                  }}
                  className="text-white cursor-pointer"
                >
                  <Image src="/imagens/X-branco.svg" width={20} height={20} alt="Fechar" />
                </button>
              </div>
            </div>

            <div className="p-8">
              <p className="text-[#686464] text-center">
                Confirme no botão abaixo que você deseja excluir a disciplina.
              </p>

              <div className="flex justify-end gap-4 mt-6">
                <button
                  onClick={confirmDelete}
                  className="px-4 py-2 rounded-md bg-[#FF6262] text-white font-semibold hover:bg-[#FF6262]/85 cursor-pointer"
                  disabled={isDeleting}
                >
                  {isDeleting ? "Excluindo..." : "Excluir"}
                </button>
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setDisciplinaToDelete(null);
                  }}
                  className="px-4 py-2 rounded-md bg-[#D9D9D9] font-semibold text-[#444444] hover:bg-[#D9D9D9]/70 cursor-pointer"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}