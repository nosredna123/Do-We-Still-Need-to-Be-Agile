import svgPaths from "../imports/svg-ggi5l4lnb0";
import { imgElement } from "../imports/svg-r8ban";
import imgGeminiGeneratedImageQyyer0Qyyer0Qyye2 from "figma:asset/0aea4b989c5d8b872f22de685ea0c79912f715e8.png";
import { motion } from "motion/react";

function BackgroundChatElement({ additionalClassNames = "" }: { additionalClassNames?: string }) {
  return (
    <div style={{ maskImage: `url('${imgElement}')` }} className={`absolute mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-size-[417.96px_417.96px] mix-blend-overlay ${additionalClassNames}`}>
      <div className="absolute inset-[-53.83%]">
        <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 572 572">
          <g filter="url(#filter0_f_1_1004)" id="Element" style={{ mixBlendMode: "overlay" }}>
            <circle cx="285.515" cy="285.515" fill="url(#paint0_linear_1_1004)" fillOpacity="0.8" r="137.487" />
          </g>
          <defs>
            <filter colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse" height="571.029" id="filter0_f_1_1004" width="571.029" x="0" y="0">
              <feFlood floodOpacity="0" result="BackgroundImageFix" />
              <feBlend in="SourceGraphic" in2="BackgroundImageFix" mode="normal" result="shape" />
              <feGaussianBlur result="effect1_foregroundBlur_1_1004" stdDeviation="74.0138" />
            </filter>
            <linearGradient gradientUnits="userSpaceOnUse" id="paint0_linear_1_1004" x1="423.002" x2="148.028" y1="285.515" y2="285.515">
              <stop stopColor="#4CBB9D" />
              <stop offset="1" stopColor="#69B8CE" />
            </linearGradient>
          </defs>
        </svg>
      </div>
    </div>
  );
}

interface HeroProps {
  onCTAClick?: () => void;
}

export function Hero({ onCTAClick }: HeroProps) {
  return (
    <div className="absolute h-[504px] left-[196px] overflow-clip top-[96px] w-[1528px]" data-name="Section" id="hero">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="absolute left-[531px] size-[465px] top-[-71px]"
        data-name="Gemini_Generated_Image_qyyer0qyyer0qyye 2"
      >
        <motion.img
          whileHover={{ scale: 1.05, rotate: 2 }}
          transition={{ duration: 0.3 }}
          alt=""
          className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full cursor-pointer"
          src={imgGeminiGeneratedImageQyyer0Qyyer0Qyye2}
        />
      </motion.div>
      <div className="absolute h-[504px] left-0 top-0 w-[1528px]" data-name="Container">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute border-2 border-slate-200 border-solid left-[28.09px] size-[151.816px] top-[28.09px]"
          data-name="Container"
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
          className="absolute border-2 border-slate-200 border-solid left-[1343.07px] size-[113.862px] top-[151.07px]"
          data-name="Container"
        />
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
          className="absolute border-2 border-slate-200 border-solid left-[365.43px] size-[113.137px] top-[327.43px]"
          data-name="Container"
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
          className="absolute border-2 border-slate-200 border-solid left-[941.42px] size-[90.51px] top-[154.73px]"
          data-name="Container"
        />
      </div>
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        className="absolute bg-white h-[241px] left-[267px] rounded-[16px] top-[263px] w-[993px]"
        data-name="Prompt Box"
      >
        <div className="box-border content-stretch flex flex-col gap-[10px] h-[241px] items-center justify-center overflow-clip px-[32px] py-[48px] relative rounded-[inherit] w-[993px]">
          <div className="absolute blur-[80.897px] filter left-[calc(50%+0.5px)] opacity-40 size-[417.96px] top-[186px] translate-x-[-50%]" data-name="Background Chat">
            <div className="absolute inset-0 mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[0px] mask-size-[417.96px_417.96px]" data-name="Element" style={{ maskImage: `url('${imgElement}')` }}>
              <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 418 418">
                <circle cx="208.98" cy="208.98" fill="url(#paint0_linear_1_1020)" fillOpacity="0.8" id="Element" r="208.98" />
                <defs>
                  <linearGradient gradientUnits="userSpaceOnUse" id="paint0_linear_1_1020" x1="417.96" x2="0" y1="208.98" y2="208.98">
                    <stop stopColor="#4CBB9D" />
                    <stop offset="1" stopColor="#69B8CE" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <div className="absolute bottom-[48.28%] left-[-40.87%] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[170.813px_163.6px] mask-size-[417.96px_417.96px] right-1/2 top-[-39.14%]" data-name="Element" style={{ maskImage: `url('${imgElement}')` }}>
              <div className="absolute inset-[-32.1%]">
                <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 624 624">
                  <g filter="url(#filter0_f_1_1018)" id="Element">
                    <circle cx="311.797" cy="311.797" fill="url(#paint0_linear_1_1018)" fillOpacity="0.8" r="189.892" />
                  </g>
                  <defs>
                    <filter colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse" height="623.595" id="filter0_f_1_1018" width="623.595" x="0" y="0">
                      <feFlood floodOpacity="0" result="BackgroundImageFix" />
                      <feBlend in="SourceGraphic" in2="BackgroundImageFix" mode="normal" result="shape" />
                      <feGaussianBlur result="effect1_foregroundBlur_1_1018" stdDeviation="60.9525" />
                    </filter>
                    <linearGradient gradientUnits="userSpaceOnUse" id="paint0_linear_1_1018" x1="501.69" x2="121.905" y1="311.798" y2="311.798">
                      <stop stopColor="#4CBB9D" />
                      <stop offset="1" stopColor="#69B8CE" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>
            <BackgroundChatElement additionalClassNames="inset-[17.11%_-43.64%_17.11%_77.85%] mask-position-[-325.378px_-71.492px]" />
            <BackgroundChatElement additionalClassNames="inset-[23.14%_53.56%_11.07%_-19.35%] mask-position-[80.884px_-96.711px]" />
            <div className="absolute inset-[10.51%_4.5%_-2.93%_-2.46%] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[10.272px_-43.918px] mask-size-[417.96px_417.96px] mix-blend-darken" data-name="Element" style={{ maskImage: `url('${imgElement}')` }}>
              <div className="absolute inset-[-13.53%_-12.76%]">
                <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 514 491">
                  <g filter="url(#filter0_f_1_1036)" id="Element" style={{ mixBlendMode: "darken" }}>
                    <path d={svgPaths.p39738b00} fill="url(#paint0_linear_1_1036)" fillOpacity="0.8" />
                  </g>
                  <defs>
                    <filter colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse" height="490.771" id="filter0_f_1_1036" width="513.905" x="0" y="0">
                      <feFlood floodOpacity="0" result="BackgroundImageFix" />
                      <feBlend in="SourceGraphic" in2="BackgroundImageFix" mode="normal" result="shape" />
                      <feGaussianBlur result="effect1_foregroundBlur_1_1036" stdDeviation="26.1225" />
                    </filter>
                    <linearGradient gradientUnits="userSpaceOnUse" id="paint0_linear_1_1036" x1="461.66" x2="52.245" y1="245.386" y2="245.386">
                      <stop stopColor="#4CBB9D" />
                      <stop offset="1" stopColor="#69B8CE" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>
          </div>
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="content-stretch flex flex-col gap-[24px] items-center max-w-[400px] relative shrink-0 w-[400px]"
            data-name="Top Part"
          >
            <div className="content-stretch flex flex-col gap-[6px] items-center not-italic relative shrink-0 text-center w-full" data-name="Page Title Wrapper">
              <p className="font-['Inter:Medium',sans-serif] font-medium leading-[1.3] relative shrink-0 text-[#19213d] text-[22px] text-nowrap whitespace-pre">Olá! Sou Buliçoso, seu Assistente de Saúde Virtual!</p>
              <p className="font-['Inter:Regular',sans-serif] font-normal leading-[1.5] min-w-full relative shrink-0 text-[#666f8d] text-[14px] w-[min-content]"></p>
            </div>
            <div className="box-border content-stretch flex flex-col items-end pb-px pt-0 px-0 relative shrink-0 w-full" data-name="Prompt Box">
              <div className="bg-white mb-[-1px] relative rounded-[16px] shrink-0 w-full" data-name="Box Wrapper">
                <div aria-hidden="true" className="absolute border border-[#f0f2f5] border-solid inset-0 pointer-events-none rounded-[16px] shadow-[0px_2px_4px_0px_rgba(25,33,61,0.08)]" />
                <div className="flex flex-row items-center size-full">
                  <div className="box-border content-stretch flex items-center justify-between pl-[16px] pr-[8px] py-[8px] relative w-full">
                    <div className="content-stretch flex gap-[8px] items-center relative shrink-0" data-name="Promp box">
                      <p className="font-['Inter:Regular',sans-serif] font-normal leading-[1.5] not-italic relative shrink-0 text-[#666f8d] text-[14px] text-nowrap whitespace-pre">Como posso ajudá-lo hoje?</p>
                    </div>
                    <div className="content-stretch flex gap-[16px] items-center justify-end relative shrink-0" data-name="Prompt Box">
                      <motion.div
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        className="bg-[#69b8ce] relative rounded-[8px] shrink-0 size-[42px] cursor-pointer"
                        data-name="Primary Button"
                        onClick={onCTAClick}
                      >
                        <div className="content-stretch flex items-center justify-center overflow-clip relative rounded-[inherit] size-[42px]">
                          <div className="relative shrink-0 size-[20px]" data-name="Filled/Send">
                            <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
                              <g id="Filled/Send">
                                <path d={svgPaths.p1850be00} fill="white" id="Element" />
                              </g>
                            </svg>
                          </div>
                        </div>
                        <div className="absolute inset-0 pointer-events-none shadow-[0px_-2px_0.3px_0px_inset_rgba(14,56,125,0.18),0px_2px_1px_0px_inset_rgba(255,255,255,0.22)]" />
                        <div aria-hidden="true" className="absolute border border-[#69b8ce] border-solid inset-0 pointer-events-none rounded-[8px] shadow-[0px_2px_5px_0px_rgba(20,88,201,0.17)]" />
                      </motion.div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
        <div aria-hidden="true" className="absolute border border-[#e3e6ea] border-solid inset-0 pointer-events-none rounded-[16px] shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]" />
      </motion.div>
      <div className="absolute h-[344px] left-[428px] top-[80px] w-[672px]" data-name="Container" />
    </div>
  );
}