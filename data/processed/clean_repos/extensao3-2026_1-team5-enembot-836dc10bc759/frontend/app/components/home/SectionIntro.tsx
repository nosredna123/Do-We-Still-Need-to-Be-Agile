type SectionIntroProps = {
  icon: string;
  title: string;
  subtitle: string;
};

export function SectionIntro({ icon, title, subtitle }: SectionIntroProps) {
  return (
    <div className="section-intro">
      <p className="section-title">
        <span aria-hidden>{icon}</span>
        {title}
      </p>
      <p className="section-subtitle">{subtitle}</p>
    </div>
  );
}
