import React from 'react';
import './Card.css';

function Card({ text, onClick }) {
  return (
    <div className="card" onClick={onClick}>
      <p className="card-text">{text}</p>
    </div>
  );
}

export default Card;
