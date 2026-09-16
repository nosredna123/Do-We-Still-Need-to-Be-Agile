import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import logo from "@/assets/logo.svg";

interface AuthLayoutProps {
    children: ReactNode;
    wide?: boolean;
}

const AuthLayout = ({ children, wide = false }: AuthLayoutProps) => {
    return (
        <div className="min-h-screen bg-slate-100 flex items-center justify-center px-6 py-10">
            <div className={`flex w-full ${wide ? "max-w-3xl" : "max-w-xl"} flex-col items-center gap-3`}>
                <Link to="/" className="flex items-center gap-3">
                    <img src={logo} alt="FoodGuard" className="h-16 w-16 rounded-full" />
                    <span className="font-sansita text-6xl font-bold text-black">
                        FoodGuard
                    </span>
                </Link>
                <div className="w-full flex flex-col animate-fade-in rounded-2xl border border-zinc-500 bg-white gap-y-12 p-8 shadow-md sm:p-12">
                    {children}
                </div>
            </div>
        </div>
    );
};

export default AuthLayout;
