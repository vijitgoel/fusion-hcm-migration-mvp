// app/batch/object-errors/page.tsx
'use client';

import { useEffect, useMemo, useState, type ReactNode } from 'react';
import Link from 'next/link';
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  ChevronDown,
  Database,
  FileText,
  Layers3,
  ShieldAlert,
  ShieldCheck,
  TriangleAlert,
} from 'lucide-react';

type BatchFileSummary = {
  file_name: string;
  total_rows: number;
  valid_rows: number;
  error_rows: number;
  status: 'success' | 'partial' | 'error';
  validation_errors: { row: number | null; column: string; message: string }[];
  generation_error: string | null;
  detailed_errors: { row: number | null; column: string; message: string }[];
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

type ObjectDetailsPayload = {
  objectName: string;
  stats: BatchObjectStats;
  files: BatchFileSummary[];
  savedAt?: string;
};

const STORAGE_KEY = 'fusion_batch_object_details';

function getStatusColor(status?: string) {
  return status === 'success' ? 'green' : status === 'partial' ? 'amber' : status === 'error' ? 'red' : 'gray';
}

function getStatusIcon(status?: string) {
  switch (status) {
    case 'success':
      return <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />;
    case 'partial':
      return <AlertCircle className="h-3.5 w-3.5 text-amber-600" />;
    case 'error':
      return <AlertCircle className="h-3.5 w-3.5 text-red-600" />;
    default:
      return null;
  }
}

function StatusBadge({ status }: { status?: string }) {
  const tone = getStatusColor(status);

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${
        tone === 'green'
          ? 'bg-green-100 text-green-800'
          : tone === 'amber'
            ? 'bg-amber-100 text-amber-800'
            : tone === 'red'
              ? 'bg-red-100 text-red-800'
              : 'bg-gray-100 text-gray-800'
      }`}
    >
      {getStatusIcon(status)}
      {(status ?? 'unknown').charAt(0).toUpperCase() + (status ?? 'unknown').slice(1)}
    </span>
  );
}

function CompactCard({
  title,
  value,
  icon,
  tone,
}: {
  title: string;
  value: number | string;
  icon: ReactNode;
  tone: 'blue' | 'green' | 'amber' | 'red' | 'violet' | 'slate';
}) {
  const styles = {
    blue: 'border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 text-blue-700',
    green: 'border-green-200 bg-gradient-to-br from-green-50 to-green-100 text-green-700',
    amber: 'border-amber-200 bg-gradient-to-br from-amber-50 to-amber-100 text-amber-700',
    red: 'border-red-200 bg-gradient-to-br from-red-50 to-red-100 text-red-700',
    violet: 'border-violet-200 bg-gradient-to-br from-violet-50 to-violet-100 text-violet-700',
    slate: 'border-slate-200 bg-gradient-to-br from-slate-50 to-slate-100 text-slate-700',
  } as const;

  return (
    <div className={`h-20 rounded-xl border p-2.5 shadow-sm ${styles[tone]}`}>
      <div className="flex h-full flex-col justify-between">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <div className="truncate text-[10px] font-semibold uppercase tracking-wider text-gray-600">
              {title}
            </div>
          </div>
          <div className="rounded-lg bg-white/70 p-1.5 shadow-sm">{icon}</div>
        </div>
        <div className="text-lg font-bold leading-none tracking-tight text-gray-900">{value}</div>
      </div>
    </div>
  );
}

export default function ObjectErrorsPage() {
  const [payload, setPayload] = useState<ObjectDetailsPayload | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setPayload(JSON.parse(raw) as ObjectDetailsPayload);
    } catch {
      setPayload(null);
    }
  }, []);

  const files = payload?.files ?? [];
  const stats = payload?.stats;

  const totals = useMemo(
    () => ({
      totalRows: stats?.total_rows ?? 0,
      validRows: stats?.valid_rows ?? 0,
      errorRows: stats?.error_rows ?? 0,
      validationErrors: stats?.validation_error_count ?? 0,
      generationErrors: stats?.generation_error_count ?? 0,
    }),
    [stats]
  );

  const cleanPct = totals.totalRows ? Math.round((totals.validRows / totals.totalRows) * 100) : 0;
  const errorPct = totals.totalRows ? Math.round((totals.errorRows / totals.totalRows) * 100) : 0;

  const hdlLoadRecommended = cleanPct > 90 ? 'Yes' : 'No';
  const hdlGenerated = totals.generationErrors === 0 ? 'Yes' : 'No';

  const riskLevel =
    totals.generationErrors > 0 || errorPct >= 20
      ? 'High'
      : totals.validationErrors > 0 || errorPct >= 5
        ? 'Medium'
        : 'Low';

  const cleanTone: 'blue' | 'green' | 'amber' | 'red' | 'violet' | 'slate' =
    cleanPct >= 95 ? 'green' : cleanPct >= 80 ? 'blue' : 'amber';

  const errorPctTone: 'blue' | 'green' | 'amber' | 'red' | 'violet' | 'slate' =
    errorPct === 0 ? 'green' : errorPct <= 5 ? 'amber' : 'red';

  const hdlLoadTone: 'blue' | 'green' | 'amber' | 'red' | 'violet' | 'slate' =
    hdlLoadRecommended === 'Yes' ? 'green' : 'amber';

  const hdlGeneratedTone: 'blue' | 'green' | 'amber' | 'red' | 'violet' | 'slate' =
    hdlGenerated === 'Yes' ? 'violet' : 'red';

  const riskTone: 'blue' | 'green' | 'amber' | 'red' | 'violet' | 'slate' =
    riskLevel === 'Low' ? 'green' : riskLevel === 'Medium' ? 'amber' : 'red';

  return (
    <main className="flex-1 overflow-y-auto bg-slate-50 p-3 pb-8 md:p-4">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-4">
        <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm md:p-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex items-start gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                <Layers3 className="h-5 w-5" />
              </div>

              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="text-2xl font-bold tracking-tight text-gray-900">Validation Details</h1>

                  {payload?.objectName && (
                    <span className="rounded-full bg-violet-100 px-3 py-1 text-xs font-semibold text-violet-700">
                      {payload.objectName}
                    </span>
                  )}
                </div>

                <p className="mt-1 text-sm text-gray-600">
                  Compact object-level view with validation and generation breakdown.
                </p>
              </div>
            </div>

            <Link
              href="/batch"
              className="inline-flex items-center gap-2 rounded-xl border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Link>
          </div>
        </div>

        {!payload ? (
          <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-start gap-3 rounded-xl border border-gray-200 bg-gray-50 p-4 text-sm text-gray-600">
              <AlertCircle className="mt-0.5 h-4 w-4 text-gray-500" />
              <div>No object details were found, or the details are not available in this browser session.</div>
            </div>
          </section>
        ) : (
          <>
            <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm md:p-5">
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 xl:grid-cols-4">
                <CompactCard
                  title="Rows"
                  value={totals.totalRows}
                  tone="slate"
                  icon={<Database className="h-3.5 w-3.5" />}
                />
                <CompactCard
                  title="Valid"
                  value={totals.validRows}
                  tone="green"
                  icon={<CheckCircle2 className="h-3.5 w-3.5" />}
                />
                <CompactCard
                  title="Errors"
                  value={totals.errorRows}
                  tone="red"
                  icon={<TriangleAlert className="h-3.5 w-3.5" />}
                />
                <CompactCard
                  title="Clean %"
                  value={`${cleanPct}%`}
                  tone={cleanTone}
                  icon={<ShieldCheck className="h-3.5 w-3.5" />}
                />
                <CompactCard
                  title="Error %"
                  value={`${errorPct}%`}
                  tone={errorPctTone}
                  icon={<ShieldAlert className="h-3.5 w-3.5" />}
                />
                <CompactCard
                  title="HDL Load Recommended"
                  value={hdlLoadRecommended}
                  tone={hdlLoadTone}
                  icon={<CheckCircle2 className="h-3.5 w-3.5" />}
                />
                <CompactCard
                  title="HDL Generated"
                  value={hdlGenerated}
                  tone={hdlGeneratedTone}
                  icon={<FileText className="h-3.5 w-3.5" />}
                />
                <CompactCard
                  title="Risk Level"
                  value={riskLevel}
                  tone={riskTone}
                  icon={<AlertCircle className="h-3.5 w-3.5" />}
                />
              </div>
            </section>

            <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm md:p-5">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-amber-50 text-amber-600">
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">File details</h3>
                  <p className="text-sm text-gray-600">Click the file row to expand detailed validation data.</p>
                </div>
              </div>

              {files.length === 0 ? (
                <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 text-sm text-gray-600">
                  No file-level details were found for this object.
                </div>
              ) : (
                <div className="space-y-3">
                  {files.map((fileSummary, index) => {
                    const validationErrors = fileSummary.validation_errors ?? [];
                    const otherDetailedErrors = (fileSummary.detailed_errors ?? []).filter(
                      (err) =>
                        !validationErrors.some(
                          (ve) =>
                            ve.row === err.row &&
                            ve.column === err.column &&
                            ve.message === err.message
                        )
                    );

                    return (
                      <details
                        key={`${fileSummary.file_name}-${index}`}
                        className="group rounded-2xl border border-gray-200 bg-white p-4 shadow-sm transition hover:shadow-md"
                      >
                        <summary className="list-none cursor-pointer">
                          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                            <div className="min-w-0">
                              <div className="flex items-center gap-2">
                                <h4 className="truncate text-base font-semibold text-gray-900">
                                  {fileSummary.file_name}
                                </h4>
                                <span className="rounded-full bg-blue-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-blue-700">
                                  Click to expand
                                </span>
                              </div>
                              <p className="text-xs text-gray-500">Detailed error breakdown</p>
                            </div>

                            <div className="flex items-center gap-3">
                              <div className="hidden text-sm text-gray-600 md:block">
                                {fileSummary.total_rows} rows
                              </div>
                              <StatusBadge status={fileSummary.status} />
                              <ChevronDown className="h-4 w-4 text-gray-400 transition-transform duration-200 group-open:rotate-180" />
                            </div>
                          </div>
                        </summary>

                        <div className="mt-4 grid grid-cols-2 gap-2 text-sm md:grid-cols-4">
                          <div className="rounded-xl bg-gray-50 p-3">
                            <div className="text-[11px] font-semibold uppercase tracking-wide text-gray-500">
                              Total rows
                            </div>
                            <div className="mt-1 text-base font-bold text-gray-900">{fileSummary.total_rows}</div>
                          </div>

                          <div className="rounded-xl bg-gray-50 p-3">
                            <div className="text-[11px] font-semibold uppercase tracking-wide text-gray-500">
                              Valid
                            </div>
                            <div className="mt-1 text-base font-bold text-green-700">
                              {fileSummary.valid_rows}
                            </div>
                          </div>

                          <div className="rounded-xl bg-gray-50 p-3">
                            <div className="text-[11px] font-semibold uppercase tracking-wide text-gray-500">
                              Errors
                            </div>
                            <div className="mt-1 text-base font-bold text-red-700">
                              {fileSummary.error_rows}
                            </div>
                          </div>

                          <div className="rounded-xl bg-gray-50 p-3">
                            <div className="text-[11px] font-semibold uppercase tracking-wide text-gray-500">
                              Generation
                            </div>
                            <div className="mt-1 text-base font-bold text-gray-900">
                              {fileSummary.generation_error ? 'Failed' : 'OK'}
                            </div>
                          </div>
                        </div>

                        {fileSummary.generation_error && (
                          <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3">
                            <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-amber-800">
                              <AlertCircle className="h-4 w-4" />
                              Generation Error
                            </div>
                            <p className="text-sm text-amber-700">{fileSummary.generation_error}</p>
                          </div>
                        )}

                        {validationErrors.length > 0 && (
                          <div className="mt-3">
                            <h5 className="mb-2 text-xs font-semibold uppercase tracking-wider text-red-800">
                              Validation Errors
                            </h5>
                            <div className="overflow-x-auto rounded-xl border border-red-200">
                              <table className="min-w-full divide-y divide-red-200">
                                <thead className="bg-red-50">
                                  <tr>
                                    <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wide text-red-700">
                                      Row
                                    </th>
                                    <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wide text-red-700">
                                      Column
                                    </th>
                                    <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wide text-red-700">
                                      Message
                                    </th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-red-100 bg-white">
                                  {validationErrors.map((err, errIndex) => (
                                    <tr key={`${fileSummary.file_name}-validation-${errIndex}`}>
                                      <td className="px-3 py-2 text-xs text-red-900">{err.row ?? 'N/A'}</td>
                                      <td className="px-3 py-2 font-mono text-xs text-red-700">{err.column}</td>
                                      <td className="px-3 py-2 text-xs text-red-700">{err.message}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}

                        {otherDetailedErrors.length > 0 && (
                          <div className="mt-3">
                            <h5 className="mb-2 text-xs font-semibold uppercase tracking-wider text-red-800">
                              Other detailed errors
                            </h5>
                            <div className="overflow-x-auto rounded-xl border border-red-200">
                              <table className="min-w-full divide-y divide-red-200">
                                <thead className="bg-red-50">
                                  <tr>
                                    <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wide text-red-700">
                                      Row
                                    </th>
                                    <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wide text-red-700">
                                      Column
                                    </th>
                                    <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wide text-red-700">
                                      Message
                                    </th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-red-100 bg-white">
                                  {otherDetailedErrors.map((err, errIndex) => (
                                    <tr key={`${fileSummary.file_name}-other-${errIndex}`}>
                                      <td className="px-3 py-2 text-xs text-red-900">{err.row ?? 'N/A'}</td>
                                      <td className="px-3 py-2 font-mono text-xs text-red-700">{err.column}</td>
                                      <td className="px-3 py-2 text-xs text-red-700">{err.message}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}

                        {validationErrors.length === 0 &&
                          otherDetailedErrors.length === 0 &&
                          !fileSummary.generation_error && (
                            <div className="mt-3 rounded-xl border border-green-200 bg-green-50 p-3 text-sm text-green-700">
                              No detailed errors found.
                            </div>
                          )}
                      </details>
                    );
                  })}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  );
}