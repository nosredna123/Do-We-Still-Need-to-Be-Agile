import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import fotoAristoteles from "@/assets/team/Ari.jpg";
import fotoPedro from "@/assets/team/Otavio.jpeg";
import fotoVictor from "@/assets/team/Timbo.jpeg";
import fotoGabriel from "@/assets/team/Pinheiro.jpeg";
import fotoPaulo from "@/assets/team/Paulo.jpeg";

type Member = {
  name: string;
  role: string;
  initials: string;
  photo?: string;
};

const members: Member[] = [
  {
    name: "Aristóteles Feitosa",
    role: "Desenvolvedor Backend",
    initials: "AF",
    photo: fotoAristoteles,
  },
  {
    name: "Pedro Otávio de Sousa Bezerra",
    role: "Desenvolvedor Frontend",
    initials: "PB",
    photo: fotoPedro,
  },
  {
    name: "Victor Manoel Magalhães Timbó",
    role: "Desenvolvedor Frontend",
    initials: "VT",
    photo: fotoVictor,
  },
  {
    name: "Gabriel Pinheiro",
    role: "Requisitos e Qualidade",
    initials: "GP",
    photo: fotoGabriel,
  },
  {
    name: "Paulo Matheus",
    role: "Requisitos e Qualidade",
    initials: "PM",
    photo: fotoPaulo,
  },
];

export function Team() {
  return (
    <section id="quem-somos" className="min-h-screen py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-wider text-foodguard-500">
            Quem somos
          </p>
          <h2 className="mt-3 font-sansita text-3xl font-extrabold tracking-tight text-black sm:text-4xl">
            O time por trás do FoodGuard
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-base text-zinc-500">
            Um grupo multidisciplinar construindo uma ferramenta que torna
            decisões alimentares mais seguras.
          </p>
        </div>

        <div className="mt-12 grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
          {members.map((m) => (
            <Card
              key={m.name}
              className="flex flex-col items-center gap-4 border-zinc-200 p-6 transition-all hover:-translate-y-1 hover:border-foodguard-400/40 hover:shadow-md"
            >
              <Avatar className="h-20 w-20 ring-2 ring-foodguard-500/20">
                {m.photo ? (
                  <img
                    src={m.photo}
                    alt={m.name}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <AvatarFallback className="bg-foodguard-50 text-base font-semibold text-foodguard-600">
                    {m.initials}
                  </AvatarFallback>
                )}
              </Avatar>
              <div className="text-center">
                <p className="text-sm font-semibold text-black">{m.name}</p>
                <p className="mt-1 text-xs text-zinc-500">{m.role}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
