// components/background/index.tsx
import { ReactNode } from 'react';

interface BackgroundProps {
  children: ReactNode;
}

export function Background({ children }: BackgroundProps) {
  return (
    <div className="min-h-screen flex relative">
      <div 
        className="flex-1 bg-no-repeat bg-[#098842] bg-cover"
        style={{ 
          backgroundImage: `url('/imagens/cafelivro.png')`,
          backgroundSize: '90%',
          backgroundPosition: 'left center',
          backgroundRepeat: 'no-repeat'
        }}
      >
        <div 
          className="fixed"
          style={{
            top: '16px',
            left: '16px',
            zIndex: 50,
          }}
        >
          <img 
            src="/imagens/Logo.png" 
            alt="EstudaAI" 
            style={{

              width: '180px',
              height: '55px',
              objectFit: 'contain'
            }}
          />
        </div>
      </div>
      <div className="absolute right-0 top-0 bottom-0 w-3/5 flex">
        <div 
          className="absolute inset-0 bg-no-repeat"
          style={{ 
            backgroundImage: `url('/cafelivro.png')`,
            backgroundSize: '50%',
            backgroundPosition: 'left center',
            backgroundRepeat: 'no-repeat'
          }}
        />
        
        <div className="bg-white rounded-tl-[5%] rounded-bl-[5%] flex justify-center items-center p-8 w-full relative z-10">
          <div className="w-full max-w-md">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}