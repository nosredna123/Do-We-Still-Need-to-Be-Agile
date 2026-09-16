import svgPaths from "./svg-ggi5l4lnb0";
import clsx from "clsx";
import imgLoginRemovebgPreview1 from "figma:asset/5a9ffecd1b54842b99dc6316ab2339e739dbf3ea.png";
import imgRectangle1 from "figma:asset/5506f4864cf674390e58406831bac7f3441235a8.png";
import imgRectangle2 from "figma:asset/9b983a02cf362f48c8e9d70818e094aea561a80a.png";
import imgRectangle3 from "figma:asset/df0370f34b56638efee5b961f27d79c3a59d7aa7.png";
import imgRectangle4 from "figma:asset/c07a09933b113ff1458be6e964b37e0a7a035922.png";
import imgRectangle5 from "figma:asset/f9871a94e7307a04a494b86d5296fe0e1808fa26.png";
import imgGeminiGeneratedImageQyyer0Qyyer0Qyye2 from "figma:asset/0aea4b989c5d8b872f22de685ea0c79912f715e8.png";
import { imgElement } from "./svg-r8ban";

function LandingPage1({ children }: React.PropsWithChildren<{}>) {
  return (
    <div className="basis-0 grow min-h-px min-w-px relative shrink-0 w-[304px]">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-full relative w-[304px]">{children}</div>
    </div>
  );
}

function LandingPage({ children }: React.PropsWithChildren<{}>) {
  return (
    <div className="h-[32px] relative shrink-0 w-[304px]">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex gap-[12px] h-[32px] items-center relative w-[304px]">{children}</div>
    </div>
  );
}
type ContainerProps = {
  additionalClassNames?: string;
};

function Container({ children, additionalClassNames = "" }: React.PropsWithChildren<ContainerProps>) {
  return (
    <div className={clsx("basis-0 grow min-h-px min-w-px relative rounded-[10px] shadow-[0px_10px_15px_-3px_rgba(0,0,0,0.1),0px_4px_6px_-4px_rgba(0,0,0,0.1)] shrink-0 w-[80px]", additionalClassNames)}>
      <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex h-full items-center justify-center relative w-[80px]">{children}</div>
    </div>
  );
}

function Icon1({ children }: React.PropsWithChildren<{}>) {
  return (
    <div className="relative shrink-0 size-[32px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 32 32">
        <g id="Icon">{children}</g>
      </svg>
    </div>
  );
}

function Icon({ children }: React.PropsWithChildren<{}>) {
  return (
    <div className="relative shrink-0 size-[40px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 40 40">
        <g id="Icon">{children}</g>
      </svg>
    </div>
  );
}
type Text1Props = {
  text: string;
  additionalClassNames?: string;
};

function Text1({ text, additionalClassNames = "" }: Text1Props) {
  return (
    <div className={clsx("bg-clip-padding border-0 border-[transparent] border-solid box-border h-[27px] relative", additionalClassNames)}>
      <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[27px] left-0 text-[18px] text-nowrap text-white top-[-2px] whitespace-pre">{text}</p>
    </div>
  );
}
type BackgroundChatElementProps = {
  additionalClassNames?: string;
};

function BackgroundChatElement({ additionalClassNames = "" }: BackgroundChatElementProps) {
  return (
    <div style={{ maskImage: `url('${imgElement}')` }} className={clsx("absolute mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-size-[417.96px_417.96px] mix-blend-overlay", additionalClassNames)}>
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
type TextProps = {
  text: string;
  additionalClassNames?: string;
};

function Text({ text, additionalClassNames = "" }: TextProps) {
  return (
    <div className={clsx("bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative", additionalClassNames)}>
      <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#45556c] text-[16px] text-nowrap top-[-2px] whitespace-pre">{text}</p>
    </div>
  );
}

export default function HomePage() {
  return (
    <div className="bg-white relative size-full" data-name="Home Page">
      <div className="absolute box-border content-stretch flex flex-col h-[97px] items-start left-[196px] pb-px pt-[16px] px-[124px] top-[8px] w-[1528px]" data-name="Header">
        <div aria-hidden="true" className="absolute border-[0px_0px_1px] border-slate-200 border-solid inset-0 pointer-events-none" />
        <div className="content-stretch flex h-[80px] items-center justify-between relative shrink-0 w-full" data-name="Navigation">
          <div className="h-[52px] relative shrink-0 w-[227px]" data-name="login-removebg-preview 1">
            <div className="absolute bg-clip-padding border-0 border-[transparent] border-solid box-border inset-0 overflow-hidden pointer-events-none">
              <img alt="" className="absolute h-[438.6%] left-0 max-w-none top-[-169.3%] w-full" src={imgLoginRemovebgPreview1} />
            </div>
            <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[52px] w-[227px]" />
          </div>
          <div className="h-[24px] relative shrink-0 w-[581px]" data-name="Container">
            <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border content-stretch flex gap-[32px] h-[24px] items-center relative w-[581px]">
              <div className="h-[24px] relative shrink-0 w-[56.734px]" data-name="Link">
                <Text text="Chatbot" additionalClassNames="w-[56.734px]" />
              </div>
              <div className="basis-0 grow h-[24px] min-h-px min-w-px relative shrink-0" data-name="Link">
                <Text text="Como funciona?" additionalClassNames="w-full" />
              </div>
              <div className="h-[24px] relative shrink-0 w-[87px]" data-name="Link">
                <Text text="Ferramentas" additionalClassNames="w-[87px]" />
              </div>
              <div className="h-[24px] relative shrink-0 w-[93.766px]" data-name="Link">
                <Text text="Quem somos" additionalClassNames="w-[93.766px]" />
              </div>
              <div className="h-[24px] relative shrink-0 w-[93.766px]" data-name="Link">
                <Text text="Login" additionalClassNames="w-[93.766px]" />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="absolute content-stretch flex flex-col gap-[48px] h-[210px] items-start left-[384px] top-[1109px] w-[1161px]" data-name="Section">
        <div className="h-[24px] relative shrink-0 w-full" data-name="Heading 2">
          <p className="absolute font-['Jost:Regular',sans-serif] font-normal leading-[24px] left-[576.88px] text-[#0f172b] text-[36px] text-center text-nowrap top-[-2px] translate-x-[-50%] whitespace-pre">Nossas Ferramentas</p>
        </div>
        <div className="h-[116px] relative shrink-0 w-full" data-name="Container">
          <div className="absolute content-stretch flex flex-col gap-[12px] h-[116px] items-center left-[306.8px] top-0 w-[80px]" data-name="Container">
            <Container additionalClassNames="bg-[#fdc700]">
              <div className="h-[24px] relative shrink-0 w-[14.219px]" data-name="Text">
                <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[14.219px]">
                  <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[#0f172b] text-[16px] text-nowrap top-[-2px] whitespace-pre">JS</p>
                </div>
              </div>
            </Container>
            <div className="h-[24px] relative shrink-0 w-[69.813px]" data-name="Text">
              <Text text="JavaScript" additionalClassNames="w-[69.813px]" />
            </div>
          </div>
          <div className="absolute content-stretch flex flex-col gap-[12px] h-[116px] items-center left-[418.8px] top-0 w-[80px]" data-name="Container">
            <Container additionalClassNames="bg-[#00d3f3]">
              <div className="relative shrink-0 size-[48px]" data-name="Icon">
                <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 48 48">
                  <g id="Icon">
                    <path d={svgPaths.p32454c00} fill="var(--fill-0, #0F172B)" id="Vector" />
                  </g>
                </svg>
              </div>
            </Container>
            <div className="h-[24px] relative shrink-0 w-[38.422px]" data-name="Text">
              <Text text="React" additionalClassNames="w-[38.422px]" />
            </div>
          </div>
          <div className="absolute content-stretch flex flex-col gap-[12px] h-[116px] items-center left-[530.8px] top-0 w-[80px]" data-name="Container">
            <Container additionalClassNames="bg-[#1d293d]">
              <div className="h-[24px] relative shrink-0 w-[49.938px]" data-name="Text">
                <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[24px] relative w-[49.938px]">
                  <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-0 text-[16px] text-nowrap text-white top-[-2px] whitespace-pre">Gemini</p>
                </div>
              </div>
            </Container>
            <div className="h-[24px] relative shrink-0 w-[70.359px]" data-name="Text">
              <Text text="Google AI" additionalClassNames="w-[70.359px]" />
            </div>
          </div>
          <div className="absolute content-stretch flex flex-col gap-[12px] h-[116px] items-center left-[642.8px] top-0 w-[90.391px]" data-name="Container">
            <Container additionalClassNames="bg-[#2b7fff]">
              <Icon>
                <path d="M13.3333 3.33333V10" id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3.33333" />
                <path d="M26.6667 3.33333V10" id="Vector_2" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3.33333" />
                <path d={svgPaths.p36a93880} id="Vector_3" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3.33333" />
                <path d="M5 16.6667H35" id="Vector_4" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3.33333" />
              </Icon>
            </Container>
            <div className="h-[24px] relative shrink-0 w-[90.391px]" data-name="Text">
              <Text text="Calendar API" additionalClassNames="w-[90.391px]" />
            </div>
          </div>
          <div className="absolute content-stretch flex flex-col gap-[12px] h-[116px] items-center left-[765.19px] top-0 w-[80px]" data-name="Container">
            <Container additionalClassNames="bg-[#00bba7]">
              <Icon>
                <path d={svgPaths.p101dd780} fill="var(--fill-0, white)" id="Vector" />
              </Icon>
            </Container>
            <div className="h-[24px] relative shrink-0 w-[67.813px]" data-name="Text">
              <Text text="Supabase" additionalClassNames="w-[67.813px]" />
            </div>
          </div>
        </div>
      </div>
      <div className="absolute bg-[#0f172b] h-[540px] left-0 top-[1401px] w-[1920px]" data-name="Section">
        <div className="absolute h-[24px] left-[384.44px] top-[60px] w-[1152px]" data-name="Heading 2">
          <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-[575.94px] text-[48px] text-center text-nowrap text-white top-[-2px] translate-x-[-50%] whitespace-pre">Mentes Criativas</p>
        </div>
        <div className="absolute h-[104px] left-[380px] top-[81px] w-[768px]" data-name="Paragraph">
          <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[26px] left-[580.5px] text-[16px] text-[rgba(255,255,255,0.8)] text-center top-[33px] translate-x-[-50%] w-[763px]">Nossa equipe une inovação e empatia para criar Bullçoso, a IA da classe. O projeto Bullçoso foi arquitetado para aprimorar e facilitar a interação digital através de IA, promovendo melhor atendimento e acessibilidade à informação de qualidade na área da saúde. Somos desenvolvedores e criativos que acreditam que tecnologia deve ser acessível a todos, especialmente à terceira idade.</p>
        </div>
        <div className="absolute h-[193px] left-[467.44px] rounded-[30px] top-[252px] w-[173px]">
          <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none rounded-[30px] size-full" src={imgRectangle1} />
        </div>
        <div className="absolute h-[193px] left-[670.44px] rounded-[30px] top-[252px] w-[173px]">
          <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none rounded-[30px] size-full" src={imgRectangle2} />
        </div>
        <div className="absolute h-[193px] left-[873.44px] rounded-[30px] top-[252px] w-[173px]">
          <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none rounded-[30px] size-full" src={imgRectangle3} />
        </div>
        <div className="absolute h-[193px] left-[1076.44px] rounded-[30px] top-[252px] w-[173px]">
          <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none rounded-[30px] size-full" src={imgRectangle4} />
        </div>
        <div className="absolute h-[193px] left-[1279.44px] rounded-[30px] top-[252px] w-[173px]">
          <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none rounded-[30px] size-full" src={imgRectangle5} />
        </div>
        <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-[554.94px] text-[16px] text-center text-nowrap text-white top-[460px] translate-x-[-50%] whitespace-pre">{`Italo  Vicente`}</p>
        <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-[757.44px] text-[16px] text-center text-nowrap text-white top-[460px] translate-x-[-50%] whitespace-pre">{`Sílvio Gonçalves `}</p>
        <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-[960.94px] text-[16px] text-center text-nowrap text-white top-[460px] translate-x-[-50%] whitespace-pre">Esterfane Camelo</p>
        <p className="absolute font-['Arimo:Regular',sans-serif] font-normal h-[24px] leading-[24px] left-[1162.94px] text-[16px] text-center text-white top-[460px] translate-x-[-50%] w-[129px]">Samuel Valente</p>
        <p className="absolute font-['Arimo:Regular',sans-serif] font-normal h-[24px] leading-[24px] left-[1365.94px] text-[16px] text-center text-white top-[460px] translate-x-[-50%] w-[129px]">Pedro Henrique</p>
        <div className="absolute blur-[2px] border-2 border-[rgba(255,255,255,0.2)] border-solid filter left-[230px] size-[189.77px] top-[64px]" data-name="Container" />
        <div className="absolute blur-[2px] border-2 border-[rgba(255,255,255,0.2)] border-solid filter left-[1536px] size-[189.77px] top-[123px]" data-name="Container" />
        <div className="absolute blur-[2px] border-2 border-[rgba(255,255,255,0.2)] border-solid filter left-[1660px] size-[189.77px] top-[235px]" data-name="Container" />
        <div className="absolute blur-[2px] border-2 border-[rgba(255,255,255,0.2)] border-solid filter left-[1668px] size-[189.77px] top-[71px]" data-name="Container" />
      </div>
      <div className="absolute bg-white box-border content-stretch flex flex-col h-[121px] items-start left-[241px] pb-0 pt-[33px] px-[188px] top-[1941px] w-[1528px]" data-name="Footer">
        <div aria-hidden="true" className="absolute border-[1px_0px_0px] border-slate-200 border-solid inset-0 pointer-events-none" />
        <div className="content-stretch flex flex-col gap-[8px] h-[56px] items-start relative shrink-0 w-full" data-name="Container">
          <div className="h-[24px] relative shrink-0 w-full" data-name="Paragraph">
            <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-[575.58px] text-[#62748e] text-[16px] text-center text-nowrap top-[-2px] translate-x-[-50%] whitespace-pre">© 2025 Bullçoso - Assistente de Saúde para Idosos</p>
          </div>
          <div className="h-[24px] relative shrink-0 w-full" data-name="Paragraph">
            <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-[576.14px] text-[#62748e] text-[16px] text-center text-nowrap top-[-2px] translate-x-[-50%] whitespace-pre">Desenvolvido com 💚 para melhorar a vida da terceira idade</p>
          </div>
        </div>
      </div>
      <div className="absolute h-[504px] left-[196px] overflow-clip top-[96px] w-[1528px]" data-name="Section">
        <div className="absolute left-[531px] size-[465px] top-[-71px]" data-name="Gemini_Generated_Image_qyyer0qyyer0qyye 2">
          <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full" src={imgGeminiGeneratedImageQyyer0Qyyer0Qyye2} />
        </div>
        <div className="absolute h-[504px] left-0 top-0 w-[1528px]" data-name="Container">
          <div className="absolute border-2 border-slate-200 border-solid left-[28.09px] size-[151.816px] top-[28.09px]" data-name="Container" />
          <div className="absolute border-2 border-slate-200 border-solid left-[1343.07px] size-[113.862px] top-[151.07px]" data-name="Container" />
          <div className="absolute border-2 border-slate-200 border-solid left-[365.43px] size-[113.137px] top-[327.43px]" data-name="Container" />
          <div className="absolute border-2 border-slate-200 border-solid left-[941.42px] size-[90.51px] top-[154.73px]" data-name="Container" />
        </div>
        <div className="absolute bg-white h-[241px] left-[267px] rounded-[16px] top-[263px] w-[993px]" data-name="Prompt Box">
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
            <div className="content-stretch flex flex-col gap-[24px] items-center max-w-[400px] relative shrink-0 w-[400px]" data-name="Top Part">
              <div className="content-stretch flex flex-col gap-[6px] items-center not-italic relative shrink-0 text-center w-full" data-name="Page Title Wrapper">
                <p className="font-['Inter:Medium',sans-serif] font-medium leading-[1.3] relative shrink-0 text-[#19213d] text-[22px] text-nowrap whitespace-pre">Bem vindo, Paulo</p>
                <p className="font-['Inter:Regular',sans-serif] font-normal leading-[1.5] min-w-full relative shrink-0 text-[#666f8d] text-[14px] w-[min-content]">Exemplo xxx - xxx - xxx</p>
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
                        <div className="bg-[#69b8ce] relative rounded-[8px] shrink-0 size-[42px]" data-name="Primary Button">
                          <div className="content-stretch flex items-center justify-center overflow-clip relative rounded-[inherit] size-[42px]">
                            <div className="relative shrink-0 size-[20px]" data-name="Filled/Send">
                              <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
                                <g id="Filled/Send">
                                  <path d={svgPaths.p1850be00} fill="var(--fill-0, white)" id="Element" />
                                </g>
                              </svg>
                            </div>
                          </div>
                          <div className="absolute inset-0 pointer-events-none shadow-[0px_-2px_0.3px_0px_inset_rgba(14,56,125,0.18),0px_2px_1px_0px_inset_rgba(255,255,255,0.22)]" />
                          <div aria-hidden="true" className="absolute border border-[#69b8ce] border-solid inset-0 pointer-events-none rounded-[8px] shadow-[0px_2px_5px_0px_rgba(20,88,201,0.17)]" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div aria-hidden="true" className="absolute border border-[#e3e6ea] border-solid inset-0 pointer-events-none rounded-[16px] shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]" />
        </div>
        <div className="absolute h-[344px] left-[428px] top-[80px] w-[672px]" data-name="Container" />
      </div>
      <div className="absolute border-2 border-slate-200 border-solid left-[1553px] size-[113.862px] top-[1127px]" data-name="Container" />
      <div className="absolute border-2 border-slate-200 border-solid left-[1639px] size-[113.862px] top-[1207px]" data-name="Container" />
      <div className="absolute border-2 border-slate-200 border-solid left-[1753px] size-[113.862px] top-[1013px]" data-name="Container" />
      <div className="absolute border-2 border-slate-200 border-solid left-[120px] size-[151.816px] top-[1105px]" data-name="Container" />
      <div className="absolute bg-[#0f172b] h-[400px] left-0 overflow-clip top-[627px] w-[1920px]" data-name="Section">
        <div className="absolute h-[400px] left-0 opacity-10 top-0 w-[1528px]" data-name="Container">
          {[...Array(2).keys()].map((_, i) => (
            <div className="absolute border-2 border-solid border-white left-[25.12px] size-[189.77px] top-[25.12px]" data-name="Container" />
          ))}
          <div className="absolute border-2 border-solid border-white left-[1348.09px] size-[151.816px] top-[220.09px]" data-name="Container" />
          <div className="absolute border-2 border-solid border-white left-[362.12px] size-[135.765px] top-[180.12px]" data-name="Container" />
        </div>
        <div className="absolute gap-[24px] grid grid-cols-[repeat(3,_minmax(0px,_1fr))] grid-rows-[repeat(1,_minmax(0px,_1fr))] h-[240px] left-[384px] top-[76px] w-[1152px]" data-name="Container">
          <div className="[grid-area:1_/_1] place-self-stretch relative rounded-[14px] shrink-0" data-name="Card">
            <div className="size-full">
              <div className="box-border content-stretch flex flex-col gap-[17px] items-start pl-[32px] pr-0 py-[32px] relative size-full">
                <LandingPage>
                  <Icon1>
                    <path d={svgPaths.p1dee4500} id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                    <path d={svgPaths.p1fa92f00} id="Vector_2" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                    <path d={svgPaths.p230c5e00} id="Vector_3" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                  </Icon1>
                  <div className="h-[27px] relative shrink-0 w-[78.984px]" data-name="Heading 3">
                    <Text1 text="Propósito" additionalClassNames="w-[78.984px]" />
                  </div>
                </LandingPage>
                <LandingPage1>
                  <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[26px] left-0 text-[16px] text-[rgba(255,255,255,0.9)] top-[-2px] w-[294px]">Facilitar o acesso à informação de saúde para idosos, oferecendo suporte personalizado e orientações confiáveis de forma simples e acessível.</p>
                </LandingPage1>
              </div>
            </div>
          </div>
          <div className="[grid-area:1_/_2] place-self-stretch relative rounded-[14px] shrink-0" data-name="Card">
            <div className="size-full">
              <div className="box-border content-stretch flex flex-col gap-[19px] items-start pl-[32px] pr-0 py-[32px] relative size-full">
                <LandingPage>
                  <Icon1>
                    <path d={svgPaths.p34392700} id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                    <path d={svgPaths.p1a533880} id="Vector_2" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                    <path d={svgPaths.p2a0ba600} id="Vector_3" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                    <path d={svgPaths.p2d878d00} id="Vector_4" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                    <path d={svgPaths.p1ad85e80} id="Vector_5" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                  </Icon1>
                  <div className="h-[27px] relative shrink-0 w-[39.016px]" data-name="Heading 3">
                    <Text1 text="Foco" additionalClassNames="w-[39.016px]" />
                  </div>
                </LandingPage>
                <LandingPage1>
                  <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[26px] left-0 text-[16px] text-[rgba(255,255,255,0.9)] top-[-2px] w-[282px]">Saúde preventiva, lembretes de medicamentos, consultas médicas e orientações sobre bem-estar específicas para a terceira idade.</p>
                </LandingPage1>
              </div>
            </div>
          </div>
          <div className="[grid-area:1_/_3] place-self-stretch relative rounded-[14px] shrink-0" data-name="Card">
            <div className="size-full">
              <div className="box-border content-stretch flex flex-col gap-[14px] items-start pl-[32px] pr-0 py-[32px] relative size-full">
                <LandingPage>
                  <Icon1>
                    <path d="M16 9.33333V28" id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                    <path d={svgPaths.p308d0700} id="Vector_2" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.66667" />
                  </Icon1>
                  <div className="h-[27px] relative shrink-0 w-[113.609px]" data-name="Heading 3">
                    <Text1 text="Modo de usar" additionalClassNames="w-[113.609px]" />
                  </div>
                </LandingPage>
                <div className="h-[118px] relative shrink-0 w-[304px]" data-name="LandingPage">
                  <div className="bg-clip-padding border-0 border-[transparent] border-solid box-border h-[118px] relative w-[304px]">
                    <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[26px] left-0 text-[16px] text-[rgba(255,255,255,0.9)] top-[-2px] w-[280px]">Faça perguntas naturalmente, como em uma conversa. O chatbot entende e responde de forma clara, com letras grandes e interface amigável.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}