"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { Navbar } from "../components/navbar";

function toLocalDatetimeInputValue(dateStringOrDate: string | Date | null): string {
  if (!dateStringOrDate) return "";
  const d = typeof dateStringOrDate === "string" ? new Date(dateStringOrDate) : dateStringOrDate;
  if (Number.isNaN(d.getTime())) return "";
  const tzOffsetMs = d.getTimezoneOffset() * 60000;
  return new Date(d.getTime() - tzOffsetMs).toISOString().slice(0, 16);
}

type Reminder = {
  id: number;
  title: string;
  description: string;
  due_date: string | null;
  isExpanded?: boolean;
};

const API_BASE = "http://localhost:8080/students";

export default function Page() {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(false);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const [selectedReminder, setSelectedReminder] = useState<Reminder | null>(null);

  const [form, setForm] = useState({
    title: "",
    description: "",
    due_date: "",
  });

  const getToken = () => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("accessToken");
  };

  const headersWithAuth = (extra?: Record<string,string>) => {
    const token = getToken();
    return {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(extra ?? {}),
    };
  };

  // carregar lembretes
  const fetchReminders = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/reminders`, {
        method: "GET",
        headers: headersWithAuth(),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Erro ao carregar lembretes: ${res.status} ${txt}`);
      }
      const data = await res.json();
      const normalized: Reminder[] = (data || []).map((r: any) => ({
        id: r.id,
        title: r.title ?? r.titulo ?? "",
        description: r.description ?? r.descricao ?? "",
        due_date: r.due_date ?? r.data ?? null,
        isExpanded: false,
      }));
      setReminders(normalized);
    } catch (err) {
      console.error("fetchReminders error:", err);
      alert((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReminders();
    
  }, []);

  const openCreateModal = () => {
    setForm({ title: "", description: "", due_date: "" });
    setShowCreateModal(true);
  };

  const openEditModal = (r: Reminder) => {
    setSelectedReminder(r);
    setForm({
      title: r.title,
      description: r.description,
      due_date: toLocalDatetimeInputValue(r.due_date),
    });
    setShowEditModal(true);
  };

  const openDeleteModal = (r: Reminder) => {
    setSelectedReminder(r);
    setShowDeleteModal(true);
  };

  const handleCreate = async () => {
    if (!form.title.trim()) return alert("Título obrigatório");
    try {
      const payload = {
        title: form.title,
        description: form.description,
        due_date: form.due_date ? new Date(form.due_date).toISOString() : undefined,
      };
      const res = await fetch(`${API_BASE}/reminders/create`, {
        method: "POST",
        headers: headersWithAuth(),
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Falha ao criar lembrete: ${res.status} ${txt}`);
      }
      const created = await res.json();
      const newRem: Reminder = {
        id: created.id ?? Date.now(),
        title: created.title ?? created.titulo ?? payload.title,
        description: created.description ?? created.descricao ?? payload.description ?? "",
        due_date: created.due_date ?? created.data ?? payload.due_date ?? null,
      };
      setReminders((s) => [newRem, ...s]);
      setShowCreateModal(false);
    } catch (err) {
      console.error("handleCreate error:", err);
      alert((err as Error).message);
    }
  };

  const handleEdit = async () => {
    if (!selectedReminder) return;
    if (!form.title.trim()) return alert("Título obrigatório");
    try {
      const payload = {
        id: selectedReminder.id,
        title: form.title,
        description: form.description,
        due_date: form.due_date ? new Date(form.due_date).toISOString() : null,
      };
      const res = await fetch(`${API_BASE}/reminders/edit`, {
        method: "PUT",
        headers: headersWithAuth(),
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Falha ao editar lembrete: ${res.status} ${txt}`);
      }
      const updated = await res.json();
      setReminders((s) =>
        s.map((r) =>
          r.id === selectedReminder.id
            ? {
                id: updated.id ?? r.id,
                title: updated.title ?? updated.titulo ?? payload.title,
                description: updated.description ?? updated.descricao ?? payload.description ?? "",
                due_date: updated.due_date ?? updated.data ?? payload.due_date,
              }
            : r,
        ),
      );
      setShowEditModal(false);
      setSelectedReminder(null);
    } catch (err) {
      console.error("handleEdit error:", err);
      alert((err as Error).message);
    }
  };

  const handleDelete = async () => {
    if (!selectedReminder) return;
    try {
      const res = await fetch(`${API_BASE}/reminders/delete?id=${selectedReminder.id}`, {
        method: "DELETE",
        headers: headersWithAuth(),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Falha ao deletar lembrete: ${res.status} ${txt}`);
      }
      setReminders((s) => s.filter((r) => r.id !== selectedReminder.id));
      setShowDeleteModal(false);
      setSelectedReminder(null);
    } catch (err) {
      console.error("handleDelete error:", err);
      alert((err as Error).message);
    }
  };

  const toggleExpand = (id: number) => {
    setReminders((s) => s.map((r) => (r.id === id ? { ...r, isExpanded: !r.isExpanded } : r)));
  };

  const formatDate = (iso: string | null) => {
    if (!iso) return "Sem data";
    const date = new Date(iso);
    return date.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
  };

  const formatTime = (iso: string | null) => {
    if (!iso) return "Sem horário";
    const date = new Date(iso);
    return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", hour12: false });
  };

  return (
    <div className="w-screen min-h-screen">
      <Navbar />
      <div className="w-screen min-h-screen bg-white pt-2 pl-8">
        <div className="font-medium text-[#686464]">
          <h1 className="text-2xl py-10 underline decoration-[#098842]/85">Lembretes</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6 pr-8">
            <div className="h-62 rounded-xl border-1 border-[#098842] border flex flex-col justify-center items-center cursor-pointer hover:bg-gray-50 gap-3" onClick={openCreateModal}>
              <button>
                <Image src="/imagens/add.svg" width={34} height={34} alt="Adicionar Lembrete" className="cursor-pointer hover:opacity-80" />
              </button>
              <span className="text-[#686464] font-medium">Adicionar Lembrete</span>
            </div>

            {loading && <div>Carregando...</div>}
            {reminders.map((reminder) => (
              <div
                key={reminder.id}
                className={`relative rounded-xl border-1 border-[#098842] p-6 flex flex-col bg-white shadow-sm cursor-pointer hover:shadow-md ${
                  reminder.isExpanded ? "h-auto" : "h-62"
                }`}
                onClick={() => toggleExpand(reminder.id)}
              >
                <div className="flex-1 overflow-hidden">
                  <div className="mb-4">
                    <h3 className="text-xl font-semibold text-[#686464] whitespace-nowrap overflow-hidden text-ellipsis pr-8">
                      {reminder.title}
                    </h3>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openEditModal(reminder);
                      }}
                      className="absolute top-3 right-3 text-[#686464] hover:text-[#098842] flex-shrink-0 ml-2 cursor-pointer z-10"
                      aria-label="Editar"
                    >
                      <Image src="/imagens/editar.svg" width={16} height={16} alt="Editar" />
                    </button>
                  </div>

                  <div className="space-y-2">
                    <div>
                      <span className="text-sm font-medium text-[#686464]">Data: </span>
                      <span className="text-sm font-normal text-[#686464]">{formatDate(reminder.due_date)}</span>
                    </div>

                    <div>
                      <span className="text-sm font-medium text-[#686464]">Horário: </span>
                      <span className="text-sm font-normal text-[#686464]">{formatTime(reminder.due_date)}</span>
                    </div>

                    {reminder.description && (
                      <div className="mt-3">
                        <span className="text-sm font-medium text-[#686464]">Descrição: </span>
                        <div className={`text-sm font-normal text-[#686464] mt-1 ${!reminder.isExpanded ? "overflow-hidden" : ""}`}>
                          {!reminder.isExpanded ? <div className="whitespace-nowrap overflow-hidden text-ellipsis">{reminder.description}</div> : <div className="whitespace-pre-wrap break-words">{reminder.description}</div>}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="absolute right-3 bottom-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openDeleteModal(reminder);
                      }}
                      className="text-[#686464] hover:text-red-600 cursor-pointer z-10"
                      aria-label="Apagar"
                    >
                      <Image src="/imagens/apagar.svg" width={16} height={16} alt="Apagar" />
                    </button>
                  </div>
                </div>
              </div>
            ))}

          </div>
        </div>
      </div>

      {/* Modal de criar lembrete */}
      {showCreateModal && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-96 shadow-lg">
            <div className="bg-[#098842] rounded-t-xl p-6">
              <div className="flex justify-between items-center">
                <div className="w-6 h-6"></div>
                <h2 className="text-xl font-semibold text-white text-center flex-1">Criar Lembrete</h2>
                <button onClick={() => setShowCreateModal(false)} className="text-white hover:text-gray-200 cursor-pointer">
                  <Image src="/imagens/X-branco.svg" width={16} height={16} alt="Fechar" />
                </button>
              </div>
            </div>

            <div className="p-6 bg-white">
              <div className="space-y-4 text-[#686464]">
                <div>
                  <label className="block text-sm font-medium mb-2">Título (obrigatório)</label>
                  <input type="text" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} className="w-full p-3 border border-gray-300 rounded-lg" placeholder="Digite o título" />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Data e Hora (opcional)</label>
                  <input type="datetime-local" value={form.due_date} onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value }))} className="w-full p-3 border border-gray-300 rounded-lg" />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Descrição</label>
                  <textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} className="w-full p-3 border border-gray-300 rounded-lg resize-none" rows={3} />
                </div>
              </div>

              <button onClick={handleCreate} className="w-full py-3 bg-[#098842] text-white rounded-lg mt-6 font-semibold hover:bg-[#098842]/90 cursor-pointer" disabled={!form.title.trim()}>
                Criar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de editar lembrete */}
      {showEditModal && selectedReminder && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-96 shadow-lg">
            <div className="bg-[#098842] rounded-t-xl p-6">
              <div className="flex justify-between items-center">
                <div className="w-6 h-6"></div>
                <h2 className="text-xl font-semibold text-white text-center flex-1">Editar Lembrete</h2>
                <button onClick={() => setShowEditModal(false)} className="text-white hover:text-gray-200 cursor-pointer">
                  <Image src="/imagens/X-branco.svg" width={16} height={16} alt="Fechar" />
                </button>
              </div>
            </div>

            <div className="p-6 bg-white">
              <div className="space-y-4 text-[#686464]">
                <div>
                  <label className="block text-sm font-medium mb-2">Título (obrigatório)</label>
                  <input type="text" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} className="w-full p-3 border border-gray-300 rounded-lg" />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Data e Hora (opcional)</label>
                  <input type="datetime-local" value={form.due_date} onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value }))} className="w-full p-3 border border-gray-300 rounded-lg" />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Descrição</label>
                  <textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} className="w-full p-3 border border-gray-300 rounded-lg resize-none" rows={3} />
                </div>
              </div>

              <button onClick={handleEdit} className="w-full py-3 bg-[#098842] text-white rounded-lg mt-6 font-semibold hover:bg-[#098842]/90 cursor-pointer" disabled={!form.title.trim()}>
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de deletar lembrete */}
      {showDeleteModal && selectedReminder && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-[640px] shadow-lg overflow-hidden">
            <div className="bg-[#098842] p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-semibold text-white">Confirmar exclusão</h2>
                <button onClick={() => setShowDeleteModal(false)} className="text-white cursor-pointer">
                  <Image src="/imagens/X-branco.svg" width={20} height={20} alt="Fechar" />
                </button>
              </div>
            </div>

            <div className="p-8">
              <p className="text-[#686464] text-center">Confirme no botão abaixo que você deseja excluir o lembrete.</p>

              <div className="flex justify-end gap-4 mt-6">
                <button onClick={handleDelete} className="px-4 py-2 rounded-md bg-[#FF6262] text-white font-semibold hover:bg-[#FF6262]/85 cursor-pointer">
                  Excluir
                </button>
                <button onClick={() => setShowDeleteModal(false)} className="px-4 py-2 rounded-md bg-[#D9D9D9] font-semibold text-[#444444] hover:bg-[#D9D9D9]/70 cursor-pointer">
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
