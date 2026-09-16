import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { useNavigate } from "react-router-dom";
import { LoginWithGoogle } from "../services/LoginWithGoogle";
import { ShieldCheck, Zap, Lock } from "lucide-react";

const floatingCards = [
  { question: "Capital do Japão?", answer: "Tóquio", rotate: "-7deg", x: "-340px", y: "-60px" },
  { question: "Quem escreveu Dom Quixote?", answer: "Miguel de Cervantes", rotate: "5deg", x: "330px", y: "-80px" },
  { question: "Velocidade da luz?", answer: "299.792 km/s", rotate: "-5deg", x: "-310px", y: "140px" },
  { question: "Fórmula da glicose?", answer: "C₆H₁₂O₆", rotate: "8deg", x: "300px", y: "160px" },
];

export default function Login() {
  const pageRef = useRef(null);
  const cardRefs = useRef([]);
  const formCardRef = useRef(null);
  const logoRef = useRef(null);
  const titleRef = useRef(null);
  const subtitleRef = useRef(null);
  const btnRef = useRef(null);
  const badgesRef = useRef(null);
  const cursorGlowRef = useRef(null);

  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      await LoginWithGoogle();
      navigate("/weeks");
    } catch (error) {
      console.error("Erro ao entrar:", error);
    }
  };

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.set(
        [logoRef.current, formCardRef.current, titleRef.current, subtitleRef.current, btnRef.current, badgesRef.current].filter(Boolean),
        { opacity: 0, y: 20 }
      );
      gsap.set(cardRefs.current.filter(Boolean), { opacity: 0, scale: 0.5 });

      const onMove = (e) => {
        gsap.to(cursorGlowRef.current, {
          x: e.clientX - 250,
          y: e.clientY - 250,
          duration: 1.4,
          ease: "power3.out",
        });
      };
      window.addEventListener("mousemove", onMove);

      const tl = gsap.timeline({ defaults: { ease: "power4.out" } });
      tl.to(logoRef.current, { y: 0, opacity: 1, duration: 0.6 })
        .to(formCardRef.current, { y: 0, opacity: 1, scale: 1, duration: 0.9 }, "-=0.3")
        .to(titleRef.current, { y: 0, opacity: 1, duration: 0.6 }, "-=0.6")
        .to(subtitleRef.current, { y: 0, opacity: 1, duration: 0.5 }, "-=0.45")
        .to(btnRef.current, { y: 0, opacity: 1, duration: 0.5 }, "-=0.3")
        .to(badgesRef.current, { y: 0, opacity: 1, duration: 0.45 }, "-=0.2")
        .to(cardRefs.current.filter(Boolean), {
          scale: 1, opacity: 1, duration: 0.8, stagger: 0.15, ease: "back.out(1.7)",
        }, 0.2);

      cardRefs.current.filter(Boolean).forEach((card, i) => {
        gsap.to(card, {
          y: `+=${12 + i * 3}`,
          rotation: `+=${1.5 + i * 0.8}`,
          duration: 2.8 + i * 0.5,
          repeat: -1,
          yoyo: true,
          ease: "sine.inOut",
          delay: i * 0.4,
        });
      });

      const onParallax = (e) => {
        const cx = window.innerWidth / 2;
        const cy = window.innerHeight / 2;
        const dx = (e.clientX - cx) / cx;
        const dy = (e.clientY - cy) / cy;
        cardRefs.current.filter(Boolean).forEach((card, i) => {
          gsap.to(card, {
            x: `+=${dx * (i + 1) * 10}`,
            y: `+=${dy * (i + 1) * 10}`,
            duration: 1.6,
            ease: "power2.out",
            overwrite: "auto",
          });
        });
        gsap.to(formCardRef.current, {
          rotateX: (dy * 3).toFixed(2),
          rotateY: (-dx * 3).toFixed(2),
          duration: 1.2,
          ease: "power2.out",
        });
      };
      window.addEventListener("mousemove", onParallax);

      return () => {
        window.removeEventListener("mousemove", onMove);
        window.removeEventListener("mousemove", onParallax);
      };
    }, pageRef);

    return () => ctx.revert();
  }, []);

  return (
    <div
      ref={pageRef}
      className="relative min-h-screen bg-[#f5f5ec] flex flex-col items-center justify-center overflow-hidden px-4"
    >
      {/* Cursor glow */}
      <div
        ref={cursorGlowRef}
        className="pointer-events-none fixed w-[500px] h-[500px] rounded-full z-0"
        style={{
          background: "radial-gradient(circle, rgba(45,106,79,0.10) 0%, transparent 70%)",
          top: 0, left: 0,
        }}
      />

      {/* Dot grid */}
      <div
        className="absolute inset-0 z-0 opacity-40"
        style={{
          backgroundImage: "radial-gradient(circle, #b7d5c4 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />

      {/* Decorative blobs */}
      <div className="absolute top-[-80px] left-[-80px] w-72 h-72 rounded-full bg-[#d8eddf] opacity-40 blur-3xl z-0" />
      <div className="absolute bottom-[-60px] right-[-60px] w-64 h-64 rounded-full bg-[#c8e6d4] opacity-30 blur-3xl z-0" />

      {/* Floating flashcards */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
        {floatingCards.map((card, i) => (
          <div
            key={i}
            ref={(el) => (cardRefs.current[i] = el)}
            className="absolute bg-white rounded-2xl shadow-md border border-gray-100 p-4 w-44 text-left"
            style={{ transform: `rotate(${card.rotate})`, translate: `${card.x} ${card.y}` }}
          >
            <p className="text-[10px] font-semibold text-[#2d6a4f] uppercase tracking-widest mb-1">Flashcard</p>
            <p className="text-[12px] font-bold text-gray-700 mb-2 leading-snug">{card.question}</p>
            <div className="border-t border-dashed border-gray-200 pt-2">
              <p className="text-[11px] text-gray-400">{card.answer}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Logo */}
      <div ref={logoRef} className="relative z-20 mb-8 flex items-center gap-2 text-gray-800 font-extrabold text-xl">
        REVISAI
      </div>

      {/* Form card */}
      <div
        ref={formCardRef}
        className="relative z-20 w-full max-w-lg bg-white rounded-3xl border border-gray-100 shadow-xl px-16 py-20"
        style={{ perspective: "1000px", transformStyle: "preserve-3d" }}
      >
        {/* Green accent line */}
        <div className="absolute top-0 left-8 right-8 h-[3px] bg-gradient-to-r from-[#2d6a4f] via-[#52b788] to-[#2d6a4f] rounded-full" />

        {/* Shield icon */}
        <div className="flex justify-center mb-6">
          <ShieldCheck className="w-14 h-14 text-[#2d6a4f]" strokeWidth={1.5} />
        </div>

        <div ref={titleRef} className="mb-3 text-center">
          <h1 className="text-4xl font-extrabold text-gray-800">Bem-vindo!</h1>
        </div>
        <p ref={subtitleRef} className="text-base text-gray-400 mb-10 text-center">
          Entre com sua conta Google para continuar.
        </p>

        {/* Google button */}
        <button
          ref={btnRef}
          onClick={handleLogin}
          className="w-full py-5 rounded-xl bg-white border border-gray-200 text-gray-700 font-semibold text-lg hover:bg-gray-50 hover:border-gray-300 active:scale-95 transition-all flex items-center justify-center gap-3 shadow-sm"
        >
          <svg width="24" height="24" viewBox="0 0 18 18" aria-hidden="true">
            <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 0 1-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" />
            <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" />
            <path fill="#FBBC05" d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" />
            <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 6.29C4.672 4.163 6.656 3.58 9 3.58z" />
          </svg>
          Entrar com Google
        </button>

        {/* Divider + trust badges */}
        <div ref={badgesRef}>
          <div className="flex items-center gap-3 mt-8 mb-5">
            <div className="flex-1 h-px bg-gray-100" />
            <span className="text-[11px] text-gray-300 tracking-wide">acesso seguro</span>
            <div className="flex-1 h-px bg-gray-100" />
          </div>
          <div className="flex items-center justify-center gap-8">
            <div className="flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-[#52b788]" />
              <span className="text-xs text-gray-400">Seguro</span>
            </div>
            <div className="w-px h-3 bg-gray-200" />
            <div className="flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-[#52b788]" />
              <span className="text-xs text-gray-400">Rápido</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom copy */}
      <p className="relative z-20 mt-6 text-xs text-[#2d6a4f]">
        © 2025 RevisAI · Todos os direitos reservados
      </p>
    </div>
  );
}
