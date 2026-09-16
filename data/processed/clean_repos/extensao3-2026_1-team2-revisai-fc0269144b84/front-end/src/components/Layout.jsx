import Sidebar from "./Sidebar";

export default function Layout({ children }) {
  return (
    <div
      className="bg-background"
      style={{ display: "flex", flexDirection: "row", height: "100vh", overflow: "hidden", position: "relative" }}
    >
      <Sidebar />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <header className="h-14 flex items-center border-b px-4 bg-card" style={{ height: 56, flexShrink: 0 }}>
          <h1 className="text-lg font-bold text-foreground">RevisAI</h1>
        </header>
        <main
          className="bg-background"
          style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column", padding: "1.5rem" }}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
