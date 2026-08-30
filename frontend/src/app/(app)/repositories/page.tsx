/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import { apiClient, fetchApi } from '@/api/client';
import AddRepositoryForm from './AddRepositoryForm';
import Link from 'next/link';

export default async function RepositoriesPage() {
  let reposData;
  try {
    reposData = await fetchApi(apiClient.GET('/api/v1/repositories/', {
      params: { query: { page: 1, size: 50 } }
    }));
  } catch (err) {
    console.error(err);
    reposData = { items: [], total: 0, page: 1, size: 50 };
  }

  return (
    <>
      <div className="flex-between page-header">
        <div>
          <h1 className="page-title">Repositories</h1>
          <p className="page-subtitle">Track and analyze your connected codebases.</p>
        </div>
        <AddRepositoryForm />
      </div>
      
      {reposData.items.length > 0 ? (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>GitHub Path</th>
                <th>Default Branch</th>
                <th>Connected At</th>
              </tr>
            </thead>
            <tbody>
              {reposData.items.map((repo: any) => (
                <tr key={repo.id}>
                  <td style={{ fontWeight: 500 }}>
                    <Link href={`/repositories/${repo.id}`}>{repo.name}</Link>
                  </td>
                  <td className="text-mono">{repo.github_full_name}</td>
                  <td><span className="badge default">{repo.default_branch}</span></td>
                  <td style={{ color: 'var(--text-muted)' }}>{repo.created_at ? new Date(repo.created_at).toLocaleString() : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <svg className="empty-state-icon" viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
          </svg>
          <h2 className="empty-state-title">No repositories connected</h2>
          <p className="empty-state-description">
            Add a GitHub repository to begin tracking dependencies and automated maintenance.
          </p>
        </div>
      )}
    </>
  );
}
