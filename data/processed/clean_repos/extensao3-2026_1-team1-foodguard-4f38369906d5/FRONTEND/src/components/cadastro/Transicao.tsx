import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import logo from "@/assets/logo.svg";

const TransicaoStep = () => {
    const navigate = useNavigate();

    useEffect(() => {
        const t = setTimeout(() => navigate("/chat"), 4000);
        return () => clearTimeout(t);
    }, [navigate]);

    return (
        <div className="flex flex-col items-center justify-center gap-6 py-16">
            <img
                src={logo}
                alt="FoodGuard"
                className="h-44 w-44 animate-[pulse_2s_ease-in-out_infinite] rounded-full"
            />
            <p className="font-sansita text-2xl font-extrabold text-foodguard-500 sm:text-3xl">
                …Excelente! Estamos quase terminando.
            </p>
            <button
                type="button"
                onClick={() => navigate("/chat")}
                className="h-12 rounded-lg bg-foodguard-500 px-10 font-bold uppercase tracking-wide text-white transition-colors hover:bg-foodguard-500/90"
            >
                Continuar
            </button>
        </div>
    );
};

export default TransicaoStep;
