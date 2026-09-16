import { Card, CardContent } from "@/components/ui/card";
import { Camera, MessageSquare, ShieldCheck, Brain } from "lucide-react";

const features = [
  {
    icon: MessageSquare,
    title: "Converse por texto",
    description:
      "Descreva o alimento ou pergunte se um produto é seguro. O chatbot responde com base na sua anamnese.",
  },
  {
    icon: Camera,
    title: "Leia o código de barras",
    description:
      "Envie uma foto e o modelo YOLOv8n extrai o código para consultar ingredientes e alergênicos.",
  },
  {
    icon: ShieldCheck,
    title: "Análise personalizada",
    description:
      "Cruzamos seu histórico de saúde com os dados nutricionais para prevenir reações adversas.",
  },
  {
    icon: Brain,
    title: "IA + visão computacional",
    description:
      "Combinamos LLM com ONNX Runtime-web no navegador para respostas rápidas e privadas.",
  },
];

export function HowItWorks() {
  return (
    <section id="como-funciona" className="min-h-screen bg-slate-100 py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold uppercase tracking-wider text-foodguard-500">
            Como funciona?
          </p>
          <h2 className="mt-3 font-sansita text-3xl font-extrabold tracking-tight text-black sm:text-4xl">
            Interpretar rótulos nunca foi tão simples
          </h2>
          <p className="mt-4 text-base leading-relaxed text-zinc-600">
            O FoodGuard é uma plataforma web que identifica componentes
            alergênicos em produtos alimentícios. Resolvemos um problema real
            de quem precisa decifrar rótulos confusos todos os dias —
            cruzando dados nutricionais com o seu histórico médico (anamnese)
            de forma ágil e intuitiva.
          </p>
        </div>

        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f) => (
            <Card
              key={f.title}
              className="border-zinc-200 transition-shadow hover:shadow-md"
            >
              <CardContent className="p-6">
                <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-foodguard-50 text-foodguard-500">
                  <f.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 text-base font-semibold text-black">
                  {f.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-zinc-500">
                  {f.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
