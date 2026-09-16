import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const floatingCards = [
  { question: "O que é um requisito funcional?", answer: "Descreve o que o sistema deve fazer (funcionalidades).", rotate: "-8deg", x: "-280px", y: "-190px", delay: 0 },
  { question: "O que é o modelo Cascata?", answer: "Modelo sequencial onde cada fase depende da conclusão da anterior.", rotate: "6deg", x: "280px", y: "-200px", delay: 0.2 },
  { question: "O que é teste de software?", answer: "Processo de verificar se o sistema atende aos requisitos e identificar defeitos.", rotate: "9deg", x: "200px", y: "250px", delay: 0.6 },
  { question: "O que é Git?", answer: "Sistema distribuído de controle de versão.", rotate: "-4deg", x: "-200px", y: "240px", delay: 0.4 },

];

export default function Hero() {
  const heroRef = useRef(null);
  const badgeRef = useRef(null);
  const titleLine1Ref = useRef(null);
  const titleLine2Ref = useRef(null);
  const subtitleRef = useRef(null);
  const cardsContainerRef = useRef(null);
  const cardRefs = useRef([]);
  const bgDotsRef = useRef(null);
  const cursorGlowRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // ── Cursor glow ──
      const onMouseMove = (e) => {
        gsap.to(cursorGlowRef.current, {
          x: e.clientX - 200,
          y: e.clientY - 200,
          duration: 1.2,
          ease: "power3.out",
        });
      };
      window.addEventListener("mousemove", onMouseMove);

      // ── Entrance timeline ──
      const tl = gsap.timeline({ defaults: { ease: "power4.out" } });

      // Badge drop
      tl.from(badgeRef.current, {
        y: -30,
        opacity: 0,
        duration: 0.7,
      })
        // Title word by word
        .from(
          titleLine1Ref.current,
          { y: 80, opacity: 0, duration: 0.9, skewY: 4 },
          "-=0.3"
        )
        .from(
          titleLine2Ref.current,
          { y: 80, opacity: 0, duration: 0.9, skewY: 4 },
          "-=0.65"
        )
        // Subtitle
        .from(
          subtitleRef.current,
          { y: 30, opacity: 0, duration: 0.7 },
          "-=0.5"
        )
        // Cards stagger in
        .from(
          cardRefs.current,
          {
            scale: 0.6,
            opacity: 0,
            duration: 0.8,
            stagger: 0.15,
            ease: "back.out(1.7)",
          },
          "-=0.5"
        );

      // ── Floating loop per card ──
      cardRefs.current.forEach((card, i) => {
        gsap.to(card, {
          y: `+=${10 + i * 4}`,
          rotation: `+=${2 + i}`,
          duration: 2.5 + i * 0.4,
          repeat: -1,
          yoyo: true,
          ease: "sine.inOut",
          delay: i * 0.3,
        });
      });

      // ── Parallax cards on mouse move ──
      const onMouseParallax = (e) => {
        const cx = window.innerWidth / 2;
        const cy = window.innerHeight / 2;
        const dx = (e.clientX - cx) / cx;
        const dy = (e.clientY - cy) / cy;

        cardRefs.current.forEach((card, i) => {
          const depth = (i + 1) * 8;
          gsap.to(card, {
            x: `+=${dx * depth}`,
            y: `+=${dy * depth}`,
            duration: 1.5,
            ease: "power2.out",
            overwrite: "auto",
          });
        });
      };
      window.addEventListener("mousemove", onMouseParallax);

      // ── Background dots subtle float ──
      gsap.to(bgDotsRef.current, {
        backgroundPosition: "40px 40px",
        duration: 8,
        repeat: -1,
        ease: "none",
      });

      return () => {
        window.removeEventListener("mousemove", onMouseMove);
        window.removeEventListener("mousemove", onMouseParallax);
      };
    }, heroRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={heroRef}
      className="relative flex flex-col items-center justify-center text-center min-h-[calc(100vh-65px)] bg-[#f5f5ec] px-4 overflow-hidden"
    >
      {/* Cursor glow */}
      <div
        ref={cursorGlowRef}
        className="pointer-events-none fixed w-[400px] h-[400px] rounded-full z-0"
        style={{
          background:
            "radial-gradient(circle, rgba(45,106,79,0.10) 0%, transparent 70%)",
          top: 0,
          left: 0,
        }}
      />

      {/* Background dot grid */}
      <div
        ref={bgDotsRef}
        className="absolute inset-0 z-0 opacity-40"
        style={{
          backgroundImage:
            "radial-gradient(circle, #b7d5c4 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />

      {/* Floating cards */}
      <div
        ref={cardsContainerRef}
        className="absolute inset-0 flex items-center justify-center pointer-events-none z-10"
      >
        {floatingCards.map((card, i) => (
          <div
            key={i}
            ref={(el) => (cardRefs.current[i] = el)}
            className="absolute bg-white rounded-2xl shadow-lg border border-gray-100 p-4 w-48 text-left"
            style={{
              transform: `rotate(${card.rotate})`,
              translate: `${card.x} ${card.y}`,
            }}
          >
            <p className="text-[11px] font-semibold text-[#2d6a4f] uppercase tracking-wide mb-1">
              Flashcard
            </p>
            <p className="text-[13px] font-bold text-gray-700 mb-2 leading-snug">
              {card.question}
            </p>
            <div className="border-t border-dashed border-gray-200 pt-2">
              <p className="text-[12px] text-gray-500">{card.answer}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Content */}
      <div className="relative z-20 flex flex-col items-center">
        <span
          ref={badgeRef}
          className="mb-6 inline-flex items-center gap-2 bg-white border border-gray-200 text-gray-600 text-sm px-4 py-1.5 rounded-full shadow-sm"
        >
          ✨ Estudo inteligente com IA
        </span>

        <h1 className="text-5xl md:text-6xl font-extrabold text-gray-800 leading-tight mb-4 overflow-hidden">
          <div ref={titleLine1Ref} className="block">
            Aprenda mais,
          </div>
          <div ref={titleLine2Ref} className="block text-[#2d6a4f]">
            esqueça menos.
          </div>
        </h1>

        <p
          ref={subtitleRef}
          className="text-gray-500 text-lg max-w-lg mb-10"
        >
          O RevisAI gera flashcards com inteligência artificial e organiza seu
          ciclo de revisão semanal para fixar o conteúdo de verdade.
        </p>

      </div>
    </section>
  );
}