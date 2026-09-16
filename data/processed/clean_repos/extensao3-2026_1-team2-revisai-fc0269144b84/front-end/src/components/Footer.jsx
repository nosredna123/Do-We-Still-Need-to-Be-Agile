const FooterLink = ({ href, children }) => (
  <a
    href={href}
    className="text-gray-400 hover:text-[#2d6a4f] transition-colors duration-200 text-sm"
  >
    {children}
  </a>
);

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="bg-[#f5f5ec] border-t border-gray-200 relative overflow-hidden">
      {/* Dot grid */}
      <div
        className="absolute inset-0 opacity-20 pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle, #b7d5c4 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />

      {/* Blob decorativo */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-32 bg-[#2d6a4f]/5 blur-3xl rounded-full pointer-events-none" />

      <div className="relative z-10 max-w-6xl mx-auto px-8 py-14">

        {/* Top row */}
        <div className="flex flex-col md:flex-row justify-between items-start gap-10 mb-12">

          {/* Brand */}
          <div className="max-w-xs">
            <div className="flex items-center gap-2 font-extrabold text-gray-800 text-lg mb-3">
              🤖 REVISAI
            </div>
            <p className="text-gray-400 text-sm leading-relaxed">
              Aprenda mais, esqueça menos. Flashcards inteligentes gerados por IA
              para fixar o conteúdo de verdade.
            </p>

            {/* Disciplina badge */}
            <div className="mt-4 inline-flex items-center gap-2 bg-[#2d6a4f]/10 border border-[#2d6a4f]/20 text-[#2d6a4f] text-xs font-semibold px-3 py-1.5 rounded-full">
              🎓 Projeto da disciplina de Extensão III
            </div>
          </div>

          {/* Links */}
          <div className="flex flex-wrap gap-12">
            <div>
              <p className="text-gray-700 font-bold text-sm mb-4 uppercase tracking-wider">
                Produto
              </p>
              <div className="flex flex-col gap-2.5">
                <FooterLink href="#">Como funciona</FooterLink>
                <FooterLink href="#">Funcionalidades</FooterLink>
                <FooterLink href="#">Preços</FooterLink>
                <FooterLink href="#">FAQ</FooterLink>
              </div>
            </div>

            <div>
              <p className="text-gray-700 font-bold text-sm mb-4 uppercase tracking-wider">
                Legal
              </p>
              <div className="flex flex-col gap-2.5">
                <FooterLink href="#">Termos de Uso</FooterLink>
                <FooterLink href="#">Privacidade</FooterLink>
                <FooterLink href="#">Cookies</FooterLink>
              </div>
            </div>

            <div>
              <p className="text-gray-700 font-bold text-sm mb-4 uppercase tracking-wider">
                Contato
              </p>
              <div className="flex flex-col gap-2.5">
                <FooterLink href="mailto:contato@revisai.com.br">
                  contato@revisai.com.br
                </FooterLink>
                <FooterLink href="#">Instagram</FooterLink>
                <FooterLink href="#">LinkedIn</FooterLink>
              </div>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="w-full h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent mb-8" />

        {/* Bottom row */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-center">
          <p className="text-gray-400 text-xs leading-relaxed">
            © {year} <span className="font-semibold text-gray-500">RevisAI</span>. Todos os direitos reservados. <br className="md:hidden" />
            Desenvolvido como projeto de extensão universitária —{" "}
            <span className="text-[#2d6a4f] font-semibold">Extensão III</span>.
          </p>

          <div className="flex items-center gap-1.5 text-xs text-gray-400">
            <span>Feito com</span>
            <span className="text-red-400">♥</span>
            <span>e muito café ☕ pelos alunos do</span>
            <span className="font-semibold text-gray-500">RevisAI Team</span>
          </div>
        </div>

        {/* IAs credit — easter egg sutil */}
        <p className="text-center text-[11px] text-gray-800 mt-4">
          Com uma ajudinha de 🤖 Claude · ✨ Gemini · 💜 Lovable
        </p>

      </div>
    </footer>
  );
}