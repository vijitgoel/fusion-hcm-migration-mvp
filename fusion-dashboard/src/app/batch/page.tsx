'use client';

import { useCallback, useMemo, useState } from 'react';
import { AlertCircle, CheckCircle2, FolderOpen, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { API_BASE } from '@/lib/api';

type BatchFileSummary = {
  file_name: string;
  total_rows: number;
  valid_rows: number;
  error_rows: number;
  status: 'success' | 'partial' | 'error';
  validation_errors: Array<{
    row: number | null;
    column: string;
    message: string;
  }>;
  generation_error: string | null;
  detailed_errors: Array<{
    row: number | null;
    column: string;
    message: string;
  }>;
  file?: string; // legacy
};

type BatchObjectStats = {
  files: number;
  processed: number;
  errors: number;
  total_rows?: number;
  valid_rows?: number;
  error_rows?: number;
  status?: 'success' | 'partial' | 'error';
  validation_error_count?: number;
  generation_error_count?: number;
};

type BatchResult = {
  status?: 'success' | 'warning' | 'error' | string;
  message?: string;
  total_files?: number;
  processed_files?: number;
  skipped_files?: number;
  errors?: string[];
  objects?: Record<string, BatchObjectStats>;
  objects_errors?: Record<string, Array<BatchFileSummary>>;
};


function getErrorMessage(error: unknown, fallback: string) {
  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }

  return fallback;
}

async function readResponseJson(response: Response): Promise<BatchResult> {
  try {
    return (await response.json()) as BatchResult;
  } catch {
    return {};
  }
}

function StatCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: 'blue' | 'green' | 'yellow' | 'red';
}) {
  const styles: Record<typeof tone, string> = {
    blue: 'bg-blue-50 text-blue-700 border-blue-100',
    green: 'bg-green-50 text-green-700 border-green-100',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-100',
    red: 'bg-red-50 text-red-700 border-red-100',
  };

  const valueStyles: Record<typeof tone, string> = {
    blue: 'text-blue-900',
    green: 'text-green-900',
    yellow: 'text-yellow-900',
    red: 'text-red-900',
  };

  return (
    <div className={`rounded-xl border p-4 text-center ${styles[tone]}`}>
      <div className="text-sm font-medium">{label}</div>
      <div className={`mt-1 text-2xl font-bold ${valueStyles[tone]}`}>{value}</div>
    </div>
  );
}

export default function BatchPage() {
  const [folder, setFolder] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<BatchResult | null>(null);
  const [expandedObjects, setExpandedObjects] = useState<Set<string>>(new Set());

  const stats = useMemo(
    () => ({
      totalFiles: result?.total_files ?? 0,
      processedFiles: result?.processed_files ?? 0,
      skippedFiles: result?.skipped_files ?? 0,
      errorCount: result?.errors?.length ?? 0,
    }),
    [result]
  );

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'success': return 'green';
      case 'partial': return 'yellow';
      case 'error': return 'red';
      default: return 'gray';
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'success': return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'partial': return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'error': return <AlertCircle className="h-4 w-4 text-red-500" />;
      default: return null;
    }
  };

  const toggleExpanded = (objName: string) => {
    const newExpanded = new Set(expandedObjects);
    if (newExpanded.has(objName)) {
      newExpanded.delete(objName);
    } else {
      newExpanded.add(objName);
    }
    setExpandedObjects(newExpanded);
  };

  const isExpanded = (objName: string) => expandedObjects.has(objName);

  const runBatch = useCallback(async () => {
    const trimmedFolder = folder.trim();

    if (!trimmedFolder) {
      setError('Please enter a valid folder path.');
    setResult(null);
      return;
    }

    setLoading(true);
    setError('');
      setResult(null);

    try {
      const response = await fetch(`${API_BASE}/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ folder: trimmedFolder }),
      });

      const data = await readResponseJson(response);

      if (!response.ok) {
        throw new Error(
          data.message || `Batch request failed with status ${response.status}.`
        );
      }

      setResult(data);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to execute the batch process.'));
    } finally {
      setLoading(false);
    }
  }, [folder]);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      void runBatch();
    }
  };

  const hasObjectSummary = Boolean(result?.objects && Object.keys(result.objects).length > 0);
  const hasValidationErrors = Boolean(result?.errors && result.errors.length > 0);

  return (
    <main className="min-h-screen flex-1 overflow-y-auto bg-gray-50 p-6 md:p-8">
      <div className="mx-auto max-w-5xl">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Folder Validation
          </h1>
          <p className="mt-2 text-base text-gray-600">
            Scan a folder and process migration files in batch.
          </p>
        </header>

        <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm md:p-8">
          <div className="mb-6 flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-50">
              <FolderOpen className="h-6 w-6 text-blue-600" />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Batch Folder Scan
              </h2>
              <p className="text-sm text-gray-600">
                Enter the folder path containing migration files.
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <label htmlFor="folderPath" className="block text-sm font-medium text-gray-700">
              Folder path
            </label>

            <input
              id="folderPath"
              type="text"
              placeholder="C:\\Personal\\data"
              value={folder}
              onChange={(e) => setFolder(e.target.value)}
              onKeyDown={handleKeyDown}
              className="block w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
            />

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={() => void runBatch()}
                disabled={loading}
                className="inline-flex items-center rounded-lg bg-blue-600 px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Running batch...
                  </>
                ) : (
                  'Run batch'
                )}
              </button>
            </div>
          </div>
        </section>

        {error && (
          <section className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4">
            <div className="mb-2 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <h3 className="font-semibold text-red-800">Error</h3>
            </div>
            <p className="text-red-700">{error}</p>
          </section>
        )}

        {result && (
          <section className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm md:p-8">
            <div className="mb-6 flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <h3 className="text-xl font-semibold text-gray-900">Batch Results</h3>
            </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <StatCard label="Total files" value={stats.totalFiles} tone="blue" />
                <StatCard label="Processed" value={stats.processedFiles} tone="green" />
                <StatCard label="Skipped" value={stats.skippedFiles} tone="yellow" />
                <StatCard label="Errors" value={stats.errorCount} tone="red" />
              </div>

            {result.message && (
              <div className="mt-6 rounded-xl bg-gray-50 p-4">
                <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-700">
                  Message
                </h4>
                <p className="text-gray-700">{result.message}</p>
              </div>
            )}

              {hasObjectSummary && (
                <div className="mt-6">
                  <h4 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-700">
                    Object summary
                  </h4>

                  <div className="overflow-hidden rounded-xl border border-gray-200">
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                              Object
                            </th>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                              Files
                            </th>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                              Total Rows
                            </th>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                              Valid Rows
                            </th>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                              Error Rows
                            </th>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                              Status
                            </th>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                              Validation Errors
                            </th>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                              Generation Errors
                            </th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 bg-white">
                          {Object.entries(result.objects ?? {}).map(([name, stats]) => {
                            const hasErrors = stats.errors > 0;
                            const objErrors = result.objects_errors?.[name] || [];
                            const status = stats.status || 'unknown';
                            const statusTone = getStatusColor(status);
                            return (
                              <>
                                <tr key={name} className="hover:bg-gray-50">
                                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                                    {name}
                                  </td>
                                  <td className="px-4 py-3 text-sm text-gray-700">
                                    {stats.files}
                                  </td>
                                  <td className="px-4 py-3 text-sm text-gray-700">
                                    {stats.total_rows ?? 0}
                                  </td>
                                  <td className={`px-4 py-3 text-sm ${statusTone === 'green' ? 'text-green-600' : 'text-gray-700'}`}>
                                    {stats.valid_rows ?? 0}
                                  </td>
                                  <td className={`px-4 py-3 text-sm ${statusTone === 'red' ? 'text-red-600' : 'text-gray-700'}`}>
                                    {stats.error_rows ?? 0}
                                  </td>
                                  <td className="px-4 py-3 text-sm">
                                    <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${statusTone === 'green' ? 'bg-green-100 text-green-800' : statusTone === 'yellow' ? 'bg-yellow-100 text-yellow-800' : statusTone === 'red' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}>
                                      {getStatusIcon(status)}
                                      {status.charAt(0).toUpperCase() + status.slice(1)}
                                    </span>
                                  </td>
                                  <td className={`px-4 py-3 text-sm cursor-pointer select-none ${hasErrors ? 'text-red-600 hover:text-red-700' : 'text-gray-700'}`}>
                                    {stats.validation_error_count ?? stats.errors ?? 0} {hasErrors && (isExpanded(name) ? <ChevronUp className="inline ml-1 h-4 w-4" /> : <ChevronDown className="inline ml-1 h-4 w-4" />)}
                                  </td>
                                  <td className="px-4 py-3 text-sm text-gray-700">
                                    {stats.generation_error_count ?? 0}
                                  </td>
                                </tr>
                                {hasErrors && isExpanded(name) && (
                                  <tr>
                                    <td colSpan={8} className="p-0">
                                      <div className="border-t border-red-200 bg-red-50 p-4">
                                        <h5 className="mb-3 font-medium text-red-800">Detailed Summary for {name}</h5>
                                        {objErrors.length > 0 ? (
                                          <div className="space-y-4">
                                            {objErrors.map((fileSummary, fileIndex) => (
                                              <div key={fileIndex} className="border border-gray-200 rounded-lg p-3 bg-white">
                                                <div className="flex justify-between items-center mb-2">
                                                  <h6 className="font-semibold text-gray-900">{fileSummary.file_name}</h6>
                                                  <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(fileSummary.status) === 'green' ? 'bg-green-100 text-green-800' : getStatusColor(fileSummary.status) === 'yellow' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                                                    {getStatusIcon(fileSummary.status)}
                                                    {fileSummary.status.charAt(0).toUpperCase() + fileSummary.status.slice(1)}
                                                  </span>
                                                </div>
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
                                                  <div><span className="font-medium">Total Rows:</span> {fileSummary.total_rows}</div>
                                                  <div><span className="font-medium">Valid:</span> {fileSummary.valid_rows}</div>
                                                  <div className="text-red-600"><span className="font-medium">Errors:</span> {fileSummary.error_rows}</div>
                                                </div>
                                                {fileSummary.generation_error && (
                                                  <div className="mb-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
                                                    <h6 className="font-medium text-yellow-800">Generation Error:</h6>
                                                    <p className="text-sm text-yellow-700">{fileSummary.generation_error}</p>
                                                  </div>
                                                )}
                                                {fileSummary.validation_errors.length > 0 && (
                                                  <div className="mb-3">
                                                    <h6 className="font-medium text-red-800 mb-2">Validation Errors:</h6>
                                                    <div className="overflow-x-auto">
                                                      <table className="min-w-full divide-y divide-red-200">
                                                        <thead className="bg-red-100">
                                                          <tr>
                                                            <th className="px-4 py-2 text-left text-xs font-semibold text-red-700">Row</th>
                                                            <th className="px-4 py-2 text-left text-xs font-semibold text-red-700">Column</th>
                                                            <th className="px-4 py-2 text-left text-xs font-semibold text-red-700">Message</th>
                                                          </tr>
                                                        </thead>
                                                        <tbody className="bg-white divide-y divide-red-200">
                                                          {fileSummary.validation_errors.map((err, errIndex) => (
                                                            <tr key={errIndex}>
                                                              <td className="px-4 py-2 text-xs text-red-900">{err.row ?? 'N/A'}</td>
                                                              <td className="px-4 py-2 text-xs font-mono text-red-700">{err.column}</td>
                                                              <td className="px-4 py-2 text-xs text-red-700">{err.message}</td>
                                                            </tr>
                                                          ))}
                                                        </tbody>
                                                      </table>
                                                    </div>
                                                  </div>
                                                )}
                                                {fileSummary.detailed_errors.length > 0 && fileSummary.detailed_errors.length !== fileSummary.validation_errors.length && (
                                                  <div>
                                                    <h6 className="font-medium text-red-800 mb-2">Other Detailed Errors:</h6>
                                                    <div className="overflow-x-auto">
                                                      <table className="min-w-full divide-y divide-red-200">
                                                        <thead className="bg-red-100">
                                                          <tr>
                                                            <th className="px-4 py-2 text-left text-xs font-semibold text-red-700">Row</th>
                                                            <th className="px-4 py-2 text-left text-xs font-semibold text-red-700">Column</th>
                                                            <th className="px-4 py-2 text-left text-xs font-semibold text-red-700">Message</th>
                                                          </tr>
                                                        </thead>
                                                        <tbody className="bg-white divide-y divide-red-200">
                                                          {fileSummary.detailed_errors.filter(err => !fileSummary.validation_errors.some(ve => ve.row === err.row && ve.column === err.column && ve.message === err.message)).map((err, errIndex) => (
                                                            <tr key={errIndex}>
                                                              <td className="px-4 py-2 text-xs text-red-900">{err.row ?? 'N/A'}</td>
                                                              <td className="px-4 py-2 text-xs font-mono text-red-700">{err.column}</td>
                                                              <td className="px-4 py-2 text-xs text-red-700">{err.message}</td>
                                                            </tr>
                                                          ))}
                                                        </tbody>
                                                      </table>
                                                    </div>
                                                  </div>
                                                )}
                                              </div>
                                            ))}
                                          </div>
                                        ) : (
                                          <p className="text-sm text-red-700">No detailed errors found.</p>
                                        )}
                                      </div>
                                    </td>
                                  </tr>
                                )}
                              </>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* Legacy detailed errors removed as now integrated into table expansion */}

              {hasValidationErrors && (
                <div className="mt-6">
                  <h4 className="mb-3 text-sm font-semibold uppercase tracking-wide text-red-800">
                    Summary Validation Errors
                  </h4>

                  <ul className="max-h-64 space-y-2 overflow-y-auto rounded-xl border border-red-200 bg-red-50 p-4">
                    {result.errors?.map((message, index) => (
                      <li key={`${index}-${message}`} className="ml-4 list-disc text-sm text-red-700">
                        {message}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
          </section>
        )}
      </div>
    </main>
  );
}