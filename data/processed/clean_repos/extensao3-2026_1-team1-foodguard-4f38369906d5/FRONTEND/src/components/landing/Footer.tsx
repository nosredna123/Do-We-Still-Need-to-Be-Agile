const CURRENT_YEAR = new Date().getFullYear();

export function Footer() {
  return (
    <footer className="border-t border-zinc-200 bg-slate-100">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-6 py-8 sm:flex-row">
        <p className="font-sansita text-lg font-extrabold text-black">
          FoodGuard
        </p>
        <p className="text-xs text-zinc-500">
          © {CURRENT_YEAR} FoodGuard. Todos os direitos reservados.
        </p>
      </div>
    </footer>
  );
}
