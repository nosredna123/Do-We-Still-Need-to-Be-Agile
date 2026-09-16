import svgPaths from "../imports/svg-ggi5l4lnb0";
import { motion } from "motion/react";

function Container({ children, additionalClassNames = "" }: React.PropsWithChildren<{ additionalClassNames?: string }>) {
  return (
    <div className={`basis-0 grow min-h-px min-w-px relative rounded-[10px] shadow-[0px_10px_15px_-3px_rgba(0,0,0,0.1),0px_4px_6px_-4px_rgba(0,0,0,0.1)] shrink-0 w-[80px] ${additionalClassNames}`}>
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-full items-center justify-center relative w-[80px]">{children}</div>
    </div>
  );
}

export function ToolsList() {
  return (
    <div className="absolute content-stretch flex flex-col gap-[48px] h-[210px] items-start left-[384px] top-[1109px] w-[1161px]" data-name="Section" id="tools">
      <motion.div
        initial={{ y: 30, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="h-[24px] relative shrink-0 w-full"
        data-name="Heading 2"
      >
        <p className="absolute font-['Jost:Regular',sans-serif] font-normal leading-[24px] left-[576.88px] text-[#0f172b] text-[36px] text-center text-nowrap top-[-2px] translate-x-[-50%] whitespace-pre">Nossas Ferramentas</p>
      </motion.div>
      <div className="h-[116px] relative shrink-0 w-full" data-name="Container">
        {/* JavaScript */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="absolute content-stretch flex flex-col gap-[12px] h-[116px] items-center left-[306.8px] top-0 w-[80px]"
          data-name="Container"
        >
          <Container additionalClassNames="bg-[#fdc700]">
            <div className="h-[24px] relative shrink-0 w-[14.219px]" data-name="Text">
              <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[14.219px]">
                <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#0f172b] text-[16px] text-nowrap top-[-2px] whitespace-pre">JS</p>
              </div>
            </div>
          </Container>
          <div className="h-[24px] relative shrink-0 w-[69.813px]" data-name="Text">
            <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[69.813px]">
              <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#45556c] text-[16px] text-nowrap top-[-2px] whitespace-pre">JavaScript</p>
            </div>
          </div>
        </motion.div>

        {/* React */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="absolute content-stretch flex flex-col gap-[12px] h-[116px] items-center left-[418.8px] top-0 w-[80px]"
          data-name="Container"
        >
          <Container additionalClassNames="bg-[#00d3f3]">
            <div className="relative shrink-0 size-[48px]" data-name="Icon">
              <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 48 48">
                <g id="Icon">
                  <path d={svgPaths.p32454c00} fill="#0F172B" id="Vector" />
                </g>
              </svg>
            </div>
          </Container>
          <div className="h-[24px] relative shrink-0 w-[38.422px]" data-name="Text">
            <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[38.422px]">
              <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#45556c] text-[16px] text-nowrap top-[-2px] whitespace-pre">React</p>
            </div>
          </div>
        </motion.div>

        {/* Gemini */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="absolute content-stretch flex flex-col gap-[12px] h-[116px] items-center left-[530.8px] top-0 w-[80px]"
          data-name="Container"
        >
          <Container additionalClassNames="bg-[#1d293d]">
            <div className="h-[24px] relative shrink-0 w-[49.938px]" data-name="Text">
              <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[49.938px]">
                <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[16px] text-nowrap text-white top-[-2px] whitespace-pre">Gemini</p>
              </div>
            </div>
          </Container>
          <div className="h-[24px] relative shrink-0 w-[70.359px]" data-name="Text">
            <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[70.359px]">
              <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#45556c] text-[16px] text-nowrap top-[-2px] whitespace-pre">Google AI</p>
            </div>
          </div>
        </motion.div>

        {/* Calendar API */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="absolute content-stretch flex flex-col gap-[12px] h-[116px] items-center left-[642.8px] top-0 w-[90.391px]"
          data-name="Container"
        >
          <Container additionalClassNames="bg-[#2b7fff]">
            <div className="relative shrink-0 size-[40px]">
              <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 40 40">
                <g id="Icon">
                  <path d="M13.3333 3.33333V10" id="Vector" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3.33333" />
                  <path d="M26.6667 3.33333V10" id="Vector_2" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3.33333" />
                  <path d={svgPaths.p36a93880} id="Vector_3" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3.33333" />
                  <path d="M5 16.6667H35" id="Vector_4" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3.33333" />
                </g>
              </svg>
            </div>
          </Container>
          <div className="h-[24px] relative shrink-0 w-[90.391px]" data-name="Text">
            <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[90.391px]">
              <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#45556c] text-[16px] text-nowrap top-[-2px] whitespace-pre">Calendar API</p>
            </div>
          </div>
        </motion.div>

        {/* Supabase */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="absolute content-stretch flex flex-col gap-[12px] h-[116px] items-center left-[765.19px] top-0 w-[80px]"
          data-name="Container"
        >
          <Container additionalClassNames="bg-[#00bba7]">
            <div className="relative shrink-0 size-[40px]">
              <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 40 40">
                <g id="Icon">
                  <path d={svgPaths.p101dd780} fill="white" id="Vector" />
                </g>
              </svg>
            </div>
          </Container>
          <div className="h-[24px] relative shrink-0 w-[67.813px]" data-name="Text">
            <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[67.813px]">
              <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#45556c] text-[16px] text-nowrap top-[-2px] whitespace-pre">Supabase</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
