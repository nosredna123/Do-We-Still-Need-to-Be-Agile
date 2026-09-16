import { AuthPanel } from "../components/AuthPanel";
import imgGeminiGeneratedImageEmqzvbemqzvbemqz1 from "figma:asset/56af3b125ae6be0fb7d9f1c787973918f08b0062.png";
import { motion } from "motion/react";

interface LoginPageProps {
  onGoogleLogin?: () => void;
}

export default function LoginPage({ onGoogleLogin }: LoginPageProps) {
  return (
    <div className="relative w-screen h-screen overflow-hidden" data-name="Login">
      <div className="absolute inset-0" data-name="Tela de login">
        <div className="absolute inset-0">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 1928 1088">
            <g id="Tela de login">
              <g filter="url(#filter0_d_1_976)" id="Rectangle 1">
                <path d="M4 0H1924V1080H974H4V0Z" fill="white" />
              </g>
            </g>
            <defs>
              <filter colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse" height="1088" id="filter0_d_1_976" width="1928" x="0" y="0">
                <feFlood floodOpacity="0" result="BackgroundImageFix" />
                <feColorMatrix in="SourceAlpha" result="hardAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" />
                <feOffset dy="4" />
                <feGaussianBlur stdDeviation="2" />
                <feComposite in2="hardAlpha" operator="out" />
                <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0" />
                <feBlend in2="BackgroundImageFix" mode="normal" result="effect1_dropShadow_1_976" />
                <feBlend in="SourceGraphic" in2="effect1_dropShadow_1_976" mode="normal" result="shape" />
              </filter>
            </defs>
          </svg>
        </div>
      </div>
      <motion.div
        initial={{ scale: 0.8, opacity: 0, rotate: -10 }}
        animate={{ scale: 1, opacity: 1, rotate: 0 }}
        transition={{ duration: 0.8, type: "spring", bounce: 0.4 }}
        className="absolute left-[8%] w-[42vw] h-[42vw] top-[50%] -translate-y-[50%]"
        data-name="Gemini_Generated_Image_emqzvbemqzvbemqz 1"
      >
        <motion.img
          whileHover={{ scale: 1.05, rotate: 2 }}
          transition={{ duration: 0.3 }}
          alt=""
          className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full cursor-pointer"
          src={imgGeminiGeneratedImageEmqzvbemqzvbemqz1}
        />
      </motion.div>
      <motion.div
        initial={{ x: 100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="absolute flex h-full items-center justify-center right-0 top-0 w-[41.15%]"
      >
        <div className="flex-none rotate-[180deg] h-full w-full">
          <header className="block h-full relative w-full" data-name="Header 1" style={{
            background: 'linear-gradient(180deg, #4CBB9D 0%, #69B8CE 100%)'
          }} />
        </div>
      </motion.div>
      <AuthPanel onGoogleLogin={onGoogleLogin} />
    </div>
  );
}