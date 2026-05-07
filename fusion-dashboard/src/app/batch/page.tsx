'use client';

import { useState } from 'react';
import { Loader2, FolderOpen, AlertCircle, CheckCircle2 } from 'lucide-react';
import { API_BASE } from '@/lib/api';

type BatchResult = {
  status?: string;
  message?: string;
  total_files?: number;
  processed_files?: number;
  skipped_files?: number;
  errors?: string[];
  objects?: Record<
    string,
    {
      files: number;
      errors: number;
    }
  >;
};

export default function BatchPage() {
  const [folder, setFolder] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<BatchResult | null>(null);

  const isValidFolder = (value: string) => {
    const trimmed = value.trim();
    if (!trimmed) return false;

    return (
      /^[a-zA-Z]:[\\/]/.test(trimmed) ||
      /^\\\\/.test(trimmed) ||
      /^\//.test(trimmed) ||
      /^\.\.?[\\/]/.test(trimmed) ||
      /[\\/]/.test(trimmed)
    );
  };

  const runBatch = async () => {
    if (!isValidFolder(folder)) {
      setError('Please enter a valid folder path.');
      setResult(null);
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch(`${API_BASE}/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          folder,
        }),
      });

      let data: BatchResult = {};

      try {
        data = await res.json();
      } catch {
        data = {};
      }

      if (!res.ok) {
        throw new Error(
          data.message ||
            `Batch request failed with status ${res.status}`
        );
      }

      setResult(data);
    } catch (err: any) {
      setError(
        err?.message || 'Failed to execute batch process.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex-1 overflow-y-auto p-8 bg-gray-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Folder Validation Sample
        </h1>

        <p className="text-lg text-gray-600">
          Scan a folder and process migration files in batch
        </p>
      </div>

      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center">
              <FolderOpen className="w-6 h-6 text-blue-600" />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Batch Folder Scan
              </h2>

              <p className="text-gray-600">
                Enter the folder path containing migration files
              </p>
            </div>
          </div>

          <input
            type="text"
            placeholder="C:\\Personal\\data"
            value={folder}
            onChange={(e) => {
              setFolder(e.target.value);
              if (error) setError('');
            }}
            className="block w-full border border-gray-300 rounded-lg px-4 py-3 mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          {folder && !isValidFolder(folder) && (
            <p className="text-sm text-yellow-700 mb-4">
              Enter a folder path like <span className="font-medium">C:\\data</span>, <span className="font-medium">\\\\server\\share</span>, <span className="font-medium">/home/data</span>, or <span className="font-medium">folder/subfolder</span>.
            </p>
          )}

          <button
            onClick={runBatch}
            disabled={loading || !isValidFolder(folder)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center transition-colors"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Running Batch...
              </>
            ) : (
              'Run Batch'
            )}
          </button>
        </div>

        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="w-5 h-5 text-red-600" />

              <h3 className="text-red-800 font-semibold">
                Error
              </h3>
            </div>

            <p className="text-red-700">{error}</p>
          </div>
        )}

        {result && (
          <div className="mt-6">
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle2 className="w-5 h-5 text-green-600" />

                <h3 className="text-xl font-semibold text-gray-900">
                  Batch Results
                </h3>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <div className="text-sm text-blue-700 font-medium">
                    Total Files
                  </div>

                  <div className="text-2xl font-bold text-blue-900">
                    {result.total_files || 0}
                  </div>
                </div>

                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <div className="text-sm text-green-700 font-medium">
                    Processed
                  </div>

                  <div className="text-2xl font-bold text-green-900">
                    {result.processed_files || 0}
                  </div>
                </div>

                <div className="bg-yellow-50 p-4 rounded-lg text-center">
                  <div className="text-sm text-yellow-700 font-medium">
                    Skipped
                  </div>

                  <div className="text-2xl font-bold text-yellow-900">
                    {result.skipped_files || 0}
                  </div>
                </div>

                <div className="bg-red-50 p-4 rounded-lg text-center">
                  <div className="text-sm text-red-700 font-medium">
                    Errors
                  </div>

                  <div className="text-2xl font-bold text-red-900">
                    {result.errors?.length || 0}
                  </div>
                </div>
              </div>

              {result.message && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-800 mb-2">
                    Message
                  </h4>

                  <p className="text-gray-700">
                    {result.message}
                  </p>
                </div>
              )}

              {result.objects &&
                Object.keys(result.objects).length > 0 && (
                  <div className="mb-6">
                    <h4 className="font-semibold text-gray-800 mb-3">
                      Object Summary
                    </h4>

                    <div className="overflow-x-auto">
                      <table className="min-w-full border border-gray-200 rounded-lg">
                        <thead className="bg-gray-100">
                          <tr>
                            <th className="text-left px-4 py-3 border-b">
                              Object
                            </th>

                            <th className="text-left px-4 py-3 border-b">
                              Files
                            </th>

                            <th className="text-left px-4 py-3 border-b">
                              Errors
                            </th>
                          </tr>
                        </thead>

                        <tbody>
                          {Object.entries(result.objects).map(
                            ([name, stats]) => (
                              <tr
                                key={name}
                                className="border-b"
                              >
                                <td className="px-4 py-3">
                                  {name}
                                </td>

                                <td className="px-4 py-3">
                                  {stats.files}
                                </td>

                                <td className="px-4 py-3">
                                  {stats.errors}
                                </td>
                              </tr>
                            )
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

              {result.errors &&
                result.errors.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-red-800 mb-3">
                      Validation Errors
                    </h4>

                    <ul className="bg-red-50 border border-red-200 rounded-lg p-4 space-y-2 max-h-64 overflow-y-auto">
                      {result.errors.map((err, index) => (
                        <li
                          key={index}
                          className="text-red-700 list-disc ml-4"
                        >
                          {err}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}