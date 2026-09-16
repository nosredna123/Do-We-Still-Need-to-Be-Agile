import { Sparkles } from "lucide-react";
import { cn } from "../lib/utils";

interface SuggestionCardProps {
  text: string;
  onClick?: () => void;
}

const SuggestionCard = ({ text, onClick }: SuggestionCardProps) => {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 px-4 py-3.5 rounded-xl border transition-all",
        "bg-suggestion border-suggestion-border dark:bg-[#1E1E1E] dark:hover:bg-[#2A2A2A] dark:border-[#333333]",
        "hover:bg-suggestion-hover hover:border-primary/30",
        "text-left w-full group"
      )}
    >
      <Sparkles className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors flex-shrink-0" />
      <span className="text-sm text-foreground ">{text}</span>
    </button>
  );
};

export default SuggestionCard;