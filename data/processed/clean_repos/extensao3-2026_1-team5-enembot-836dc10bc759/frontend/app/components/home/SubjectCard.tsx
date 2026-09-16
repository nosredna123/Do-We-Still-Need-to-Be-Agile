import type { Subject } from '../../lib/types';

type SubjectCardProps = {
  item: Subject;
};

export function SubjectCard({ item }: SubjectCardProps) {
  return (
    <article className="card subject-card" role="button" tabIndex={0}>
      <div className={`subject-icon ${item.gradient}`} aria-hidden>
        {item.icon}
      </div>
      <h3 className="card-title">{item.title}</h3>
      <p className="card-description">{item.description}</p>
    </article>
  );
}
