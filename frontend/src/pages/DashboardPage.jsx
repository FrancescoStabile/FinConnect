import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

export default function DashboardPage() {
  const [account, setAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [accountRes, transactionsRes] = await Promise.all([
        api.get('/accounts/me'),
        api.get('/accounts/me/transactions?limit=10'),
      ]);
      setAccount(accountRes.data);
      setTransactions(transactionsRes.data);
    } catch (err) {
      setError('Errore nel caricamento dei dati');
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Caricamento dashboard...</p>
      </div>
    );
  }

  if (error) {
    return <div className="error-container">{error}</div>;
  }

  return (
    <div className="dashboard-page">
      <h1>Dashboard</h1>

      <div className="dashboard-grid">
        <div className="card account-card">
          <h2>Il tuo Conto</h2>
          <div className="account-details">
            <div className="balance">
              <span className="label">Saldo Disponibile</span>
              <span className="amount">{formatCurrency(account?.balance || 0)}</span>
            </div>
            <div className="iban">
              <span className="label">IBAN</span>
              <span className="value">{account?.account_number}</span>
            </div>
          </div>
          <Link to="/transfer" className="btn-secondary">
            Effettua un bonifico →
          </Link>
        </div>

        <div className="card investments-card">
          <h2>Investimenti</h2>
          <p>Esplora i prodotti di investimento e simula il tuo PAC.</p>
          <div className="card-actions">
            <Link to="/investments" className="btn-secondary">
              Vai agli investimenti →
            </Link>
            <Link to="/simulate" className="btn-outline">
              Simula un PAC
            </Link>
          </div>
        </div>
      </div>

      <div className="card transactions-card">
        <h2>Ultime Transazioni</h2>
        {transactions.length === 0 ? (
          <p className="empty-state">Nessun movimento recente</p>
        ) : (
          <table className="transactions-table">
            <thead>
              <tr>
                <th>Data</th>
                <th>Descrizione</th>
                <th>Importo</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => {
                const isOutgoing = tx.sender_account_id === account?.id;
                return (
                  <tr key={tx.id}>
                    <td>{formatDate(tx.timestamp)}</td>
                    <td>{tx.description || 'Bonifico'}</td>
                    <td className={isOutgoing ? 'amount-negative' : 'amount-positive'}>
                      {isOutgoing ? '-' : '+'}{formatCurrency(tx.amount)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
