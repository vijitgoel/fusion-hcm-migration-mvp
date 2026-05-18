'use client';

import { useCallback, useEffect, useMemo, useState, type KeyboardEvent } from 'react';
import { AlertCircle, CheckCircle2, ExternalLink, FolderOpen, Loader2 } from 'lucide-react';
import { API_BASE } from '@/lib/api';

type BatchFileSummary = {
  file_name: string;
  total_rows: number;
  valid_rows: number;
  error_rows: number;
  status: 'success' | 'partial' | 'error';
  validation_errors: { row: number | null; column: string; message: string }[];
  generation_error: string | null;
  detailed_errors: { row: number | null; column: string; message: string }[];
  file?: string;
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
  objects_errors?: Record<string, BatchFileSummary[]>;
};

const SUMMARY_STORAGE_KEY = 'fusion_batch_validation_summary';
const OBJECT_STORAGE_KEY = 'fusion_batch_object_details';

function getErrorMessage(error: unknown, fallback: string) {
  return error instanceof Error && error.message.trim() ? error.message : fallback;
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
  const styles = {
    blue: 'bg-blue-50 text-blue-700 border-blue-100',
    green: 'bg-green-50 text-green-700 border-green-100',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-100',
    red: 'bg-red-50 text-red-700 border-red-100',
  } as const;

  const valueStyles = {
    blue: 'text-blue-900',
    green: 'text-green-900',
    yellow: 'text-yellow-900',
    red: 'text-red-900',
  } as const;

  return (
    <div className={`rounded-xl border p-2 text-center ${styles[tone]}`}>
      <div className="text-sm font-medium">{label}</div>
      <div className={`mt-0.5 text-xl font-bold ${valueStyles[tone]}`}>{value}</div>
    </div>
  );
}

function getStatusColor(status?: string) {
  return status === 'success' ? 'green' : status === 'partial' ? 'yellow' : status === 'error' ? 'red' : 'gray';
}

function getStatusIcon(status?: string) {
  switch (status) {
    case 'success':
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case 'partial':
      return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    case 'error':
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    default:
      return null;
  }
}

export default function BatchPage() {
  const [folder, setFolder] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<BatchResult | null>(null);
  const [toastMessage, setToastMessage] = useState('');

  const stats = useMemo(
    () => ({
      totalFiles: result?.total_files ?? 0,
      processedFiles: result?.processed_files ?? 0,
      skippedFiles: result?.skipped_files ?? 0,
      errorCount: result?.errors?.length ?? 0,
    }),
    [result]
  );

  useEffect(() => {
    if (!toastMessage) return;

    const timer = window.setTimeout(() => {
      setToastMessage('');
    }, 3000);

    return () => window.clearTimeout(timer);
  }, [toastMessage]);

  const openDetailsPage = useCallback(
    (route: string, storageKey: string, payload: Record<string, unknown>) => {
      try {
        localStorage.setItem(
          storageKey,
          JSON.stringify({
            ...payload,
            savedAt: new Date().toISOString(),
          })
        );

        const win = window.open(route, '_blank');
        if (win) win.opener = null;
      } catch {
        setError('Unable to open the details page.');
      }
    },
    []
  );

  const openSummaryErrors = useCallback(() => {
    openDetailsPage('/batch/validation-errors', SUMMARY_STORAGE_KEY, {
      errors: result?.errors ?? [],
      total_files: stats.totalFiles,
      processed_files: stats.processedFiles,
      skipped_files: stats.skippedFiles,
      message: result?.message ?? '',
    });
  }, [openDetailsPage, result, stats]);

  const openObjectErrors = useCallback(
    (objectName: string, objectStats: BatchObjectStats, fileSummaries: BatchFileSummary[]) => {
      openDetailsPage('/batch/object-errors', OBJECT_STORAGE_KEY, {
        objectName,
        stats: objectStats,
        files: fileSummaries,
      });
    },
    [openDetailsPage]
  );

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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder: trimmedFolder }),
      });

      const data = await readResponseJson(response);

      if (!response.ok) {
        throw new Error(data.message || `Scan request failed with status ${response.status}.`);
      }

      setResult(data);

      if (data.message) {
        setToastMessage(data.message);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to execute the Scan process.'));
    } finally {
      setLoading(false);
    }
  }, [folder]);

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') void runBatch();
  };

  const hasObjectSummary = Boolean(result?.objects && Object.keys(result.objects).length > 0);
  const summaryErrorCount = result?.errors?.length ?? 0;

  return (
    <main className="flex-1 overflow-y-auto p-4 md:p-6">
      {toastMessage && (
        <div className="fixed right-4 top-4 z-50 w-full max-w-sm animate-in slide-in-from-top-2 duration-300">
          <div className="flex items-start gap-3 rounded-xl border border-green-200 bg-green-50 p-4 shadow-xl">
            <div className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-full bg-green-100">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            </div>
            <div className="min-w-0">
              <div className="text-sm font-semibold text-green-900">Scan Completed</div>
              <p className="mt-1 text-sm text-green-800">{toastMessage}</p>
            </div>
          </div>
        </div>
      )}

      <div className="mx-auto max-w-5xl"> 
        <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm md:p-6">
          <div className="mb-4 flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-50">
              <FolderOpen className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Fusion HCM Migration Diagnostics Suite</h2>
              
            </div>
          </div>

          <div className="space-y-3">
            <label htmlFor="folderPath" className="block text-sm font-medium text-gray-700">
              Folder path
            </label>

            <div className="flex items-end gap-3">
              <input
                id="folderPath"
                type="text"
                placeholder="C:\\Personal\\data"
                value={folder}
                onChange={(e) => setFolder(e.target.value)}
                onKeyDown={handleKeyDown}
                className="h-10 flex-1 rounded-lg border border-gray-300 px-4 py-2 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />
              <button
                type="button"
                onClick={() => void runBatch()}
                disabled={loading}
                className="inline-flex h-10 items-center rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Running Scan...
                  </>
                ) : (
                  'Run Scan'
                )}
              </button>
            </div>
          </div>
        </section>

        {error && (
          <section className="rounded-2xl border border-red-200 bg-red-50 p-3">
            <div className="mb-2 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <h3 className="font-semibold text-red-800">Error</h3>
            </div>
            <p className="text-red-700">{error}</p>
          </section>
        )}

        {result && (
          <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm md:p-6">
            <div className="mb-4 flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <h3 className="text-xl font-semibold text-gray-900">Scan Results</h3>
            </div>

            <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
              <StatCard label="Total files" value={stats.totalFiles} tone="blue" />
              <StatCard label="Processed" value={stats.processedFiles} tone="green" />
              <StatCard label="Skipped" value={stats.skippedFiles} tone="yellow" />
              <StatCard label="Errors" value={stats.errorCount} tone="red" />
            </div>

            <div className="mt-2 text-xs text-gray-600">Generated HDL files available in: fusion-app/output/</div>

            {summaryErrorCount > 0 && (
              <button
                type="button"
                onClick={openSummaryErrors}
                className="mt-4 inline-flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100"
              >
                Open validation summary ({summaryErrorCount})
                <ExternalLink className="h-4 w-4" />
              </button>
            )}

            {hasObjectSummary && (
              <div className="mt-4">
                <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-700">Object summary</h4>

                <div className="overflow-x-auto rounded-xl border border-gray-200">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Object</th>
                        <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Files</th>
                        <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Total Rows</th>
                        <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Valid Rows</th>
                        <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Error Rows</th>
                        <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Status</th>
                        <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Validation Errors</th>
                        <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700">Generation Errors</th>
                      </tr>
                    </thead>

                    <tbody className="divide-y divide-gray-200 bg-white">
                      {Object.entries(result.objects ?? {}).map(([name, obj]) => {
                        const objErrors = result.objects_errors?.[name] || [];
                        const status = obj.status || 'unknown';
                        const statusTone = getStatusColor(status);
                        const validationCount = obj.validation_error_count ?? obj.errors ?? 0;

                        return (
                          <tr key={name} className="hover:bg-gray-50">
                            <td className="px-4 py-2 text-sm font-medium text-gray-900">{name}</td>
                            <td className="px-4 py-2 text-sm text-gray-700">{obj.files}</td>
                            <td className="px-4 py-2 text-sm text-gray-700">{obj.total_rows ?? 0}</td>
                            <td className={`px-4 py-2 text-sm ${statusTone === 'green' ? 'text-green-600' : 'text-gray-700'}`}>
                              {obj.valid_rows ?? 0}
                            </td>
                            <td className={`px-4 py-2 text-sm ${statusTone === 'red' ? 'text-red-600' : 'text-gray-700'}`}>
                              {obj.error_rows ?? 0}
                            </td>
                            <td className="px-4 py-2 text-sm">
                              <span
                                className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium ${
                                  statusTone === 'green'
                                    ? 'bg-green-100 text-green-800'
                                    : statusTone === 'yellow'
                                      ? 'bg-yellow-100 text-yellow-800'
                                      : statusTone === 'red'
                                        ? 'bg-red-100 text-red-800'
                                        : 'bg-gray-100 text-gray-800'
                                }`}
                              >
                                {getStatusIcon(status)}
                                {status.charAt(0).toUpperCase() + status.slice(1)}
                              </span>
                            </td>
                            <td className="px-4 py-2 text-sm">
                              {validationCount > 0 ? (
                                <button
                                  type="button"
                                  onClick={() => openObjectErrors(name, obj, objErrors)}
                                  className="inline-flex items-center gap-1 text-red-600 hover:text-red-700"
                                >
                                  {validationCount}
                                  <ExternalLink className="h-4 w-4" />
                                </button>
                              ) : (
                                <span className="text-gray-700">0</span>
                              )}
                            </td>
                            <td className="px-4 py-2 text-sm text-gray-700">{obj.generation_error_count ?? 0}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  );
}