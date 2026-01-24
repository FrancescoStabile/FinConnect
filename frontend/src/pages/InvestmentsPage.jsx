import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

export default function InvestmentsPage() {
  const [products, setProducts] = useState([]);
  const [portfolio, setPortfolio] = useState(null);
  const [account, setAccount] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Stati per modal acquisto
  const [showBuyModal, setShowBuyModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [buyAmount, setBuyAmount] = useState('');
  const [isBuying, setIsBuying] = useState(false);
  
  // Stati per modal vendita
  const [showSellModal, setShowSellModal] = useState(false);
  const [selectedHolding, setSelectedHolding] = useState(null);
  const [sellQuantity, setSellQuantity] = useState('');
  const [isSelling, setIsSelling] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [productsRes, portfolioRes, accountRes] = await Promise.all([
        api.get('/investments/products'),
        api.get('/investments/portfolio'),
        api.get('/accounts/me'),
      ]);
      setProducts(productsRes.data);
      setPortfolio(portfolioRes.data);
      setAccount(accountRes.data);
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

  const formatPercent = (value) => {
    return `${(parseFloat(value) * 100).toFixed(1)}%`;
  };

  const getRiskColor = (risk) => {
    const colors = {
      'Conservativo': 'risk-low',
      'Moderato': 'risk-medium',
      'Aggressivo': 'risk-high',
    };
    return colors[risk] || '';
  };

  const openBuyModal = (product) => {
    setSelectedProduct(product);
    setBuyAmount('');
    setShowBuyModal(true);
    setError('');
    setSuccess('');
  };

  const closeBuyModal = () => {
    setShowBuyModal(false);
    setSelectedProduct(null);
    setBuyAmount('');
  };

  const handleBuy = async (e) => {
    e.preventDefault();
    if (!selectedProduct || !buyAmount) return;

    setIsBuying(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/investments/buy', {
        product_id: selectedProduct.id,
        amount: parseFloat(buyAmount),
      });
      
      setSuccess(`Acquistate ${parseFloat(response.data.quantity_purchased).toFixed(4)} quote di ${response.data.product_name} per ${formatCurrency(response.data.amount_spent)}`);
      closeBuyModal();
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Errore durante l\'acquisto');
    } finally {
      setIsBuying(false);
    }
  };

  const openSellModal = (holding) => {
    setSelectedHolding(holding);
    setSellQuantity('');
    setShowSellModal(true);
    setError('');
    setSuccess('');
  };

  const closeSellModal = () => {
    setShowSellModal(false);
    setSelectedHolding(null);
    setSellQuantity('');
  };

  const handleSell = async (e) => {
    e.preventDefault();
    if (!selectedHolding || !sellQuantity) return;

    setIsSelling(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/investments/sell', {
        product_id: selectedHolding.product.id,
        quantity: parseFloat(sellQuantity),
      });
      
      setSuccess(`Vendute ${parseFloat(response.data.quantity_sold).toFixed(4)} quote di ${response.data.product_name} per ${formatCurrency(response.data.amount_received)}`);
      closeSellModal();
      fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Errore durante la vendita');
    } finally {
      setIsSelling(false);
    }
  };

  const sellAll = () => {
    if (selectedHolding) {
      setSellQuantity(parseFloat(selectedHolding.quantity).toString());
    }
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Caricamento investimenti...</p>
      </div>
    );
  }

  return (
    <div className="investments-page">
      <h1>Investimenti</h1>

      {/* Saldo disponibile */}
      {account && (
        <div className="balance-info">
          <span>Saldo Disponibile</span>
          <strong>{formatCurrency(account.balance)}</strong>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {/* Portafoglio */}
      {portfolio && portfolio.holdings && portfolio.holdings.length > 0 && (
        <div className="card portfolio-section">
          <h2>Il tuo Portafoglio</h2>
          <div className="portfolio-total">
            <span>Valore Totale:</span>
            <strong>{formatCurrency(portfolio.total_value)}</strong>
          </div>
          <table className="holdings-table">
            <thead>
              <tr>
                <th>Prodotto</th>
                <th>Quantità</th>
                <th>Valore Attuale</th>
                <th>P/L</th>
                <th>Azioni</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.holdings.map((holding) => (
                <tr key={holding.id}>
                  <td>{holding.product.name}</td>
                  <td>{parseFloat(holding.quantity).toFixed(4)}</td>
                  <td>{formatCurrency(holding.current_value)}</td>
                  <td className={parseFloat(holding.profit_loss) >= 0 ? 'amount-positive' : 'amount-negative'}>
                    {formatCurrency(holding.profit_loss)}
                  </td>
                  <td>
                    <button 
                      className="btn-sell"
                      onClick={() => openSellModal(holding)}
                    >
                      Vendi
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Prodotti disponibili */}
      <div className="products-section">
        <div className="section-header">
          <h2>Prodotti Disponibili</h2>
          <Link to="/simulate" className="btn-primary">
            Simula un PAC →
          </Link>
        </div>

        <div className="products-grid">
          {products.map((product) => (
            <div key={product.id} className="product-card">
              <div className="product-header">
                <h3>{product.name}</h3>
                <span className={`risk-badge ${getRiskColor(product.risk_profile)}`}>
                  {product.risk_profile}
                </span>
              </div>
              <p className="ticker">{product.ticker}</p>
              <p className="description">{product.description}</p>
              <div className="product-stats">
                <div className="stat">
                  <span className="label">Prezzo Quota</span>
                  <span className="value">{formatCurrency(product.current_price)}</span>
                </div>
                <div className="stat">
                  <span className="label">Rendimento Atteso</span>
                  <span className="value">{formatPercent(product.sim_annual_return_rate)}</span>
                </div>
                <div className="stat">
                  <span className="label">Volatilità</span>
                  <span className="value">{formatPercent(product.sim_volatility)}</span>
                </div>
              </div>
              <button 
                className="btn-buy"
                onClick={() => openBuyModal(product)}
              >
                Acquista
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Modal Acquisto */}
      {showBuyModal && selectedProduct && (
        <div className="modal-overlay" onClick={closeBuyModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Acquista {selectedProduct.name}</h2>
            <p className="modal-info">
              Prezzo quota: <strong>{formatCurrency(selectedProduct.current_price)}</strong>
            </p>
            <p className="modal-info">
              Saldo disponibile: <strong>{formatCurrency(account?.balance || 0)}</strong>
            </p>
            
            <form onSubmit={handleBuy}>
              <div className="form-group">
                <label htmlFor="buyAmount">Importo da investire (€)</label>
                <input
                  type="number"
                  id="buyAmount"
                  value={buyAmount}
                  onChange={(e) => setBuyAmount(e.target.value)}
                  min="1"
                  max={account?.balance || 0}
                  step="0.01"
                  required
                  placeholder="es. 500"
                />
              </div>
              
              {buyAmount && parseFloat(buyAmount) > 0 && (
                <p className="quote-preview">
                  Riceverai circa <strong>{(parseFloat(buyAmount) / parseFloat(selectedProduct.current_price)).toFixed(4)}</strong> quote
                </p>
              )}
              
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={closeBuyModal}>
                  Annulla
                </button>
                <button type="submit" className="btn-primary" disabled={isBuying}>
                  {isBuying ? 'Acquisto...' : 'Conferma Acquisto'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Vendita */}
      {showSellModal && selectedHolding && (
        <div className="modal-overlay" onClick={closeSellModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Vendi {selectedHolding.product.name}</h2>
            <p className="modal-info">
              Quote possedute: <strong>{parseFloat(selectedHolding.quantity).toFixed(4)}</strong>
            </p>
            <p className="modal-info">
              Prezzo attuale: <strong>{formatCurrency(selectedHolding.product.current_price)}</strong>
            </p>
            <p className="modal-info">
              Valore totale: <strong>{formatCurrency(selectedHolding.current_value)}</strong>
            </p>
            
            <form onSubmit={handleSell}>
              <div className="form-group">
                <label htmlFor="sellQuantity">Quantità da vendere</label>
                <input
                  type="number"
                  id="sellQuantity"
                  value={sellQuantity}
                  onChange={(e) => setSellQuantity(e.target.value)}
                  min="0.0001"
                  max={parseFloat(selectedHolding.quantity)}
                  step="0.0001"
                  required
                  placeholder="es. 5.5"
                />
                <button type="button" className="btn-small" onClick={sellAll}>
                  Vendi tutto
                </button>
              </div>
              
              {sellQuantity && parseFloat(sellQuantity) > 0 && (
                <p className="quote-preview">
                  Riceverai circa <strong>{formatCurrency(parseFloat(sellQuantity) * parseFloat(selectedHolding.product.current_price))}</strong>
                </p>
              )}
              
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={closeSellModal}>
                  Annulla
                </button>
                <button type="submit" className="btn-primary" disabled={isSelling}>
                  {isSelling ? 'Vendita...' : 'Conferma Vendita'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
