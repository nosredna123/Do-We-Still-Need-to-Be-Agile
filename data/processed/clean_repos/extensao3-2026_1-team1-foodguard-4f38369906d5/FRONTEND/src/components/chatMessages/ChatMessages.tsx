import { useEffect, useRef } from "react";
import { Stethoscope } from "lucide-react";
import type { Verdict } from "@/models/message.model";
import { VERDICT_META } from "@/lib/verdict";

export type Message = {
    id: string;
    role: "user" | "assistant";
    text: string;
    image?: File;
    imageUrl?: string;
    pending?: boolean;
    verdict?: Verdict | null;
    recommendsDoctor?: boolean;
};

const VerdictBadge = ({ verdict }: { verdict: Verdict }) => {
    const meta = VERDICT_META[verdict];
    return (
        <span
            className={`inline-flex w-fit items-center rounded-full border px-3 py-1 text-xs font-bold uppercase tracking-wide ${meta.className}`}
        >
            {meta.label}
        </span>
    );
};

const DoctorTag = () => (
    <span className="inline-flex w-fit items-center gap-1 rounded-full border border-red-300 bg-red-100 px-3 py-1 text-xs font-bold uppercase tracking-wide text-red-800">
        <Stethoscope className="h-3.5 w-3.5" />
        Procure um médico
    </span>
);

const TypingDots = () => (
    <div className="flex items-center gap-1.5">
        {[0, 1, 2].map((i) => (
            <span
                key={i}
                className="h-2.5 w-2.5 animate-pulse rounded-full bg-foodguard-600"
                style={{ animationDelay: `${i * 0.15}s` }}
            />
        ))}
    </div>
);

const ChatMessages = ({ messages }: { messages: Message[] }) => {
    const endRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    return (
        <div className="flex flex-col gap-4 px-2 py-6">
            {messages.map((m) => {
                if (m.role === "user") {
                    return (
                        <div key={m.id} className="flex flex-col items-end gap-2 animate-fade-in">
                            {m.imageUrl && (
                                <div className="flex h-fit w-fit flex-col items-center justify-center gap-1 rounded-2xl p-2 rounded-se border border-zinc-400 bg-foodguard-500 text-white shadow-sm">
                                    <img
                                        src={m.imageUrl}
                                        alt="Anexo enviado"
                                        className="w-20 h-20 object-cover rounded-xl border border-foodguard-300"
                                    />
                                </div>
                            )}
                            {m.text && (
                                <div className="max-w-[80%] rounded-2xl rounded-se border border-zinc-400 bg-foodguard-500 p-4 text-white whitespace-break-spaces shadow shadow-black/15">
                                    {m.text}
                                </div>
                            )}
                        </div>
                    );
                }

                return (
                    <div key={m.id} className="flex animate-fade-in">
                        {m.pending ? (
                            <div className="flex items-center gap-3 px-2 py-2">
                                <TypingDots />
                                <span className="text-black">Sua mensagem está sendo processada ...</span>
                            </div>
                        ) : (
                            <div className="flex max-w-[85%] flex-col rounded-2xl rounded-ss border border-zinc-400 bg-white px-6 py-5 text-black shadow shadow-black/15">
                                {(m.verdict || m.recommendsDoctor) && (
                                    <div className="mb-3 flex flex-wrap gap-2">
                                        {m.verdict && <VerdictBadge verdict={m.verdict} />}
                                        {m.recommendsDoctor && <DoctorTag />}
                                    </div>
                                )}
                                {m.text.split("\n\n").map((p, i) => (
                                    <p key={`${m.id}-${i}`} className={i > 0 ? "mt-4" : ""}>{p}</p>
                                ))}
                            </div>
                        )}
                    </div>
                );
            })}
            <div ref={endRef} />
        </div>
    );
};

export default ChatMessages;
