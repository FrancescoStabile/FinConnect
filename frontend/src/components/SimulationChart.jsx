import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function SimulationChart({ data }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="year" 
            label={{ value: 'Anno', position: 'insideBottom', offset: -5 }} 
          />
          <YAxis 
            tickFormatter={formatCurrency}
            width={100}
          />
          <Tooltip 
            formatter={(value) => formatCurrency(value)}
            labelFormatter={(label) => `Anno ${label}`}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="total_invested" 
            stroke="#6b7280" 
            strokeWidth={2}
            name="Capitale Investito" 
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="projected_average_value" 
            stroke="#2563eb" 
            strokeWidth={2}
            name="Scenario Medio" 
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="projected_best_case" 
            stroke="#16a34a" 
            strokeWidth={2}
            strokeDasharray="5 5"
            name="Scenario Ottimista" 
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="projected_worst_case" 
            stroke="#dc2626" 
            strokeWidth={2}
            strokeDasharray="5 5"
            name="Scenario Pessimista" 
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
