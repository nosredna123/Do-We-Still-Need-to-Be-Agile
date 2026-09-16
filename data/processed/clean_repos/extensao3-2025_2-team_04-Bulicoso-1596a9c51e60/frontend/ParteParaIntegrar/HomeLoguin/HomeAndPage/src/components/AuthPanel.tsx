import { SocialButton } from "./SocialButton";
import { motion } from "motion/react";

interface AuthPanelProps {
  onGoogleLogin?: () => void;
}

export function AuthPanel({ onGoogleLogin }: AuthPanelProps) {
  return (
    <div className="absolute flex flex-col right-[8%] top-[50%] -translate-y-[50%] w-[25vw] gap-[2vh]">
      <motion.div 
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="flex flex-col font-['Arimo:Regular',sans-serif] font-normal leading-[1.2] text-[2.5vw] text-black tracking-[-1px]"
      >
        <p className="mb-0">{`Precisa de ajuda? `}</p>
        <p className="mb-0">{`Não sabe como usar um medicamento? `}</p>
        <p className="mb-0">Deixe que eu dou conta.</p>
      </motion.div>
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.3 }}
        className="flex flex-col font-['Arimo:Regular',sans-serif] font-normal leading-[1.5] text-[#1e1e1e] text-[1.25vw] tracking-[-0.5px]"
      >
        <p className="mb-0">
          </p>
      </motion.div>
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        className="flex flex-col font-['Arimo:Regular',sans-serif] font-normal leading-[1.5] text-[#1e1e1e] text-[1.25vw] tracking-[-0.5px]"
      >
        <p className="mb-0">Entre através da sua conta google:</p>
      </motion.div>
      <SocialButton onClick={onGoogleLogin} />
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.8 }}
        className="flex flex-col font-['Inter:Regular',sans-serif] font-normal leading-[1.5] not-italic text-[#1e1e1e] text-[1vw] text-center tracking-[-0.4px] mt-[4vh]"
      >
      </motion.div>
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.9 }}
        className="[text-shadow:rgba(0,0,0,0.25)_0px_4px_4px] flex flex-col font-['Inter:Regular',sans-serif] font-normal leading-[1.5] not-italic text-[1vw] text-black tracking-[-0.4px]"
      >
        <p className="mb-0">
          <span>{`Termos e Condições `}</span>
          <span className="text-[#1e1e1e]">e</span>
          <span>{` Declaroções sobre Privacidade e cookies`}</span>
        </p>
      </motion.div>
    </div>
  );
}