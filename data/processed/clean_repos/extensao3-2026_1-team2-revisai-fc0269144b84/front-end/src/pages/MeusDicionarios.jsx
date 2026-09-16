import { useState, useRef, useEffect } from "react";
import Layout from "../components/Layout";
import { BookOpen, Trash2, X, Pencil, Check } from "lucide-react";
import { useFlashcards } from "../contexts/FlashcardContext";

export default function MeusDicionarios() {
  const { dicionarios, updateDicionario, removeDicionario } = useFlashcards();
  const [selectedDicionario, setSelectedDicionario] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [editingDicionario, setEditingDicionario] = useState(null);
  const [editTopic, setEditTopic] = useState("");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const modalRef = useRef(null);

  // Click-outside to close view modal
  useEffect(() => {
    if (!selectedDicionario) return;
    const handleClick = (e) => {
      if (modalRef.current && !modalRef.current.contains(e.target)) {
        setSelectedDicionario(null);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [selectedDicionario]);

  const handleStartEdit = (e, dicionario) => {
    e.stopPropagation();
    setEditingDicionario(dicionario);
    setEditTopic(dicionario.topic);
  };

  const handleSaveEdit = async () => {
    if (!editTopic.trim() || editTopic === editingDicionario.topic) {
      setEditingDicionario(null);
      return;
    }
    setSaving(true);
    try {
      await updateDicionario(editingDicionario.id, editTopic.trim());
      setEditingDicionario(null);
    } catch (err) {
      console.error("Erro ao editar dicionário:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!confirmDeleteId) return;
    setDeleting(true);
    try {
      await removeDicionario(confirmDeleteId);
      setConfirmDeleteId(null);
    } catch (err) {
      console.error("Erro ao excluir dicionário:", err);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <Layout>
      <main className="flex-1 overflow-auto p-6">
        <div className="max-w-5xl mx-auto animate-fade-in">
          <h2 className="text-2xl font-bold mb-1">Meus Dicionários</h2>
          <p className="text-muted-foreground mb-6">Dicionários gerados pelo RevisAI</p>

          {dicionarios.length === 0 ? (
            <div className="text-center py-10">
              <p className="text-muted-foreground text-sm">Nenhum dicionário salvo ainda.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {dicionarios.map((dicionario) => (
                <div
                  key={dicionario.id}
                  className="rounded-lg border bg-card text-card-foreground shadow-sm p-5 card-hover border-l-4 border-l-primary relative group cursor-pointer"
                  onClick={() => setSelectedDicionario(dicionario)}
                >
                  {/* Action buttons */}
                  <div
                    className={`absolute top-3 right-3 flex gap-1 transition-opacity z-10 ${
                      editingDicionario?.id === dicionario.id
                        ? "opacity-0 pointer-events-none"
                        : "opacity-0 group-hover:opacity-100"
                    }`}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button
                      onClick={(e) => handleStartEdit(e, dicionario)}
                      title="Editar nome"
                      className="h-7 w-7 inline-flex items-center justify-center rounded-md text-muted-foreground hover:bg-primary/10 hover:text-primary transition-all"
                    >
                      <Pencil className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); setConfirmDeleteId(dicionario.id); }}
                      title="Excluir"
                      className="h-7 w-7 inline-flex items-center justify-center rounded-md text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-all"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <BookOpen className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0 pr-14">
                      {editingDicionario?.id === dicionario.id ? (
                        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                          <input
                            autoFocus
                            value={editTopic}
                            onChange={(e) => setEditTopic(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") handleSaveEdit();
                              if (e.key === "Escape") setEditingDicionario(null);
                            }}
                            className="flex-1 text-sm font-bold border border-primary rounded px-1.5 py-0.5 outline-none bg-background"
                          />
                          <button
                            onClick={handleSaveEdit}
                            disabled={saving}
                            className="text-primary hover:text-primary/80 transition-colors"
                          >
                            <Check className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => setEditingDicionario(null)}
                            className="text-muted-foreground hover:text-foreground transition-colors"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ) : (
                        <h3 className="font-bold text-sm truncate">{dicionario.topic}</h3>
                      )}
                      <p className="text-xs text-muted-foreground">{dicionario.date}</p>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {(dicionario.html.match(/<tr>/g) || []).length - 1 || dicionario.termsCount || 0} termos definidos
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* View modal */}
      {selectedDicionario && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div
            ref={modalRef}
            className="relative w-full max-w-2xl max-h-[80vh] overflow-auto border bg-background p-6 shadow-lg rounded-lg mx-4"
          >
            <div className="mb-4">
              <h2 className="text-lg font-semibold leading-none tracking-tight">{selectedDicionario.topic}</h2>
            </div>
            <div
              className="prose prose-sm max-w-none
                [&_table]:w-full [&_table]:border-collapse [&_table]:text-sm
                [&_thead_th]:p-2 [&_thead_th]:text-left [&_thead_th]:font-semibold [&_thead_th]:bg-muted
                [&_tbody_td]:p-2 [&_tbody_td]:border-t [&_tbody_td]:border-border
                [&_tbody_tr:nth-child(odd)]:bg-secondary/30"
              dangerouslySetInnerHTML={{ __html: selectedDicionario.html }}
            />
            <button
              type="button"
              onClick={() => setSelectedDicionario(null)}
              className="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100 transition-opacity"
            >
              <X className="h-4 w-4" />
              <span className="sr-only">Fechar</span>
            </button>
          </div>
        </div>
      )}

      {/* Delete confirmation modal */}
      {confirmDeleteId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-background border rounded-xl shadow-xl p-6 max-w-sm w-full mx-4 animate-fade-in">
            <h3 className="text-base font-semibold mb-2">Excluir dicionário?</h3>
            <p className="text-sm text-muted-foreground mb-5">Esta ação não pode ser desfeita.</p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setConfirmDeleteId(null)}
                className="inline-flex items-center justify-center h-9 rounded-md px-4 text-sm font-medium border border-input bg-background hover:bg-accent hover:text-accent-foreground transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirmDelete}
                disabled={deleting}
                className="inline-flex items-center justify-center h-9 rounded-md px-4 text-sm font-medium bg-destructive text-destructive-foreground hover:bg-destructive/90 transition-colors disabled:opacity-60"
              >
                {deleting ? "Excluindo..." : "Excluir"}
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
