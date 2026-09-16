import Link from "next/link";
import Image from "next/image";

export function Navbar() {
    return(
        <div className="flex justify-between bg-white px-6 py-4 text-[#494949] drop-shadow">
                <Link href="/homepage" className="flex items-center gap-3">
                    <Image 
                        src="/imagens/chapeu.svg"
                        width={30}
                        height={30}
                        alt="Logo"
                    />
                    <div className="flex items-baseline gap-0">
                        <span className="text-xl text-[#494949] font-bold">Estuda</span>
                        <span className="text-xl text-[#098842] font-bold">AI</span>
                    </div>
                </Link>
                <nav className="flex items-center gap-6">
                    <Link href="/reminders" className="flex items-center gap-2 pr-6">
                        <span><img src="/imagens/lembretes.svg" alt="Lembretes" className="w-5 h-5"/></span>
                        <span className="text-sm text-[#494949] hover:text-[#098842]/80 font-medium">Lembretes</span>
                    </Link>
                </nav>
        </div>
    );
}