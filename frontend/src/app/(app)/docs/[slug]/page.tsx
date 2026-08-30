/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars, react/no-unescaped-entities, @typescript-eslint/no-unused-expressions */
import fs from 'fs';
import path from 'path';
import { marked } from 'marked';
import Link from 'next/link';

export default async function DocSlugPage({ params }: { params: { slug: string } }) {
  const { slug } = await Promise.resolve(params);
  
  let content = '';
  let html = '';
  try {
    const docsDir = path.join(process.cwd(), 'docs-content');
    const filePath = path.join(docsDir, `${slug}.md`);
    if (fs.existsSync(filePath)) {
      content = fs.readFileSync(filePath, 'utf-8');
      html = await marked.parse(content);
    } else {
      content = '# Not Found\n\nDocumentation page not found.';
      html = await marked.parse(content);
    }
  } catch (err) {
    console.error(err);
    html = '<h1>Error</h1><p>Failed to load documentation.</p>';
  }

  return (
    <div style={{ lineHeight: '1.6' }}>
      <div 
        className="markdown-body" 
        dangerouslySetInnerHTML={{ __html: html }} 
        style={{ 
          fontSize: '1rem',
          color: 'var(--foreground)'
        }}
      />
      
      <div style={{ marginTop: '48px', paddingTop: '24px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between' }}>
        <Link href="/docs" style={{ color: 'var(--primary)', textDecoration: 'none' }}>
          &larr; Back to Docs Home
        </Link>
      </div>
    </div>
  );
}
