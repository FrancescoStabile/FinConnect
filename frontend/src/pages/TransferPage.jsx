import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function TransferPage() {
  const [formData, setFormData] = useState({
    receiver_account_number: '',
    receiver_name: '',
    amount: '',
    description: '',
  });
  const [account, setAccount] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAccount();
  }, []);

  const fetchAccount = async () => {
    try {
      const response = await api.get('/accounts/me');
      setAccount(response.data);
    } catch (err) {
      setError('Errore nel caricamento del conto');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
    }).format(amount);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    const amount = parseFloat(formData.amount);
    if (amount <= 0) {
      setError('L\'importo deve essere maggiore di zero');
      setIsLoading(false);
      return;
    }

    if (amount > account.balance) {
      setError('Saldo insufficiente per completare il bonifico');
      setIsLoading(false);
      return;
    }

    try {
      const payload = {
        receiver_account_number: formData.receiver_account_number,
        amount: amount,
        description: formData.description || null,
      };
      console.log('Sending transfer:', payload);
      console.log('Token:', localStorage.getItem('token')?.substring(0, 20) + '...');
      
      const response = await api.post('/transfers', payload);
      console.log('Transfer success:', response.data);

      setSuccess('Bonifico eseguito con successo!');
      setTimeout(() => navigate('/dashboard'), 2000);
    } catch (err) {
      console.error('Transfer error:', err.response?.status, err.response?.data);
      if (err.response?.status === 400) {
        setError(err.response.data.detail || 'Errore nei dati del bonifico');
      } else if (err.response?.status === 404) {
        setError('IBAN destinatario non trovato');
      } else if (err.response?.status === 401) {
        setError('Sessione scaduta. Effettua nuovamente il login.');
      } else {
        setError('Errore durante il bonifico. Riprova.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="transfer-page">
      <h1>Effettua un Bonifico</h1>

      {account && (
        <div className="balance-info">
          <span>Saldo disponibile:</span>
          <strong>{formatCurrency(account.balance)}</strong>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="receiver_account_number">IBAN Destinatario</label>
            <input
              type="text"
              id="receiver_account_number"
              name="receiver_account_number"
              value={formData.receiver_account_number}
              onChange={handleChange}
              required
              placeholder="es. IT60X0542811101000000012346"
            />
          </div>

          <div className="form-group">
            <label htmlFor="receiver_name">Nome Beneficiario</label>
            <input
              type="text"
              id="receiver_name"
              name="receiver_name"
              value={formData.receiver_name}
              onChange={handleChange}
              required
              placeholder="es. Mario Rossi"
            />
          </div>

          <div className="form-group">
            <label htmlFor="amount">Importo (€)</label>
            <input
              type="number"
              id="amount"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              required
              min="0.01"
              step="0.01"
              placeholder="es. 100.00"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Causale (opzionale)</label>
            <input
              type="text"
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="es. Rimborso cena"
            />
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? 'Invio in corso...' : 'Invia Bonifico'}
          </button>
        </form>
      </div>
    </div>
  );
}
