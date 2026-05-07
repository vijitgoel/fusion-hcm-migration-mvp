'use client';

import { useState } from 'react';
import { API_BASE } from '@/lib/api';

export default function BatchPage() {
  const [folder, setFolder] = useState('');
  const [result, setResult] = useState<any>(null);

  const runBatch = async () => {
    const formData = new FormData();
    formData.append('folder', folder);

    const res = await fetch(`${API_BASE}/batch`, {
      method: 'POST',
      body: formData,
    });

    const data = await res.json();
    setResult(data);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Folder Validation</h1>

      <input
        type="text"
        placeholder="Enter folder path"
        value={folder}
        onChange={(e) => setFolder(e.target.value)}
        className="border p-2 w-full mb-4"
      />

      <button onClick={runBatch} className="bg-blue-600 text-white px-4 py-2">
        Run Batch
      </button>

      {result && (
        <pre className="mt-4 bg-gray-100 p-4">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}