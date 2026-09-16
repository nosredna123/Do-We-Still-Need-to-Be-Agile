import Layout from "../components/Layout";
import {
  BookOpen, RotateCcw, X, ArrowLeft, Play, Plus,
  ThumbsUp, ThumbsDown, FileText, BookMarked, Eye, Link2,
} from "lucide-react";
import { useFlashcards } from "../contexts/FlashcardContext";
import { useState, useEffect, useRef } from "react";
import { fetchFlashcards, fetchResumos, fetchDicionarios } from "../services/flashcard.service";

// ─── LocalStorage helpers ─────────────────────────────────────────────────────
const LS_LINKS_KEY    = "revisai:weekLinks";
const LS_DAY_LINKS    = "revisai:dayLinks";   // resumo/glossario/cards por dia
const LS_HISTORY_KEY  = "revisai:reviewHistory";

const ls = {
  get: (key, fallback = {}) => {
    try { return JSON.parse(localStorage.getItem(key) || "null") ?? fallback; }
    catch { return fallback; }
  },
  set: (key, val) => localStorage.setItem(key, JSON.stringify(val)),
};

// ─── Helpers de exibição genérica de conteúdo (Resumo/Dicionário) ─────────────
const CONTENT_FIELDS = ["html", "content", "description", "definition", "text", "body", "summary", "resumo"];
const HTML_FIELDS    = ["html"];
const TITLE_FIELDS   = ["title", "topic", "term", "name", "titulo"];

function getItemTitle(item) {
  for (const f of TITLE_FIELDS) if (item?.[f]) return item[f];
  return "Sem título";
}

function getItemContent(item) {
  for (const f of CONTENT_FIELDS) if (item?.[f]) return item[f];
  return null;
}

function isHtmlContent(item) {
  return HTML_FIELDS.some((f) => item?.[f]);
}

// ─── Modal: visualizar conteúdo de Resumo/Dicionário ──────────────────────────
function ContentViewModal({ item, typeLabel, onClose }) {
  const modalRef = useRef(null);

  useEffect(() => {
    let downOutside = false;
    const handleDown = (e) => {
      downOutside = modalRef.current && !modalRef.current.contains(e.target);
    };
    const handleUp = (e) => {
      if (downOutside && modalRef.current && !modalRef.current.contains(e.target)) {
        onClose();
      }
      downOutside = false;
    };
    document.addEventListener("mousedown", handleDown);
    document.addEventListener("mouseup", handleUp);
    return () => {
      document.removeEventListener("mousedown", handleDown);
      document.removeEventListener("mouseup", handleUp);
    };
  }, [onClose]);

  // Dicionário pode vir como array de termos { term, definition }
  const isTermList = Array.isArray(item?.terms) || Array.isArray(item?.items) || Array.isArray(item?.entries);
  const termList = item?.terms ?? item?.items ?? item?.entries ?? null;

  const content = getItemContent(item);
  
  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div ref={modalRef} className="relative w-full max-w-lg mx-4 border bg-background shadow-lg rounded-lg animate-fade-in flex flex-col max-h-[85vh]">
        <div className="flex items-center justify-between p-5 border-b shrink-0">
          <div className="min-w-0">
            <p className="text-xs text-muted-foreground mb-0.5">{typeLabel}</p>
            <h2 className="text-lg font-semibold leading-tight tracking-tight truncate">{getItemTitle(item)}</h2>
          </div>
          <button type="button" onClick={onClose} className="rounded-sm opacity-70 hover:opacity-100 transition-opacity shrink-0 ml-3">
            <X className="h-4 w-4" /><span className="sr-only">Fechar</span>
          </button>
        </div>

        <div className="overflow-y-auto flex-1 p-5 space-y-4 select-text" style={{ userSelect: "text" }}>
          <style>{`
            .glossario-html table { width: 100%; border-collapse: collapse; font-size: 0.875rem; margin-top: 0.5rem; }
            .glossario-html th, .glossario-html td { border: 1px solid hsl(var(--border, 220 13% 91%)); padding: 0.5rem 0.75rem; text-align: left; vertical-align: top; }
            .glossario-html th { background: hsl(var(--muted, 220 14% 96%)); font-weight: 600; }
            .glossario-html h1, .glossario-html h2, .glossario-html h3 { font-weight: 700; margin: 0.75rem 0 0.5rem; }
            .glossario-html p { margin: 0.5rem 0; }
            .glossario-html ul, .glossario-html ol { padding-left: 1.25rem; margin: 0.5rem 0; }
          `}</style>
          {item?.date && <p className="text-xs text-muted-foreground">{item.date}</p>}

          {isTermList && Array.isArray(termList) ? (
            <div className="space-y-3">
              {termList.map((t, idx) => (
                <div key={idx} className="rounded-md border p-3">
                  <p className="text-sm font-semibold">{t.term ?? t.name ?? t.title ?? `Item ${idx + 1}`}</p>
                  <p className="text-sm text-muted-foreground mt-1 whitespace-pre-wrap">
                    {t.definition ?? t.description ?? t.content ?? ""}
                  </p>
                </div>
              ))}
            </div>
          ) : isHtmlContent(item) ? (
            <div
              className="text-sm leading-relaxed select-text glossario-html"
              style={{ userSelect: "text" }}
              dangerouslySetInnerHTML={{ __html: content }}
            />
          ) : content ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap select-text">{content}</p>
          ) : (
            <pre className="text-xs bg-muted/40 rounded-md p-3 overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(item, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Modal: vincular / visualizar Resumo e Dicionário do dia da semana ────────
function DayLinksModal({ day, weekNumber, allResumos, allDicionarios, dayLinks, onToggle, onClose }) {
  const modalRef = useRef(null);
  const [tab, setTab] = useState("resumos"); // "resumos" | "glossarios"
  const [mode, setMode] = useState("link");  // "link" | "view"
  const [viewingItem, setViewingItem] = useState(null); // { item, typeLabel }

  useEffect(() => {
    const handleClick = (e) => {
      if (modalRef.current && !modalRef.current.contains(e.target)) onClose();
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [onClose]);

  const resumoIds    = dayLinks.resumos    ?? [];
  const glossarioIds = dayLinks.glossarios ?? [];

  const dayLabels = { SEG: "Segunda", TER: "Terça", QUA: "Quarta", QUI: "Quinta", SEX: "Sexta" };

  const renderList = (items, type, linkedIds, emptyMsg, typeLabel) => {
    if (mode === "view") {
      const linkedItems = items.filter((i) => linkedIds.includes(i.id));
      if (linkedItems.length === 0)
        return <p className="text-sm text-muted-foreground text-center py-8">Nenhum {typeLabel.toLowerCase()} vinculado a este dia ainda.</p>;

      return linkedItems.map((item) => (
        <button
          key={item.id}
          onClick={() => setViewingItem({ item, typeLabel })}
          className="w-full text-left rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground p-4 transition-colors flex items-start gap-3"
        >
          <Eye className="h-4 w-4 mt-0.5 text-muted-foreground shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium leading-snug truncate">{getItemTitle(item)}</p>
            {item.date && <p className="text-xs text-muted-foreground mt-0.5">{item.date}</p>}
          </div>
        </button>
      ));
    }

    if (items.length === 0)
      return <p className="text-sm text-muted-foreground text-center py-8">{emptyMsg}</p>;

    return items.map((item) => {
      const isLinked = linkedIds.includes(item.id);
      return (
        <button
          key={item.id}
          onClick={() => onToggle(type, item.id)}
          className={`w-full text-left rounded-md border p-4 transition-colors flex items-start gap-3 ${
            isLinked ? "border-primary/40 bg-primary/5" : "border-input bg-background hover:bg-accent hover:text-accent-foreground"
          }`}
        >
          <div className={`mt-0.5 h-5 w-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors ${isLinked ? "border-primary bg-primary" : "border-muted-foreground/40"}`}>
            {isLinked && <div className="h-2 w-2 rounded-full bg-white" />}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium leading-snug truncate">{getItemTitle(item)}</p>
            {item.date && <p className="text-xs text-muted-foreground mt-0.5">{item.date}</p>}
            {item.theme && (
              <span className="inline-block mt-1 text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">{item.theme}</span>
            )}
          </div>
        </button>
      );
    });
  };

  const totalLinked = resumoIds.length + glossarioIds.length;

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div ref={modalRef} className="relative w-full max-w-md mx-4 border bg-background shadow-lg rounded-lg animate-fade-in flex flex-col max-h-[80vh]">

          {/* Header */}
          <div className="flex items-center justify-between p-5 border-b shrink-0">
            <div>
              <h2 className="text-lg font-semibold leading-none tracking-tight">
                {dayLabels[day]} — Semana {weekNumber}
              </h2>
              <p className="text-xs text-muted-foreground mt-1">
                {mode === "link" ? "Vincular materiais de estudo" : "Visualizar materiais vinculados"}
              </p>
            </div>
            <button type="button" onClick={onClose} className="rounded-sm opacity-70 hover:opacity-100 transition-opacity">
              <X className="h-4 w-4" /><span className="sr-only">Fechar</span>
            </button>
          </div>

          {/* Mode toggle */}
          <div className="flex gap-2 p-3 border-b shrink-0">
            <button
              onClick={() => setMode("link")}
              className={`flex-1 inline-flex items-center justify-center gap-2 h-9 rounded-md text-sm font-medium transition-colors ${
                mode === "link" ? "bg-primary text-primary-foreground" : "border border-input bg-background hover:bg-accent hover:text-accent-foreground"
              }`}
            >
              <Link2 className="h-4 w-4" />
              Vincular
            </button>
            <button
              onClick={() => setMode("view")}
              className={`flex-1 inline-flex items-center justify-center gap-2 h-9 rounded-md text-sm font-medium transition-colors ${
                mode === "view" ? "bg-primary text-primary-foreground" : "border border-input bg-background hover:bg-accent hover:text-accent-foreground"
              }`}
            >
              <Eye className="h-4 w-4" />
              Visualizar
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b shrink-0">
            <button
              onClick={() => setTab("resumos")}
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors border-b-2 ${
                tab === "resumos" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <FileText className="h-4 w-4" />
              Resumos
              {resumoIds.length > 0 && (
                <span className="ml-1 h-4 w-4 rounded-full bg-primary text-primary-foreground text-[10px] font-bold flex items-center justify-center">
                  {resumoIds.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setTab("glossarios")}
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors border-b-2 ${
                tab === "glossarios" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <BookMarked className="h-4 w-4" />
              Dicionários
              {glossarioIds.length > 0 && (
                <span className="ml-1 h-4 w-4 rounded-full bg-primary text-primary-foreground text-[10px] font-bold flex items-center justify-center">
                  {glossarioIds.length}
                </span>
              )}
            </button>
          </div>

          {/* List */}
          <div className="overflow-y-auto flex-1 p-4 space-y-2">
            {tab === "resumos" &&
              renderList(allResumos, "resumos", resumoIds, 'Nenhum resumo disponível. Crie resumos em "Meus Resumos".', "Resumo")}
            {tab === "glossarios" &&
              renderList(allDicionarios, "glossarios", glossarioIds, 'Nenhum dicionário disponível. Crie dicionários em "Meus Dicionários".', "Dicionário")}
          </div>

          {/* Footer */}
          <div className="p-4 border-t shrink-0">
            <p className="text-xs text-muted-foreground text-center">
              {totalLinked} material{totalLinked !== 1 ? "is" : ""} vinculado{totalLinked !== 1 ? "s" : ""} a este dia
            </p>
          </div>
        </div>
      </div>

      {viewingItem && (
        <ContentViewModal
          item={viewingItem.item}
          typeLabel={viewingItem.typeLabel}
          onClose={() => setViewingItem(null)}
        />
      )}
    </>
  );
}

// ─── Modal: Sábado / Domingo ──────────────────────────────────────────────────
function DayReviewModal({ day, weekNumber, linkedCount, onClose, onStartReview, onManageCards }) {
  const modalRef = useRef(null);
  const dayLabel = day === "SAB" ? "Sábado" : "Domingo";

  useEffect(() => {
    const handleClick = (e) => {
      if (modalRef.current && !modalRef.current.contains(e.target)) onClose();
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div ref={modalRef} className="relative w-full max-w-md mx-4 border bg-background p-6 shadow-lg rounded-lg animate-fade-in">
        <button type="button" onClick={onClose} className="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100 transition-opacity">
          <X className="h-4 w-4" /><span className="sr-only">Fechar</span>
        </button>

        <div className="flex items-center gap-2 mb-1">
          <RotateCcw className="h-5 w-5 text-accent" />
          <h2 className="text-lg font-semibold leading-none tracking-tight">{dayLabel} — Semana {weekNumber}</h2>
        </div>
        <p className="text-sm text-muted-foreground mt-2 mb-6">
          {linkedCount === 0
            ? "0 cards vinculados a esta semana."
            : `${linkedCount} card${linkedCount !== 1 ? "s" : ""} vinculado${linkedCount !== 1 ? "s" : ""} a esta semana.`}
        </p>

        <div className="flex flex-col gap-3">
          <button
            onClick={onStartReview}
            disabled={linkedCount === 0}
            className="inline-flex items-center justify-center gap-2 h-10 rounded-md px-4 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed w-full"
          >
            <Play className="h-4 w-4" />
            Iniciar Revisão ({linkedCount} cards)
          </button>
          <button
            onClick={onManageCards}
            className="inline-flex items-center justify-center gap-2 h-10 rounded-md px-4 text-sm font-medium border border-input bg-background hover:bg-accent hover:text-accent-foreground transition-colors w-full"
          >
            <Plus className="h-4 w-4" />
            Adicionar / Gerenciar Cards
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Modal: Gerenciar Cards ───────────────────────────────────────────────────
function ManageCardsModal({ weekNumber, allCards, linkedCardIds, onBack, onClose, onToggleCard }) {
  const modalRef = useRef(null);

  useEffect(() => {
    const handleClick = (e) => {
      if (modalRef.current && !modalRef.current.contains(e.target)) onClose();
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div ref={modalRef} className="relative w-full max-w-md mx-4 border bg-background shadow-lg rounded-lg animate-fade-in flex flex-col max-h-[80vh]">
        <div className="flex items-center justify-between p-5 border-b shrink-0">
          <h2 className="text-lg font-semibold leading-none tracking-tight">Vincular Cards — Semana {weekNumber}</h2>
          <button type="button" onClick={onClose} className="rounded-sm opacity-70 hover:opacity-100 transition-opacity">
            <X className="h-4 w-4" /><span className="sr-only">Fechar</span>
          </button>
        </div>

        <button onClick={onBack} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground px-5 py-3 border-b transition-colors shrink-0 text-left">
          <ArrowLeft className="h-4 w-4" />Voltar
        </button>

        <div className="overflow-y-auto flex-1 p-4 space-y-2">
          {allCards.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">Nenhum card disponível. Crie cards em "Meus Cards".</p>
          ) : (
            allCards.map((card) => {
              const isLinked = linkedCardIds.includes(card.id);
              return (
                <button
                  key={card.id}
                  onClick={() => onToggleCard(card.id)}
                  className={`w-full text-left rounded-md border p-4 transition-colors flex items-start gap-3 ${
                    isLinked ? "border-primary/40 bg-primary/5" : "border-input bg-background hover:bg-accent hover:text-accent-foreground"
                  }`}
                >
                  <div className={`mt-0.5 h-5 w-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors ${isLinked ? "border-primary bg-primary" : "border-muted-foreground/40"}`}>
                    {isLinked && <div className="h-2 w-2 rounded-full bg-white" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium leading-snug truncate">{card.front || card.question || "Sem título"}</p>
                    {card.theme && (
                      <span className="inline-block mt-1 text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">{card.theme}</span>
                    )}
                  </div>
                </button>
              );
            })
          )}
        </div>

        <div className="p-4 border-t shrink-0">
          <p className="text-xs text-muted-foreground text-center">
            {linkedCardIds.length} card{linkedCardIds.length !== 1 ? "s" : ""} selecionado{linkedCardIds.length !== 1 ? "s" : ""}
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── Modal: Revisão ───────────────────────────────────────────────────────────
function ReviewModal({ day, weekNumber, cards, onClose, onSaveResult }) {
  const textareaRef = useRef(null);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswer, setUserAnswer]     = useState("");
  const [revealed, setRevealed]         = useState(false);
  const [judged, setJudged]             = useState(false);
  const [hits, setHits]                 = useState(0);
  const [errors, setErrors]             = useState(0);
  const [showFinishConfirm, setShowFinishConfirm] = useState(false);

  const currentCard = cards[currentIndex];
  const total       = cards.length;
  const progress    = Math.round(((currentIndex + (judged ? 1 : 0)) / total) * 100);

  const handleReveal = () => { if (userAnswer.trim()) setRevealed(true); };
  const handleJudge  = (correct) => {
    if (correct) setHits((h) => h + 1); else setErrors((e) => e + 1);
    setJudged(true);
  };
  const handleNext = () => {
    if (currentIndex < total - 1) {
      setCurrentIndex((i) => i + 1);
      setUserAnswer(""); setRevealed(false); setJudged(false);
      setTimeout(() => textareaRef.current?.focus(), 50);
    } else {
      setShowFinishConfirm(true);
    }
  };
  const handleRestart = () => {
    setShowFinishConfirm(false); setCurrentIndex(0);
    setUserAnswer(""); setRevealed(false); setJudged(false);
    setHits(0); setErrors(0);
    setTimeout(() => textareaRef.current?.focus(), 50);
  };
  const handleFinish = () => {
    onSaveResult({ day, weekNumber, hits, errors, total, date: new Date().toISOString() });
    onClose();
  };
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && e.ctrlKey && !revealed) handleReveal();
  };

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div className="relative w-full max-w-lg mx-4 border bg-background shadow-lg rounded-lg animate-fade-in">
          <div className="flex items-center justify-between p-5 border-b">
            <h2 className="text-lg font-semibold leading-none tracking-tight">Revisão — Semana {weekNumber}</h2>
            <div className="flex items-center gap-3">
              <span className="text-sm text-muted-foreground tabular-nums">{currentIndex + 1}/{total}</span>
              <button type="button" onClick={onClose} className="rounded-sm opacity-70 hover:opacity-100 transition-opacity">
                <X className="h-4 w-4" /><span className="sr-only">Fechar</span>
              </button>
            </div>
          </div>

          <div className="h-1 bg-muted w-full">
            <div className="h-1 bg-primary transition-all duration-300" style={{ width: `${progress}%` }} />
          </div>

          <div className="p-5 space-y-4">
            <div className="rounded-md border bg-muted/40 min-h-[90px] flex items-center justify-center p-5">
              <p className="text-base font-medium text-center leading-relaxed">
                {currentCard.front || currentCard.question}
              </p>
            </div>

            <div>
              <p className="text-sm font-medium mb-1.5">Sua resposta:</p>
              <textarea
                ref={textareaRef}
                autoFocus
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={revealed}
                placeholder="Digite sua resposta... (Ctrl+Enter para revelar)"
                rows={3}
                className="w-full text-sm border border-input rounded-md px-3 py-2.5 resize-none focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 bg-background disabled:opacity-70 disabled:cursor-not-allowed transition-all"
              />
            </div>

            {revealed && (
              <div className="rounded-md border border-blue-200 bg-blue-50 p-4">
                <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-1">Gabarito</p>
                <p className="text-sm text-blue-900 leading-relaxed whitespace-pre-wrap">{currentCard.back || currentCard.answer}</p>
              </div>
            )}

            {!revealed && (
              <button onClick={handleReveal} disabled={!userAnswer.trim()}
                className="inline-flex items-center justify-center w-full h-10 rounded-md px-4 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Revelar Resposta
              </button>
            )}

            {revealed && !judged && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-center text-muted-foreground">Você acertou?</p>
                <div className="grid grid-cols-2 gap-3">
                  <button onClick={() => handleJudge(false)}
                    className="inline-flex items-center justify-center gap-2 h-10 rounded-md border border-red-200 bg-red-50 text-red-700 hover:bg-red-100 transition-colors text-sm font-medium"
                  ><ThumbsDown className="h-4 w-4" /> Errei</button>
                  <button onClick={() => handleJudge(true)}
                    className="inline-flex items-center justify-center gap-2 h-10 rounded-md border border-green-200 bg-green-50 text-green-700 hover:bg-green-100 transition-colors text-sm font-medium"
                  ><ThumbsUp className="h-4 w-4" /> Acertei</button>
                </div>
              </div>
            )}

            {revealed && judged && (
              <button onClick={handleNext}
                className="inline-flex items-center justify-center w-full h-10 rounded-md px-4 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                {currentIndex < total - 1 ? "Próximo Card →" : "Finalizar Revisão"}
              </button>
            )}

            <div className="grid grid-cols-2 gap-3 pt-1">
              <div className="rounded-md border border-green-200 bg-green-50 p-3 text-center">
                <p className="text-xs text-green-700 font-medium mb-1">Acertos</p>
                <p className="text-2xl font-bold text-green-600">{hits}</p>
              </div>
              <div className="rounded-md border border-red-200 bg-red-50 p-3 text-center">
                <p className="text-xs text-red-700 font-medium mb-1">Erros</p>
                <p className="text-2xl font-bold text-red-600">{errors}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showFinishConfirm && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-background border rounded-xl shadow-xl p-6 max-w-sm w-full mx-4 animate-fade-in">
            <h3 className="text-base font-semibold mb-2">Revisão concluída!</h3>
            <p className="text-sm text-muted-foreground mb-1">
              Você acertou <span className="font-semibold text-green-600">{hits}</span> de{" "}
              <span className="font-semibold">{total}</span> cards.
            </p>
            <p className="text-sm text-muted-foreground mb-5">
              Erros: <span className="font-semibold text-red-600">{errors}</span>
            </p>
            <div className="flex gap-3 justify-end">
              <button onClick={handleRestart}
                className="inline-flex items-center justify-center h-9 rounded-md px-4 text-sm font-medium border border-input bg-background hover:bg-accent hover:text-accent-foreground transition-colors"
              >Revisar novamente</button>
              <button onClick={handleFinish}
                className="inline-flex items-center justify-center h-9 rounded-md px-4 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
              >Concluir</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function Weeks() {
  const { themes } = useFlashcards();
  const totalSavedCards = themes ? themes.reduce((acc, t) => acc + t.cards.length, 0) : 0;



  // Dados externos
  const [allCards, setAllCards]           = useState([]);
  const [allResumos, setAllResumos]       = useState([]);
  const [allDicionarios, setAllDicionarios] = useState([]);

  // Links persistidos
  const [weekLinks, setWeekLinks] = useState(() => ls.get(LS_LINKS_KEY));     // cards SAB/DOM
  const [dayLinks, setDayLinks]   = useState(() => ls.get(LS_DAY_LINKS));     // resumos/glossarios/cards SEG-SEX

  const [activeWeek, setActiveWeek] = useState(1);

  // Modais
  const [openDay, setOpenDay]         = useState(null);   // SAB/DOM
  const [modalView, setModalView]     = useState("day-review");
  const [openWeekDay, setOpenWeekDay] = useState(null);   // SEG–SEX

  useEffect(() => {
    fetchFlashcards().then(setAllCards).catch(() => {});
    fetchResumos().then(setAllResumos).catch(() => {});
    fetchDicionarios().then(setAllDicionarios).catch(() => {});
  }, []);

  useEffect(() => { ls.set(LS_LINKS_KEY, weekLinks); }, [weekLinks]);
  useEffect(() => { ls.set(LS_DAY_LINKS, dayLinks); }, [dayLinks]);

  // ── helpers SAB/DOM ──
  const linkKey        = (day) => `${activeWeek}-${day}`;
  const getLinkedIds   = (day) => weekLinks[linkKey(day)] ?? [];
  const getLinkedCards = (day) => allCards.filter((c) => getLinkedIds(day).includes(c.id));

  const toggleCard = (day, cardId) => {
    const key = linkKey(day);
    setWeekLinks((prev) => {
      const cur = prev[key] ?? [];
      return { ...prev, [key]: cur.includes(cardId) ? cur.filter((id) => id !== cardId) : [...cur, cardId] };
    });
  };

  // ── helpers SEG–SEX ──
  const dayLinkKey = (day) => `${activeWeek}-${day}`;
  const getDayLinks = (day) => dayLinks[dayLinkKey(day)] ?? { resumos: [], glossarios: [] };

  const toggleDayItem = (day, type, itemId) => {
    const key = dayLinkKey(day);
    setDayLinks((prev) => {
      const current = prev[key] ?? { resumos: [], glossarios: [] };
      const arr     = current[type] ?? [];
      const updated = arr.includes(itemId) ? arr.filter((id) => id !== itemId) : [...arr, itemId];
      return { ...prev, [key]: { ...current, [type]: updated } };
    });
  };


  // ── misc ──
  const handleSaveResult = (result) => {
    const history = ls.get(LS_HISTORY_KEY);
    const key     = `${result.weekNumber}-${result.day}`;
    const entries = [result, ...(history[key] ?? [])].slice(0, 20);
    ls.set(LS_HISTORY_KEY, { ...history, [key]: entries });
  };


  const totalLinkedCards   = getLinkedIds("SAB").length + getLinkedIds("DOM").length;

  const weekdays = ["SEG", "TER", "QUA", "QUI", "SEX"];
  const weekend  = ["SAB", "DOM"];

  const closeModal    = () => { setOpenDay(null); setModalView("day-review"); };
  const closeWeekDay  = () => setOpenWeekDay(null);

  return (
    <Layout savedCardsCount={totalSavedCards}>
      <div className="flex-1 overflow-auto">
        <div className="max-w-5xl mx-auto animate-fade-in">
          <h2 className="text-2xl font-bold mb-1">Semanas de Estudo</h2>
          <p className="text-muted-foreground mb-6">Planeje seus estudos e revisões semanais</p>

          {/* Week tabs */}
          <div className="flex gap-3 mb-8">
            {[1, 2, 3, 4].map((w) => (
              <button key={w} onClick={() => setActiveWeek(w)}
                className={`px-5 py-2.5 rounded-lg font-semibold text-sm transition-all ${
                  activeWeek === w ? "bg-primary text-primary-foreground shadow-md" : "bg-card text-foreground border hover:bg-muted"
                }`}
              >Semana {w}</button>
            ))}
          </div>

          {/* Day grid */}
          <div className="grid grid-cols-7 gap-3 mb-8">
            {weekdays.map((day) => {
              const dl          = getDayLinks(day);
              const linkedCount = (dl.resumos?.length ?? 0) + (dl.glossarios?.length ?? 0);

              return (
                <div key={day} className="text-center">
                  <p className="text-xs font-bold text-muted-foreground mb-2">{day}</p>
                  <div
                    onClick={() => setOpenWeekDay(day)}
                    className="rounded-lg border text-card-foreground shadow-sm p-3 min-h-[120px] flex flex-col items-center justify-center gap-2 transition-all bg-card cursor-pointer group hover:border-primary/40 hover:shadow-md"
                  >
                    <BookOpen className={`h-5 w-5 transition-colors ${linkedCount > 0 ? "text-primary" : "text-muted-foreground/40 group-hover:text-primary/70"}`} />

                    {linkedCount > 0 ? (
                      <span className="inline-flex items-center gap-1 rounded-full border border-primary/40 bg-primary/5 text-primary px-2 py-0.5 text-[10px] font-semibold">
                        <FileText className="h-2.5 w-2.5" />
                        {linkedCount} {linkedCount === 1 ? "material" : "materiais"}
                      </span>
                    ) : (
                      <span className="text-[10px] text-muted-foreground/60 group-hover:text-primary/60 transition-colors font-medium">
                        Vincular
                      </span>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Weekend */}
            {weekend.map((day) => {
              const count = getLinkedIds(day).length;
              return (
                <div key={day} className="text-center">
                  <p className="text-xs font-bold text-muted-foreground mb-2">{day}</p>
                  <div
                    onClick={() => { setOpenDay(day); setModalView("day-review"); }}
                    className="rounded-lg text-card-foreground shadow-sm p-3 min-h-[120px] flex flex-col items-center justify-center gap-2 transition-all border-accent border-2 bg-accent/10 cursor-pointer hover:bg-accent/20 hover:shadow-md"
                  >
                    <RotateCcw className="h-6 w-6 text-accent" />
                    <span className="text-xs font-medium text-center leading-tight">Revisão</span>
                    <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 font-semibold transition-colors text-[10px] border-accent text-accent">
                      {count > 0 ? `${count} card${count !== 1 ? "s" : ""}` : "Revisão"}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="rounded-lg border text-card-foreground shadow-sm p-5 bg-primary/5 border-primary/20">
              <div className="flex items-center gap-3 mb-2">
                <FileText className="h-5 w-5 text-primary" />
                <span className="font-bold text-sm">Materiais Vinculados</span>
              </div>
              <p className="text-2xl font-bold text-primary">
                {weekdays.reduce((acc, d) => {
                  const dl = getDayLinks(d);
                  return acc + (dl.resumos?.length ?? 0) + (dl.glossarios?.length ?? 0);
                }, 0)}
              </p>
              <p className="text-xs text-muted-foreground">resumos e dicionários esta semana</p>
            </div>
            <div className="rounded-lg border text-card-foreground shadow-sm p-5 bg-accent/5 border-accent/20">
              <div className="flex items-center gap-3 mb-2">
                <RotateCcw className="h-5 w-5 text-accent" />
                <span className="font-bold text-sm">Cards para Revisão</span>
              </div>
              <p className="text-2xl font-bold text-accent">{totalLinkedCards}</p>
              <p className="text-xs text-muted-foreground">
                {totalLinkedCards === 0 ? "clique no sábado ou domingo para revisar" : `vinculados à Semana ${activeWeek}`}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Modal: dia da semana (resumo/dicionário) ── */}
      {openWeekDay && (
        <DayLinksModal
          day={openWeekDay}
          weekNumber={activeWeek}
          allResumos={allResumos}
          allDicionarios={allDicionarios}
          dayLinks={getDayLinks(openWeekDay)}
          onToggle={(type, id) => toggleDayItem(openWeekDay, type, id)}
          onClose={closeWeekDay}
        />
      )}

      {/* ── Modais SAB/DOM ── */}
      {openDay && modalView === "day-review" && (
        <DayReviewModal
          day={openDay} weekNumber={activeWeek}
          linkedCount={getLinkedIds(openDay).length}
          onClose={closeModal}
          onStartReview={() => setModalView("reviewing")}
          onManageCards={() => setModalView("manage-cards")}
        />
      )}

      {openDay && modalView === "manage-cards" && (
        <ManageCardsModal
          weekNumber={activeWeek}
          allCards={allCards}
          linkedCardIds={getLinkedIds(openDay)}
          onBack={() => setModalView("day-review")}
          onClose={closeModal}
          onToggleCard={(id) => toggleCard(openDay, id)}
        />
      )}

      {openDay && modalView === "reviewing" && getLinkedCards(openDay).length > 0 && (
        <ReviewModal
          day={openDay} weekNumber={activeWeek}
          cards={getLinkedCards(openDay)}
          onClose={closeModal}
          onSaveResult={handleSaveResult}
        />
      )}
    </Layout>
  );
}