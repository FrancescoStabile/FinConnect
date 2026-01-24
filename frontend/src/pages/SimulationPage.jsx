import { useState, useEffect } from 'react';
import api from '../services/api';
import SimulationChart from '../components/SimulationChart';

export default function SimulationPage() {
  const [products, setProducts] = useState([]);
  const [formData, setFormData] = useState({
    product_id: '',
    initial_amount: '',
    monthly_contribution: '',
    investment_period_years: '',
  });
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/investments/products');
      setProducts(response.data);
    } catch (err) {
      setError('Errore nel caricamento dei prodotti');
    } finally {
      setIsFetching(false);
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
    setResult(null);
    setIsLoading(true);

    try {
      const response = await api.post('/investments/simulate', {
        product_id: parseInt(formData.product_id),
        initial_amount: parseFloat(formData.initial_amount) || 0,
        monthly_contribution: parseFloat(formData.monthly_contribution) || 0,
        investment_period_years: parseInt(formData.investment_period_years),
      });
      setResult(response.data);
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Errore durante la simulazione. Riprova.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isFetching) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Caricamento...</p>
      </div>
    );
  }

  return (
    <div className="simulation-page">
      <h1>Simulazione Piano di Accumulo (PAC)</h1>
      <p className="page-description">
        Simula l'andamento del tuo investimento nel tempo con diversi scenari.
      </p>

      {error && <div className="error-message">{error}</div>}

      <div className="simulation-content">
        <div className="card simulation-form-card">
          <h2>Configura la Simulazione</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="product_id">Prodotto di Investimento</label>
              <select
                id="product_id"
                name="product_id"
                value={formData.product_id}
                onChange={handleChange}
                required
              >
                <option value="">Seleziona un prodotto</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name} ({product.ticker})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="initial_amount">Investimento Iniziale (€)</label>
              <input
                type="number"
                id="initial_amount"
                name="initial_amount"
                value={formData.initial_amount}
                onChange={handleChange}
                min="0"
                step="100"
                placeholder="es. 1000"
              />
            </div>

            <div className="form-group">
              <label htmlFor="monthly_contribution">Contributo Mensile (€)</label>
              <input
                type="number"
                id="monthly_contribution"
                name="monthly_contribution"
                value={formData.monthly_contribution}
                onChange={handleChange}
                min="0"
                step="50"
                placeholder="es. 200"
              />
            </div>

            <div className="form-group">
              <label htmlFor="investment_period_years">Durata (anni)</label>
              <input
                type="number"
                id="investment_period_years"
                name="investment_period_years"
                value={formData.investment_period_years}
                onChange={handleChange}
                required
                min="1"
                max="50"
                placeholder="es. 10"
              />
            </div>

            <button type="submit" className="btn-primary" disabled={isLoading}>
              {isLoading ? 'Simulazione in corso...' : 'Avvia Simulazione'}
            </button>
          </form>
        </div>

        {result && (
          <div className="card simulation-results">
            <h2>Risultati della Simulazione</h2>
            <p className="product-name">Prodotto: <strong>{result.product_name}</strong></p>

            <div className="results-grid">
              <div className="result-item">
                <span className="label">Capitale Investito</span>
                <span className="value">{formatCurrency(result.total_invested_final)}</span>
              </div>
              <div className="result-item highlight">
                <span className="label">Scenario Medio</span>
                <span className="value">{formatCurrency(result.projected_average_final)}</span>
              </div>
              <div className="result-item positive">
                <span className="label">Scenario Ottimista</span>
                <span className="value">{formatCurrency(result.projected_best_final)}</span>
              </div>
              <div className="result-item negative">
                <span className="label">Scenario Pessimista</span>
                <span className="value">{formatCurrency(result.projected_worst_final)}</span>
              </div>
            </div>

            <SimulationChart data={result.projection_data} />
          </div>
        )}
      </div>
    </div>
  );
}
