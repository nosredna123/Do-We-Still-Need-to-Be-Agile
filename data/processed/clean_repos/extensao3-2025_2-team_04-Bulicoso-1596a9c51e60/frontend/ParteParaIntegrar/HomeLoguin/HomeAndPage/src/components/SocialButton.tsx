import svgPaths from "../imports/svg-myd3g6l33v";
import { motion } from "motion/react";

interface SocialButtonProps {
  onClick?: () => void;
}

export function SocialButton({ onClick }: SocialButtonProps) {
  return (
    <motion.div 
      whileHover={{ scale: 1.05, y: -5 }}
      whileTap={{ scale: 0.95 }}
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6, delay: 0.6 }}
      className="bg-white box-border content-stretch flex gap-[0.5vw] items-center px-[1.5vw] py-[0.75vw] rounded-[0.5vw] w-full cursor-pointer" 
      onClick={onClick}
    >
      <div aria-hidden="true" className="absolute border border-black border-solid inset-0 pointer-events-none rounded-[0.5vw]" />
      <div className="h-[2vw] relative shrink-0 w-[1.5vw]" data-name="Group">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 22 28">
          <g id="Group">
            <path d={svgPaths.p21f19680} fill="#4280EF" id="Vector" />
            <path d={svgPaths.p210a5c00} fill="#34A353" id="Vector_2" />
            <path d={svgPaths.pc6ec00} fill="#F6B704" id="Vector_3" />
            <path d={svgPaths.p35d15200} fill="#E54335" id="Vector_4" />
          </g>
        </svg>
      </div>
      <div className="flex-1 flex items-center justify-center">
        <p className="font-['Inter:Medium',sans-serif] font-medium leading-[1.8] not-italic text-[1vw] text-black text-center mb-0">Continuar com Google</p>
      </div>
    </motion.div>
  );
}