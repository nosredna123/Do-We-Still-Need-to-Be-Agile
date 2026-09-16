import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useFlashcards } from "../contexts/FlashcardContext";
import Layout from "../components/Layout";
import { CreditCard, Pencil, Trash2, Check, X } from "lucide-react";

export default function MyCards() {
  const navigate = useNavigate();
  const { themes, renameTheme, deleteTheme } = useFlashcards();

  const [editingTheme, setEditingTheme] = useState(null); // { id, name }
  const [editName, setEditName] = useState("");
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleStartEdit = (e, theme) => {
    e.stopPropagation();
    setEditingTheme(theme);
    setEditName(theme.name);
  };

  const handleSaveEdit = async () => {
    if (!editName.trim() || editName === editingTheme.name) {
      setEditingTheme(null);
      return;
    }
    setSaving(true);
    try {
      await renameTheme(editingTheme.id, editName.trim());
      setEditingTheme(null);
    } catch (err) {
      console.error("Erro ao renomear tema:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!confirmDeleteId) return;
    setDeleting(true);
    try {
      await deleteTheme(confirmDeleteId);
      setConfirmDeleteId(null);
    } catch (err) {
      console.error("Erro ao excluir tema:", err);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-5xl mx-auto animate-fade-in w-full overflow-y-auto">
        <h2 className="text-2xl font-bold mb-1 text-foreground">Meus Cards</h2>
        <p className="text-sm text-muted-foreground mb-6">{themes.length} temas disponíveis</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 w-full">
          {themes.map(theme => (
            <div
              key={theme.id}
              className="bg-card p-5 border border-l-4 border-l-primary rounded-[var(--radius)] shadow-sm card-hover text-card-foreground relative group cursor-pointer"
              onClick={() => navigate(`/meus-cards/${theme.id}`)}
            >
              {/* Action buttons — appear on hover, hidden while editing */}
              <div
                className={`absolute top-3 right-3 flex gap-1 transition-opacity z-10 ${
                  editingTheme?.id === theme.id
                    ? "opacity-0 pointer-events-none"
                    : "opacity-0 group-hover:opacity-100"
                }`}
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  onClick={(e) => handleStartEdit(e, theme)}
                  title="Renomear tema"
                  className="h-7 w-7 inline-flex items-center justify-center rounded-md text-muted-foreground hover:bg-primary/10 hover:text-primary transition-all"
                >
                  <Pencil className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); setConfirmDeleteId(theme.id); }}
                  title="Excluir tema"
                  className="h-7 w-7 inline-flex items-center justify-center rounded-md text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-all"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <CreditCard className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0 pr-14">
                  {editingTheme?.id === theme.id ? (
                    <div
                      className="flex items-center gap-1"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <input
                        autoFocus
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") handleSaveEdit();
                          if (e.key === "Escape") setEditingTheme(null);
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
                        onClick={() => setEditingTheme(null)}
                        className="text-muted-foreground hover:text-foreground transition-colors"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <h3 className="font-bold text-sm text-foreground truncate">{theme.name}</h3>
                  )}
                  <p className="text-xs text-muted-foreground">{theme.cards.length} cards</p>
                </div>
              </div>

              <p className="text-xs text-muted-foreground line-clamp-1 leading-relaxed">
                {theme.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Delete confirmation modal */}
      {confirmDeleteId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-background border rounded-xl shadow-xl p-6 max-w-sm w-full mx-4 animate-fade-in">
            <h3 className="text-base font-semibold mb-2">Excluir tema?</h3>
            <p className="text-sm text-muted-foreground mb-5">
              Todos os cards deste tema serão excluídos. Esta ação não pode ser desfeita.
            </p>
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
