'use client';

export default function LoadingPage() {
  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]  overflow-hidden">
      <div className="flex flex-col items-center gap-4">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#098842] border-t-transparent"></div>
        <p className="font-montserrat text-[#686464] text-lg">Carregando...</p>
      </div>
    </div>
  );
}