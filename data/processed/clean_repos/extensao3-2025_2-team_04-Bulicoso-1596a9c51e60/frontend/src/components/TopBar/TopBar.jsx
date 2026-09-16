import React from "react";
import "./TopBar.css";

function TopBar() {
  return (
    <div className="topbar">
      <div className="search-container">
        <label className="search-label">Conversas</label>
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input type="text" placeholder="Pesquisar..." />
          <span className="shortcut">⌘ C</span>
        </div>
      </div>

      <button className="new-conversation-btn">
        + Iniciar uma nova conversa
      </button>
    </div>
  );
}

export default TopBar;
