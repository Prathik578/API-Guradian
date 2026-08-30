/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import { apiClient, fetchApi } from '@/api/client';
import AddIntegrationForm from './AddIntegrationForm';
import IntegrationCard from './IntegrationCard';

export default async function IntegrationsPage() {
  let integrationsData;
  try {
    integrationsData = await fetchApi(apiClient.GET('/api/v1/integrations/', {
      params: { query: { page: 1, size: 50 } }
    }));
  } catch (err) {
    console.error(err);
    integrationsData = { items: [], total: 0, page: 1, size: 50 };
  }

  return (
    <>
      <div className="flex-between page-header">
        <div>
          <h1 className="page-title">Integrations</h1>
          <p className="page-subtitle">Manage connected API providers, GitHub, and other external services.</p>
        </div>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '24px' }}>
        {integrationsData.items.map((integration: any) => (
          <IntegrationCard key={integration.id} integration={integration} />
        ))}
        
        <AddIntegrationForm />
      </div>
    </>
  );
}
