import svgPaths from "../imports/svg-ggi5l4lnb0";
import { motion } from "motion/react";

interface FeatureCardProps {
  icon: 'purpose' | 'focus' | 'usage';
  title: string;
  description: string;
  index: number;
}

export function FeatureCard({ icon, title, description, index }: FeatureCardProps) {
  return (
    <motion.div
      initial={{ y: 50, opacity: 0 }}
      whileInView={{ y: 0, opacity: 1 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.6, delay: index * 0.2 }}
      whileHover={{
        y: -10,
        transition: { duration: 0.3 }
      }}
      className="place-self-stretch relative rounded-[14px] shrink-0"
      data-name="Card"
    >
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[17px] items-start pl-[32px] pr-0 py-[32px] relative size-full">
          <div className="basis-0 grow min-h-px min-w-px relative shrink-0 w-[304px]">
            <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex gap-[12px] h-[32px] items-center relative w-[304px]">
              <motion.div
                initial={{ rotate: 0 }}
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
                className="relative shrink-0 size-[32px]"
              >
                <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 32 32">
                  <g id="Icon">
                    {icon === 'purpose' && (
                      <>
                        <path d={svgPaths.p1dee4500} id="Vector" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                        <path d={svgPaths.p1fa92f00} id="Vector_2" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                        <path d={svgPaths.p230c5e00} id="Vector_3" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                      </>
                    )}
                    {icon === 'focus' && (
                      <>
                        <path d={svgPaths.p34392700} id="Vector" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                        <path d={svgPaths.p1a533880} id="Vector_2" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                        <path d={svgPaths.p2a0ba600} id="Vector_3" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                        <path d={svgPaths.p2d878d00} id="Vector_4" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                        <path d={svgPaths.p1ad85e80} id="Vector_5" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                      </>
                    )}
                    {icon === 'usage' && (
                      <>
                        <path d="M16 9.33333V28" id="Vector" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                        <path d={svgPaths.p308d0700} id="Vector_2" stroke="white" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                      </>
                    )}
                  </g>
                </svg>
              </motion.div>
              <div className="h-[27px] relative shrink-0" data-name="Heading 3">
                <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[27px] relative">
                  <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[27px] left-0 text-[18px] text-nowrap text-white top-[-2px] whitespace-pre">{title}</p>
                </div>
              </div>
            </div>
          </div>
          <div className="basis-0 grow min-h-px min-w-px relative shrink-0 w-[304px]">
            <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[26px] left-0 text-[16px] text-[rgba(255,255,255,0.9)] top-[-2px] w-[294px]">{description}</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
