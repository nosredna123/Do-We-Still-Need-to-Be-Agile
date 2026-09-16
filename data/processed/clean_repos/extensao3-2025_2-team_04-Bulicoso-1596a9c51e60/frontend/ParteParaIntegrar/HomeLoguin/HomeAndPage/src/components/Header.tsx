import imgLoginRemovebgPreview1 from "figma:asset/5a9ffecd1b54842b99dc6316ab2339e739dbf3ea.png";
import { motion } from "motion/react";

interface HeaderProps {
  onNavigate?: (page: 'home' | 'login') => void;
  onScrollTo?: (section: string) => void;
}

export function Header({ onNavigate, onScrollTo }: HeaderProps) {
  return (
    <motion.div
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="absolute box-border content-stretch flex flex-col h-[97px] items-start left-[196px] pb-px pt-[16px] px-[124px] top-[8px] w-[1528px] z-50"
      data-name="Header"
    >
      <div aria-hidden="true" className="absolute border-[0px_0px_1px] border-slate-200 border-solid inset-0 pointer-events-none" />
      <div className="content-stretch flex h-[80px] items-center justify-between relative shrink-0 w-full" data-name="Navigation">
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="h-[52px] relative shrink-0 w-[227px] cursor-pointer"
          data-name="login-removebg-preview 1"
          onClick={() => onNavigate?.('home')}
        >
          <div className="absolute bg-clip-padding border-0 border-[transparent] border-solid box-border inset-0 overflow-hidden pointer-events-none">
            <img alt="" className="absolute h-[438.6%] left-0 max-w-none top-[-169.3%] w-full" src={imgLoginRemovebgPreview1} />
          </div>
          <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[52px] w-[227px]" />
        </motion.div>
        <div className="h-[24px] relative shrink-0 w-[581px]" data-name="Container">
          <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex gap-[32px] h-[24px] items-center relative w-[581px]">
            <motion.div
              whileHover={{ y: -2 }}
              className="h-[24px] relative shrink-0 w-[56.734px] cursor-pointer"
              data-name="Link"
              onClick={() => onScrollTo?.('hero')}
            >
              <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[56.734px]">
                <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#45556c] text-[16px] text-nowrap top-[-2px] whitespace-pre hover:text-[#69b8ce] transition-colors">Chatbot</p>
              </div>
            </motion.div>
            <motion.div
              whileHover={{ y: -2 }}
              className="basis-0 grow h-[24px] min-h-px min-w-px relative shrink-0 cursor-pointer"
              data-name="Link"
              onClick={() => onScrollTo?.('features')}
            >
              <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-full">
                <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#45556c] text-[16px] text-nowrap top-[-2px] whitespace-pre hover:text-[#69b8ce] transition-colors">Como funciona?</p>
              </div>
            </motion.div>
            <motion.div
              whileHover={{ y: -2 }}
              className="h-[24px] relative shrink-0 w-[87px] cursor-pointer"
              data-name="Link"
              onClick={() => onScrollTo?.('tools')}
            >
              <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[87px]">
                <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#45556c] text-[16px] text-nowrap top-[-2px] whitespace-pre hover:text-[#69b8ce] transition-colors">Ferramentas</p>
              </div>
            </motion.div>
            <motion.div
              whileHover={{ y: -2 }}
              className="h-[24px] relative shrink-0 w-[93.766px] cursor-pointer"
              data-name="Link"
              onClick={() => onScrollTo?.('team')}
            >
              <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[93.766px]">
                <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#45556c] text-[16px] text-nowrap top-[-2px] whitespace-pre hover:text-[#69b8ce] transition-colors">Quem somos</p>
              </div>
            </motion.div>
            <motion.div
              whileHover={{ y: -2 }}
              className="h-[24px] relative shrink-0 w-[93.766px] cursor-pointer"
              data-name="Link"
              onClick={() => onNavigate?.('login')}
            >
              <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[93.766px]">
                <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#45556c] text-[16px] text-nowrap top-[-2px] whitespace-pre hover:text-[#69b8ce] transition-colors">Login</p>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}