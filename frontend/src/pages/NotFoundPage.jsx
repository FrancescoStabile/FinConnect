import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="not-found-page">
      <div className="not-found-content">
        <h1>404</h1>
        <h2>Pagina non trovata</h2>
        <p>La pagina che stai cercando non esiste o è stata spostata.</p>
        <Link to="/dashboard" className="btn-primary">
          Torna alla Dashboard
        </Link>
      </div>
    </div>
  );
}
