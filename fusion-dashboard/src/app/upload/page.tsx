'use client';

import { useState } from 'react';
import { Upload, Loader2, Download } from 'lucide-react';
import PreviewTable from '@/components/PreviewTable';
import { API_BASE } from '@/lib/api';

type ApiStats = {
  total: number;
  valid: number;
  errors: number;
};

type ApiResponse = {
  status: 'success' | 'validation_error' | 'error';
  message: string;
  errors?: string[];
  preview?: Record<string, any>[];
  hdl?: string;
  stats?: ApiStats;
};

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedFile = e.target.files?.[0] || null;

    setFile(selectedFile);
    setResponse(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      let data: ApiResponse | null = null;

      try {
        data = await res.json();
      } catch {
        data = null;
      }

      // Handle validation errors gracefully
      if (data?.status === 'validation_error') {
        setResponse(data);
        return;
      }

      // Handle other non-OK responses
      if (!res.ok) {
        const message =
          data?.message ||
          (typeof (data as any)?.detail === 'string'
            ? (data as any).detail
            : `Upload failed with status ${res.status}`);

        throw new Error(message);
      }

      setResponse(data);
    } catch (err: any) {
      setError(
        err?.message ||
          'Failed to upload file. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (
      !response ||
      response.status !== 'success' ||
      !response.hdl
    ) {
      return;
    }

    const blob = new Blob([response.hdl], {
      type: 'text/csv',
    });

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'worker.hdl.csv';
    a.click();

    window.URL.revokeObjectURL(url);
  };

  // FIXED PARAMETER ORDER
  const renderStats = (
    statusColor: 'yellow' | 'green',
    stats?: ApiStats
  ) => {
    if (!stats) return null;

    const totalCardClass =
      statusColor === 'yellow'
        ? 'bg-yellow-100'
        : 'bg-green-100';

    const totalTextClass =
      statusColor === 'yellow'
        ? 'text-yellow-900'
        : 'text-green-900';

    return (
      <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
        <div
          className={`${totalCardClass} p-3 rounded-lg text-center`}
        >
          <div
            className={`font-semibold ${totalTextClass}`}
          >
            Total Rows
          </div>

          <div className={`text-lg ${totalTextClass}`}>
            {stats.total}
          </div>
        </div>

        <div className="bg-green-100 p-3 rounded-lg text-center">
          <div className="font-semibold text-green-900">
            Valid Rows
          </div>

          <div className="text-lg text-green-900">
            {stats.valid}
          </div>
        </div>

        <div className="bg-red-100 p-3 rounded-lg text-center">
          <div className="font-semibold text-red-900">
            Errors
          </div>

          <div className="text-lg text-red-900">
            {stats.errors}
          </div>
        </div>
      </div>
    );
  };

  return (
    <main className="flex-1 overflow-y-auto p-8 bg-gray-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Upload Data
        </h1>

        <p className="text-lg text-gray-600">
          Upload your employee data file for validation and HDL
          generation
        </p>
      </div>

      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center">
              <Upload className="w-6 h-6 text-blue-600" />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Upload Excel or CSV
              </h2>

              <p className="text-gray-600">
                Required columns: EmployeeNumber,
                FirstName, LastName, HireDate
              </p>
            </div>
          </div>

          <input
            type="file"
            accept=".xlsx,.csv"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-600 
              file:mr-4 file:py-2 file:px-4 
              file:rounded-full file:border-0 
              file:text-sm file:font-semibold 
              file:bg-blue-50 file:text-blue-700 
              hover:file:bg-blue-100 mb-4"
          />

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg 
              hover:bg-blue-700 disabled:opacity-50 
              disabled:cursor-not-allowed flex items-center 
              justify-center transition-colors"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              'Convert to HDL'
            )}
          </button>
        </div>

        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="text-red-800 font-medium mb-2">
              Error
            </h3>

            <p className="text-red-700">{error}</p>
          </div>
        )}

        {response && (
          <>
            {response.status === 'error' && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <h3 className="text-red-800 font-medium mb-2">
                  Error
                </h3>

                <p className="text-red-700">
                  {response.message}
                </p>

                {response.errors &&
                  response.errors.length > 0 && (
                    <ul className="mt-3 list-disc ml-5 text-red-700 space-y-1">
                      {response.errors.map(
                        (item, idx) => (
                          <li key={idx}>{item}</li>
                        )
                      )}
                    </ul>
                  )}
              </div>
            )}

            {response.status ===
              'validation_error' && (
              <div className="mt-6">
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg mb-4">
                  <h3 className="text-yellow-800 font-medium mb-2">
                    Validation Errors
                  </h3>

                  <p className="text-yellow-700 mb-4">
                    {response.message}
                  </p>

                  {renderStats(
                    'yellow',
                    response.stats
                  )}

                {response.errors &&
                  response.errors.length > 0 && (
                    <div className="mt-4">
                      {typeof response.errors[0] === 'string' ? (
                        <ul className="text-yellow-800 space-y-2 max-h-48 overflow-y-auto">
                          {response.errors.map(
                            (err, index) => (
                              <li
                                key={index}
                                className="list-disc ml-4"
                              >
                                {err}
                              </li>
                            )
                          )}
                        </ul>
                      ) : (
                        <div className="overflow-x-auto">
                          <table className="min-w-full divide-y divide-yellow-200">
                            <thead className="bg-yellow-100">
                              <tr>
                                <th className="px-4 py-2 text-left text-xs font-semibold text-yellow-700">Row</th>
                                <th className="px-4 py-2 text-left text-xs font-semibold text-yellow-700">Column</th>
                                <th className="px-4 py-2 text-left text-xs font-semibold text-yellow-700">Message</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-yellow-200">
                              {(response.errors as Array<{row: number | null; column: string; message: string}>).map((err, index) => (
                                <tr key={index}>
                                  <td className="px-4 py-2 text-xs text-yellow-900">{err.row ?? 'N/A'}</td>
                                  <td className="px-4 py-2 text-xs font-mono text-yellow-700">{err.column}</td>
                                  <td className="px-4 py-2 text-xs text-yellow-700">{err.message}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <PreviewTable
                  data={response.preview || []}
                />
              </div>
            )}

            {response.status === 'success' && (
              <div className="mt-6">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg mb-4">
                  <h3 className="text-green-800 font-medium mb-2">
                    Success
                  </h3>

                  <p className="text-green-700">
                    {response.message}
                  </p>

                  {renderStats(
                    'green',
                    response.stats
                  )}
                </div>

                <PreviewTable
                  data={response.preview || []}
                />

                <button
                  onClick={handleDownload}
                  className="mt-4 bg-green-600 text-white py-3 px-6 rounded-lg 
                    hover:bg-green-700 flex items-center gap-2 
                    mx-auto transition-colors"
                >
                  <Download className="w-5 h-5" />
                  Download HDL CSV
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}