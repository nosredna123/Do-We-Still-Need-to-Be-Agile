import heroImage from "@/assets/hero-food.jpg";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";

export function Hero() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleInitChat = () => {
    navigate(isAuthenticated ? "/chat" : "/login")
  }

  return (
    <section className="relative isolate overflow-hidden min-h-screen pt-32 pb-20 md:pt-40 md:pb-32">
      <div
        className="absolute inset-0 -z-10 bg-cover bg-center opacity-90"
        style={{ backgroundImage: `url(${heroImage})` }}
        aria-hidden
      />
      <div
        className="absolute inset-0 -z-10 bg-gradient-to-r from-white via-white/85 to-white/20"
        aria-hidden
      />

      <div className="mx-auto max-w-6xl px-6">
        <div className="max-w-2xl">
          <span className="inline-flex items-center gap-2 rounded-full border border-foodguard-400/30 bg-foodguard-50 px-3 py-1 text-xs font-medium text-foodguard-600">
            <Sparkles className="h-3.5 w-3.5" />
            Análise inteligente de alergênicos
          </span>

          <h1 className="mt-6 font-sansita text-4xl font-extrabold leading-[1.05] tracking-tight text-black sm:text-5xl md:text-6xl">
            Coma com confiança.{" "}
            <span className="text-foodguard-500">Sem surpresas</span> no rótulo.
          </h1>

          <p className="mt-6 text-lg leading-relaxed text-zinc-600">
            O FoodGuard cruza o seu histórico de saúde com os ingredientes dos
            produtos que você consome. Tire uma foto do código de barras ou
            descreva o alimento — nós te dizemos se é seguro.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Button
              size="lg"
              className="rounded-full px-6 bg-foodguard-500 hover:bg-foodguard-600 text-white border-transparent"
              onClick={handleInitChat}
            >
              Iniciar conversa
              <ArrowRight className="ml-1 h-4 w-4" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="rounded-full px-6 border-zinc-400 text-black hover:bg-foodguard-50 hover:border-foodguard-400"
              onClick={() =>
                document
                  .getElementById("como-funciona")
                  ?.scrollIntoView({ behavior: "smooth" })
              }
            >
              Saiba mais
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}
