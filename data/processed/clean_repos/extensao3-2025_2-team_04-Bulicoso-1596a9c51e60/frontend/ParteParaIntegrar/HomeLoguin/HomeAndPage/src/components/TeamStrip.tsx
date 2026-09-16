import imgRectangle1 from "figma:asset/5506f4864cf674390e58406831bac7f3441235a8.png";
import imgRectangle2 from "figma:asset/9b983a02cf362f48c8e9d70818e094aea561a80a.png";
import imgRectangle3 from "figma:asset/df0370f34b56638efee5b961f27d79c3a59d7aa7.png";
import imgRectangle4 from "figma:asset/c07a09933b113ff1458be6e964b37e0a7a035922.png";
import imgRectangle5 from "figma:asset/f9871a94e7307a04a494b86d5296fe0e1808fa26.png";
import { motion } from "motion/react";

export function TeamStrip() {
  const teamMembers = [
    { img: imgRectangle1, name: "Italo  Vicente", left: "467.44px" },
    { img: imgRectangle2, name: "Sílvio Gonçalves ", left: "670.44px" },
    { img: imgRectangle3, name: "Esterfane Camelo", left: "873.44px" },
    { img: imgRectangle4, name: "Samuel Valente", left: "1076.44px" },
    { img: imgRectangle5, name: "Pedro Henrique", left: "1279.44px" },
  ];

  return (
    <div className="absolute bg-[#0f172b] h-[540px] left-0 top-[1401px] w-[1920px]" data-name="Section" id="team">
      <motion.div
        initial={{ y: 30, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="absolute h-[24px] left-[384.44px] top-[60px] w-[1152px]"
        data-name="Heading 2"
      >
        <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-[575.94px] text-[48px] text-center text-nowrap text-white top-[-2px] translate-x-[-50%] whitespace-pre">Mentes Criativas</p>
      </motion.div>
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="absolute h-[104px] left-[380px] top-[81px] w-[768px]"
        data-name="Paragraph"
      >
        <p className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[26px] left-[580.5px] text-[16px] text-[rgba(255,255,255,0.8)] text-center top-[33px] translate-x-[-50%] w-[763px]">Nossa equipe une inovação e empatia para criar Bullçoso, a IA da classe. O projeto Bullçoso foi arquitetado para aprimorar e facilitar a interação digital através de IA, promovendo melhor atendimento e acessibilidade à informação de qualidade na área da saúde. Somos desenvolvedores e criativos que acreditam que tecnologia deve ser acessível a todos, especialmente à terceira idade.</p>
      </motion.div>

      {teamMembers.map((member, index) => (
        <motion.div
          key={index}
          initial={{ y: 100, opacity: 0 }}
          whileInView={{ y: 0, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 * index }}
          whileHover={{
            y: -10,
            scale: 1.05,
            transition: { duration: 0.3 }
          }}
          className="absolute h-[193px] rounded-[30px] top-[252px] w-[173px]"
          style={{ left: member.left }}
        >
          <img
            alt={member.name}
            className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none rounded-[30px] size-full"
            src={member.img}
          />
        </motion.div>
      ))}

      <motion.p
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-[554.94px] text-[16px] text-center text-nowrap text-white top-[460px] translate-x-[-50%] whitespace-pre"
      >{`Italo  Vicente`}</motion.p>
      <motion.p
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.7 }}
        className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-[757.44px] text-[16px] text-center text-nowrap text-white top-[460px] translate-x-[-50%] whitespace-pre"
      >{`Sílvio Gonçalves `}</motion.p>
      <motion.p
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.8 }}
        className="absolute font-['Arimo:Regular',sans-serif] font-normal leading-[24px] left-[960.94px] text-[16px] text-center text-nowrap text-white top-[460px] translate-x-[-50%] whitespace-pre"
      >Esterfane Camelo</motion.p>
      <motion.p
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.9 }}
        className="absolute font-['Arimo:Regular',sans-serif] font-normal h-[24px] leading-[24px] left-[1162.94px] text-[16px] text-center text-white top-[460px] translate-x-[-50%] w-[129px]"
      >Samuel Valente</motion.p>
      <motion.p
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 1 }}
        className="absolute font-['Arimo:Regular',sans-serif] font-normal h-[24px] leading-[24px] left-[1365.94px] text-[16px] text-center text-white top-[460px] translate-x-[-50%] w-[129px]"
      >Pedro Henrique</motion.p>

      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
        className="absolute blur-[2px] border-2 border-[rgba(255,255,255,0.2)] border-solid filter left-[230px] size-[189.77px] top-[64px]"
        data-name="Container"
      />
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
        className="absolute blur-[2px] border-2 border-[rgba(255,255,255,0.2)] border-solid filter left-[1536px] size-[189.77px] top-[123px]"
        data-name="Container"
      />
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 35, repeat: Infinity, ease: "linear" }}
        className="absolute blur-[2px] border-2 border-[rgba(255,255,255,0.2)] border-solid filter left-[1660px] size-[189.77px] top-[235px]"
        data-name="Container"
      />
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        className="absolute blur-[2px] border-2 border-[rgba(255,255,255,0.2)] border-solid filter left-[1668px] size-[189.77px] top-[71px]"
        data-name="Container"
      />
    </div>
  );
}
