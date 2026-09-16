import React from "react";
import { useNavigate } from "react-router-dom";
import HomePage from "../ParteParaIntegrar/HomeLoguin/HomeAndPage/src/pages/HomePage";

export default function HomeWrapper() {
  const navigate = useNavigate();

  const handleNavigate = (page: 'home' | 'login') => {
    if (page === 'login') navigate('/login');
    else navigate('/');
  };

  // The exported Figma layout uses many absolute positioned elements and
  // expects a large page height. Render the HomePage inside a full-width
  // container with a large min-height so nothing is clipped.
  return (
    <div style={{ width: '100%', minHeight: '2200px' }}>
      <HomePage onNavigate={handleNavigate} />
    </div>
  );
}
