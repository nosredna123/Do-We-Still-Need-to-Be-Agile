import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { gsap } from "gsap";
import { Trash2 } from "lucide-react";
import { useFlashcards } from "../contexts/FlashcardContext";
import Layout from "../components/Layout";

function Flashcard({ card, onEdit, onDelete }) {
  const [isFlipped, setIsFlipped] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const cardRef = useRef(null);

  const handleFlip = () => {
    if (isAnimating) return;
    setIsFlipped(!isFlipped);
  };

  useEffect(() => {
    if (cardRef.current) {
      gsap.to(cardRef.current, {
        rotationY: isFlipped ? 180 : 0,
        duration: 0.6,
        ease: "back.out(1.2)",
        onStart: () => setIsAnimating(true),
        onComplete: () => setIsAnimating(false),
      });
    }
  }, [isFlipped]);

  return (
    <div className="relative group">
      {/* Controls Container */}
      <div className={`absolute top-2 left-2 z-10 flex gap-1 transition-opacity duration-200 ${isAnimating ? 'opacity-0 pointer-events-none' : 'opacity-0 group-hover:opacity-100'}`}>
        {/* Edit Button */}
        <button
          onClick={(e) => { e.stopPropagation(); onEdit(card); }}
          className="h-7 w-7 inline-flex items-center justify-center rounded-md text-muted-foreground hover:bg-primary/10 hover:text-primary transition-all"
          title="Editar card"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-3.5 h-3.5">
            <path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"></path><path d="m15 5 4 4"></path>
          </svg>
        </button>

        {/* Delete Button */}
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(card); }}
          className="h-7 w-7 inline-flex items-center justify-center rounded-md text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-all"
          title="Excluir card"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>

      <div 
        className="perspective-1000 w-full h-64 cursor-pointer"
        onClick={handleFlip}
      >
        <div 
          ref={cardRef}
          className="relative w-full h-full transition-transform duration-500 preserve-3d rounded-lg"
        >
          {/* Front Face (Question) */}
          <div className="rounded-lg border bg-card text-card-foreground shadow-sm absolute inset-0 p-6 flex flex-col items-center justify-center text-center backface-hidden">
            <div className="inline-flex items-center rounded-full border border-gray-100 px-2.5 py-0.5 font-semibold text-gray-400 absolute top-3 right-3 text-[10px] uppercase tracking-wider">
              Pergunta
            </div>
            <p className="text-sm font-semibold text-gray-800">{card.question}</p>
            <p className="text-xs text-muted-foreground mt-3">Clique para virar</p>
          </div>

          {/* Back Face (Answer) */}
          <div className="rounded-lg border bg-primary/5 border-primary/20 text-card-foreground shadow-sm absolute inset-0 p-6 flex flex-col items-center justify-center text-center rotate-y-180 backface-hidden">
            <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-2.5 py-0.5 font-semibold text-primary absolute top-3 right-3 text-[10px] uppercase tracking-wider">
              Resposta
            </div>
            <p className="text-sm font-medium text-gray-700 leading-relaxed">
              {card.answer}
            </p>
            <p className="text-xs text-primary/60 mt-3 font-semibold">Clique para voltar</p>
          </div>

        </div>
      </div>
    </div>
  );
}

export default function DeckDetail() {
  const { deckId } = useParams();
  const navigate = useNavigate();
  const { themes, updateCard } = useFlashcards();
  
  const [editingCard, setEditingCard] = useState(null);
  const [deletingCard, setDeletingCard] = useState(null);
  const [editQuestion, setEditQuestion] = useState("");
  const [editAnswer, setEditAnswer] = useState("");

  const { removeCard } = useFlashcards();

  const deck = themes.find(t => t.id === deckId);

  const openEdit = (card) => {
    setEditingCard(card);
    setEditQuestion(card.question);
    setEditAnswer(card.answer);
  };

  const handleSave = () => {
    if (editingCard) {
      updateCard(editingCard.id, editQuestion, editAnswer);
      setEditingCard(null);
    }
  };

  if (!deck) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center h-full text-center p-8">
          <h2 className="text-xl font-bold text-gray-800">Deck não encontrado</h2>
          <button onClick={() => navigate("/meus-cards")} className="mt-4 text-[#2d6a4f] font-bold">Voltar para meus cards</button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto w-full animate-fade-in overflow-y-auto">
        <button 
          onClick={() => navigate("/meus-cards")}
          className="inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-medium h-9 rounded-md px-3 mb-4 bg-transparent hover:bg-accent hover:text-accent-foreground transition-colors duration-150"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 mr-1">
            <path d="m12 19-7-7 7-7" />
            <path d="M19 12H5" />
          </svg>
          Voltar
        </button>

        <h2 className="text-2xl font-bold mb-1 text-foreground">{deck.name}</h2>
        <p className="text-sm text-muted-foreground mb-6">{deck.cards.length} cards — clique para virar</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-12">
          {deck.cards.map((card) => (
            <Flashcard 
              key={card.id} 
              card={card} 
              onEdit={openEdit} 
              onDelete={(c) => setDeletingCard(c)}
            />
          ))}
        </div>
      </div>


      {/* Basic Edit Modal */}
      {editingCard && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center px-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setEditingCard(null)} />
          <div className="bg-card rounded-3xl p-8 w-full max-w-md relative shadow-2xl animate-in zoom-in-95 duration-200">
            <h3 className="text-xl font-bold text-gray-800 mb-6">Editar Card</h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block">Pergunta</label>
                <textarea 
                  value={editQuestion} 
                  onChange={e => setEditQuestion(e.target.value)} 
                  rows={3}
                  className="w-full bg-muted border border-border rounded-2xl px-4 py-3 text-sm focus:border-primary outline-none transition-all"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block">Resposta</label>
                <textarea 
                  value={editAnswer} 
                  onChange={e => setEditAnswer(e.target.value)} 
                  rows={3}
                  className="w-full bg-muted border border-border rounded-2xl px-4 py-3 text-sm focus:border-primary outline-none transition-all"
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-8">
              <button 
                onClick={() => setEditingCard(null)}
                className="flex-1 px-6 py-3 bg-gray-100 text-gray-600 rounded-2xl text-sm font-bold hover:bg-gray-200 transition-all"
              >
                Cancelar
              </button>
              <button 
                onClick={handleSave}
                className="flex-1 px-6 py-3 bg-primary text-primary-foreground rounded-2xl text-sm font-bold hover:bg-primary/90 shadow-lg shadow-primary/20 transition-all"
              >
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Delete Confirmation Modal */}
      {deletingCard && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center px-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setDeletingCard(null)} />
          <div className="bg-card rounded-3xl p-8 w-full max-w-md relative shadow-2xl animate-in zoom-in-95 duration-200 text-center">
            <h3 className="text-xl font-bold text-gray-800 mb-2">Excluir Card?</h3>
            <p className="text-muted-foreground mb-8 text-sm">
              Tem certeza que deseja excluir este card? Esta ação não pode ser desfeita.
            </p>
            
            <div className="flex gap-3">
              <button 
                onClick={() => setDeletingCard(null)}
                className="flex-1 px-6 py-3 bg-muted text-muted-foreground rounded-2xl text-sm font-bold hover:bg-gray-200 transition-all"
              >
                Não, manter
              </button>
              <button 
                onClick={() => {
                  removeCard(deletingCard.id);
                  setDeletingCard(null);
                }}
                className="flex-1 px-6 py-3 bg-destructive text-destructive-foreground rounded-2xl text-sm font-bold hover:bg-destructive/90 shadow-lg shadow-destructive/20 transition-all"
              >
                Sim, excluir
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}


