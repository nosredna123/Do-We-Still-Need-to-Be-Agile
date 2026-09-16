import React from "react";
import "./Sidebar.css";

export default function Sidebar() {

  const handleNewChat = () => {
    window.location.reload();
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <h2 className="user-name">Ítalo Vicente</h2>
      </div>
   
      <nav className="nav-section">      
        <input className="nav-search" type="text" placeholder="Pesquisar por conversas..." ></input>  
        <button className="nav-btn active">
          
          <span className="label">Conversas</span>
        </button>

        <button className="nav-btn">
          
          <span className="label">Modo de usar</span>
        </button>

        <button className="nav-btn">
          
          <span className="label">Preferência</span>
        </button>
      </nav>

      <div className="section">
        <h3 className="section-title">EXEMPLOS DE USO</h3>
        <ul className="list">
          <li>Consultar Bula</li>
          <li>Agendar Medicamento</li>
          <li>Editar Medicamento</li>
          <li>Deletar Medicamento</li>
        </ul>
      </div>

      <div className="section">
        <h3 className="section-title">HISTÓRICO DE CONVERSA</h3>
        <ul className="list">
          <li>Quero agendar dipirona</li>
          <li>Edite a medicação de dipirona</li>
          <li>Quero saber as contraindicações desse remédio</li>
          <li>Edite o horário da dipirona</li>
        </ul>
      </div>

      <button className="new-chat" onClick={handleNewChat}>
        ＋ Iniciar uma nova conversa
      </button>
    </aside>
  );
}
