import Header from './Header';

export default function Layout({ children }) {
  return (
    <div className="layout">
      <Header />
      <main className="main-content">
        {children}
      </main>
      <footer className="footer">
        <p>© 2026 FinConnect - Project Work Tesi Triennale</p>
      </footer>
    </div>
  );
}
