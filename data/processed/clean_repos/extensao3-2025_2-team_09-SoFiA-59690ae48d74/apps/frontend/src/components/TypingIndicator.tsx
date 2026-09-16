const TypingIndicator = () => {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-muted rounded-2xl px-4 py-3">
        <div className="flex gap-1 items-center">
          <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
          <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
          <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce"></div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;